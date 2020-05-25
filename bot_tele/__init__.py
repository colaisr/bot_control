import configparser
import datetime
import threading

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot_calendar import set_event, update_schedule_for_date
from bot_db import update_stat


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Order:
    def __init__(self, name):
        self.name = name
        self.date = "None"
        self.hours = "None"
        self.minutes = "None"
        self.phone = "None"


class Bot:

    def __init__(self, key, update=False, start_time=8, end_time=20, interval=15, owner_id=0):
        self.bot = telebot.TeleBot(key)
        self.user_dict = {}
        self.START_TIME = start_time
        self.END_TIME = end_time
        self.SLOT_SIZE = interval
        self.UPDATE_CALENDAR = update
        self.OWNER_ID = owner_id
        self.is_running = False
        self.thread_native_id = 0
        self.thread = None

        # Handle '/iammaster command
        @self.bot.message_handler(commands=['iammaster'])
        def confirm_master(message):

            msg = self.bot.reply_to(message, """\
            אז אתה בעל הבית ?  yes/clear
            """)
            self.bot.register_next_step_handler(msg, process_master_set)

        # processing the belonging
        def process_master_set(message):
            try:
                chat_id = message.chat.id
                name = message.text
                user_id = message.chat.id

                if message.text.lower() == 'yes':
                    self.OWNER_ID = user_id
                    self.bot.reply_to(message, 'סבבה')
                else:
                    self.OWNER_ID = 0
                    self.bot.reply_to(message, 'ניקיתי')

            except Exception as e:
                self.bot.reply_to(message, 'oooops')

        # Handle Restart
        def restart_the_flow(call):
            chat_id = call.from_user.id
            msg = self.bot.send_message(chat_id, """\
            מייד נזמין לך תור ! מה שמך ?
            """)
            update_stat(Order("empty"), call.from_user, True)

            self.bot.register_next_step_handler(msg, process_name_step)

        # Handle '/start'
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            update_stat(Order("empty"), message.from_user, True)

            msg = self.bot.reply_to(message, """\
            מייד נזמין לך תור ! מה שמך ?
            """)
            self.bot.register_next_step_handler(msg, process_name_step)

        # steps

        # processing name
        def process_name_step(message):
            try:
                chat_id = message.chat.id
                name = message.text
                order = Order(name)
                self.user_dict[chat_id] = order
                update_stat(order, message.from_user)

                markup = InlineKeyboardMarkup()
                markup.row_width = 2
                markup.add(InlineKeyboardButton("היום", callback_data="cb_day_today"),
                           InlineKeyboardButton("מחר", callback_data="cb_day_tomorrow"))
                markup = self.add_reset(markup)
                msg = self.bot.reply_to(message, 'איזה יום נוח לך?', reply_markup=markup)

            except Exception as e:
                self.bot.reply_to(message, 'oooops')

        # processing day
        def process_day_step(call):
            chat_id = call.from_user.id
            order = self.user_dict[chat_id]

            call.data = call.data.replace("cb_day_", "")
            markup = InlineKeyboardMarkup()
            if call.data == "today":
                order.date = datetime.date.today()
                self.bot.answer_callback_query(call.id, "Today selected")
                markup = self.generate_hours(today=True)


            elif call.data == "tomorrow":
                order.date = datetime.date.today() + datetime.timedelta(days=1)
                self.bot.answer_callback_query(call.id, "Tomorrow selected")
                markup = generate_hours()
            markup = self.add_reset(markup)
            self.bot.send_message(chat_id, "איזה שעה ?", reply_markup=markup)
            # update_stat(order, call.from_user)

        # processing hour
        def process_hours_step(call):
            chat_id = call.from_user.id
            order = self.user_dict[chat_id]

            call.data = call.data.replace("cb_hours_", "")
            order.hours = call.data

            markup = self.generate_minutes(order)
            markup = self.add_reset(markup)
            self.bot.send_message(chat_id, "מתי בדיוק ?", reply_markup=markup)
            update_stat(order, call.from_user)

        # processing minutes
        def process_minutes_step(call):
            chat_id = call.from_user.id
            order = self.user_dict[chat_id]

            call.data = call.data.replace("cb_minutes_", "")
            order.minutes = call.data

            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add(types.KeyboardButton(text="שלח מספר שלי", request_contact=True))

            msg = self.bot.send_message(chat_id, "מה מספר הטלפון ?", reply_markup=markup)
            self.bot.register_next_step_handler(msg, process_phone_step)
            update_stat(order, call.from_user)

        # processingPhone
        def process_phone_step(message):
            try:
                chat_id = message.chat.id
                order = self.user_dict[chat_id]
                if message.contact is None:
                    order.phone = message.text
                else:
                    order.phone = message.contact.phone_number
                finalize_the_order(message)
            except Exception as e:
                self.bot.reply_to(message, 'oooops')

        # summarizing
        def finalize_the_order(call):
            chat_id = call.from_user.id
            order = self.user_dict[chat_id]
            markup = InlineKeyboardMarkup()
            markup = self.add_reset(markup)
            update_stat(order, call.from_user, close_record=True)

            self.bot.send_message(chat_id,
                                  'מגניב !' + order.name + ' היקר!  ' + '\n אנו מחכים לך ב \n' + str(
                                      order.date) + ' ' + str(
                                      order.hours) + ':' + str(order.minutes), reply_markup=markup)

            email_message = "New order for " + order.name + " Tel: " + order.phone + " at " + str(
                order.date) + " " + str(
                order.hours) + ":" + str(order.minutes)
            # send_email(email_message)
            if self.OWNER_ID != 0:
                self.bot.send_message(self.OWNER_ID, email_message)
            if self.UPDATE_CALENDAR:
                try:
                    set_event(order)
                except Exception as e:
                    print(e)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            try:
                if "cb_day" in call.data:
                    process_day_step(call)
                elif "cb_hours_" in call.data:
                    process_hours_step(call)
                elif "cb_minutes_" in call.data:
                    process_minutes_step(call)
                elif "cb_restart" in call.data:
                    restart_the_flow(call)






            except Exception as e:
                print(e)

    def add_reset(markup):
        new_row = []
        new_row.append(InlineKeyboardButton("התחל מחדש", callback_data="cb_restart"))
        markup.add(*new_row)
        return markup

    def generate_empty_schedule(self, ):
        hours = {}

        for h in range(START_TIME, END_TIME):
            slots = {}
            for m in range(0, 60, SLOT_SIZE):
                slots[m] = ""
            hours[h] = slots
        return hours

    def generate_hours(self, today=False):
        now = datetime.datetime.now()
        current_hour = int(now.strftime("%H"))
        sched = self.generate_empty_schedule()
        if UPDATE_CALENDAR:
            if today:
                sched = update_schedule_for_date(sched, datetime.date.today())
            else:
                tmw = datetime.date.today() + datetime.timedelta(days=1)
                sched = update_schedule_for_date(sched, tmw)

        min_hour = 0
        if today:
            min_hour = current_hour
        i = 0
        buttons_row = []
        markup = types.InlineKeyboardMarkup()

        for h, m in sched.items():
            if "" in m.values() and h > min_hour:  # only hours with empty slots
                if i % 3 != 0 and i != 0:
                    have_empty_slots = True
                    buttons_row.append(InlineKeyboardButton(h, callback_data="cb_hours_" + str(h)))
                else:
                    markup.add(*buttons_row)
                    buttons_row.clear()
                    buttons_row.append(InlineKeyboardButton(h, callback_data="cb_hours_" + str(h)))
                i = i + 1
        if len(buttons_row) > 0:
            markup.add(*buttons_row)
        return markup

    def generate_minutes(self, order):
        sched = self.generate_empty_schedule()
        if UPDATE_CALENDAR:
            sched = update_schedule_for_date(sched, order.date)

        i = 0
        buttons_row = []
        markup = types.InlineKeyboardMarkup()

        for m, t in sched[int(order.hours)].items():
            if t == "":  # only  empty slots
                if i % 3 != 0 and i != 0:

                    buttons_row.append(InlineKeyboardButton(m, callback_data="cb_minutes_" + str(m)))
                else:
                    markup.add(*buttons_row)
                    buttons_row.clear()
                    buttons_row.append(InlineKeyboardButton(m, callback_data="cb_minutes_" + str(m)))
                i = i + 1
        if len(buttons_row) > 0:
            markup.add(*buttons_row)

        return markup

    def start(self):
        self.thread = StoppableThread(name=self.bot.token, target=self.bot.polling, )
        self.thread.start()
        self.is_running = True

    def stop(self):

        self.thread.stop()
        self.is_running = True


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    API_TOKEN = config['Telegram']['api_token']
    last_updated_schedule = {}
    OWNER_ID = 0

    bot1 = Bot(API_TOKEN)

    bot1.start()
