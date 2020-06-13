from __future__ import print_function

import configparser
import pathlib

from Bots.bot_base import Bot_base

config = configparser.ConfigParser()
config.read('config.ini')

import datetime
import threading

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# <editor-fold desc="Calendar imports and Vars">
from google.oauth2 import service_account
from googleapiclient.discovery import build

CALENDAR_ID = config['Calendar']['calendar_id']
BOT_SERVICE_ID = config['Calendar']['bot_sevice_id']
SERVICE_ACCOUNT_FILE = config['Calendar']['service_credentials']
SLOT_SIZE_MIN = int(config['Workday']['slot_size_min'])
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


# </editor-fold>

# <editor-fold desc="Calendar functions">
def get_events_for_date(date):
    try:

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        service = build('calendar', 'v3', credentials=creds)

        dt = datetime.datetime.combine(date, datetime.datetime.min.time())

        now = dt.isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events
    except Exception as e:
        print(e)


def update_schedule_for_date(schedule, date):
    events = get_events_for_date(date)

    for event in events:
        startF = event['start']['dateTime']
        startT = startF.split('T')[1]
        startH = int(startT.split(':')[0])
        startM = int(startT.split(':')[1])
        sum = event['summary']
        schedule[startH][startM] = sum

    return schedule


def set_event(order):
    # setting service
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)

    message_text = order.name + " " + order.phone
    # dat=order.date.strftime("%Y-%M-%D")
    start = datetime.datetime(order.date.year, order.date.month, order.date.day, int(order.hours), int(order.minutes),
                              00, 000000)
    end = start + datetime.timedelta(minutes=SLOT_SIZE_MIN)
    # dat =dat +"T"+order.hours+":"+order.minutes+":00+03:00"

    event = {
        'summary': message_text,

        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'Asia/Jerusalem'
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'Asia/Jerusalem'
        },

    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()


# </editor-fold>

# <editor-fold desc="DB imports and vars">
import sqlite3

DATABASE = str(pathlib.Path(__file__).parent.absolute())+"/scheduler_db.sqlite"


# </editor-fold>

# <editor-fold desc="DB functions">
def orders_table_exist(c):
    # get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Orders' ''')

    # if the count is 1, then table exists
    if c.fetchone()[0] == 1:
        return True
    else:
        return False


def create_interactions(c):
    # Create table
    c.execute('''CREATE TABLE Interactions
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                     Started TIMESTAMP,
                     Ended TIMESTAMP,
                     OrderID int NOT NULL ,
                     UserFirst TEXT,
                     UserLast TEXT,
                     UserUser,
                     UserTeId int,
                     FOREIGN KEY(OrderID) REFERENCES Orders(OrderID)
                     )''')


def create_orders(c):
    # Create table
    c.execute('''CREATE TABLE Orders
                     (OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
                     Created TIMESTAMP,
                     Name TEXT,
                     Phone TEXT,
                     Date TEXT,
                     Hours TEXT,
                     Minutes TEXT
                     )''')


def validate_user(user):
    if user.first_name == None:
        user.first_name = ""
    if user.last_name == None:
        user.last_name = ""
    if user.username == None:
        user.last_name = ""
    if user.id == None:
        user.last_name = ""
    return user


def validate_order(order):
    if order.name is None:
        order.name = ""
    if order.phone is None:
        order.phone = ""
    if order.date is None:
        order.date = ""
    if order.hours is None:
        order.hours = ""
    if order.minutes is None:
        order.minutes = ""
    return order


def update_stat(order, user, new_record=False, close_record=False):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    naive_dt = datetime.datetime.now()
    if not orders_table_exist(c):
        create_interactions(c)
        create_orders(c)

    if new_record:
        # add order

        c.execute("INSERT INTO Orders (Created,Name,Phone,Date,Hours,Minutes) VALUES (?,?,?,?,?,?)",
                  (naive_dt, order.name, order.phone, order.date, order.hours, order.minutes))
        last_order = c.lastrowid

        user = validate_user(user)
        c.execute(
            "INSERT INTO Interactions (Started,Ended,OrderId,UserFirst,UserLast,UserUser,UserTeId) VALUES (?,?,?,?,?,?,?)",
            (naive_dt, "Null", last_order, user.first_name, user.last_name, user.username, user.id))
    else:
        # updating
        # get last interaction for user
        c.execute(
            "SELECT * FROM Interactions WHERE UserTeId = ? ORDER BY ID DESC LIMIT 1 ",
            (user.id,))

        i = c.fetchone()
        interact_id = i[0]
        order_id = i[3]

        # update Order
        c.execute("UPDATE Orders SET Name=?,Phone=?,Date=?,Hours=?,Minutes=? WHERE OrderId = ?",
                  (order.name, order.phone, order.date, order.hours, order.minutes, order_id))

    if close_record:
        # updating
        # get last interaction for user
        c.execute(
            "SELECT * FROM Interactions WHERE UserTeId = ? ORDER BY ID DESC LIMIT 1 ",
            (user.id,))

        i = c.fetchone()
        interact_id = i[0]
        order_id = i[3]

        # update Order
        c.execute("UPDATE Orders SET Name=?,Phone=?,Date=?,Hours=?,Minutes=? WHERE OrderId = ?",
                  (order.name, order.phone, order.date, order.hours, order.minutes, order_id))

        # update Interaction
        c.execute("UPDATE Interactions SET Ended=? WHERE ID = ?",
                  (naive_dt, interact_id))

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

    pass


# </editor-fold>


class Order:
    def __init__(self, name):
        self.name = name
        self.date = "None"
        self.hours = "None"
        self.minutes = "None"
        self.phone = "None"


class Schedule_bot(Bot_base):

    def __init__(self, key,bot_ID,password="rrr", update=False, start_time=8, end_time=20, interval=15,):
        super().__init__(key,password,bot_id=bot_ID)
        self.type="Scheduling bot"
        self.description="Scheduling bot to handle the que Hebrew Version"
        self.user_dict = {}
        self.START_TIME = start_time
        self.END_TIME = end_time
        self.SLOT_SIZE = interval
        self.UPDATE_CALENDAR = update

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
            try:
                self.add_message_to_db(message)
                update_stat(Order("empty"), message.from_user, True)

                msg = self.bot.reply_to(message, """\
                מייד נזמין לך תור ! מה שמך ?
                """)
                self.bot.register_next_step_handler(msg, process_name_step)
            except Exception as e:
                self.log_error(e)

        # steps

        # processing name
        def process_name_step(message):
            try:
                self.add_message_to_db(message)
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
                self.log_error(e)

        # processing day
        def process_day_step(call):
            try:
                chat_id = call.from_user.id
                if chat_id in self.user_dict.keys():
                    order = self.user_dict[chat_id]
                else:
                    #from old chat - no name
                    return

                call.data = call.data.replace("cb_day_", "")
                markup = InlineKeyboardMarkup()
                if call.data == "today":
                    order.date = datetime.date.today()
                    self.bot.answer_callback_query(call.id, "Today selected")
                    markup = self.generate_hours(today=True)


                elif call.data == "tomorrow":
                    order.date = datetime.date.today() + datetime.timedelta(days=1)
                    self.bot.answer_callback_query(call.id, "Tomorrow selected")
                    markup = self.generate_hours()
                markup = self.add_reset(markup)
                self.bot.send_message(chat_id, "איזה שעה ?", reply_markup=markup)
            except Exception as e:
                self.log_error(e)
            # update_stat(order, call.from_user)

        # processing hour
        def process_hours_step(call):
            try:
                chat_id = call.from_user.id
                if chat_id in self.user_dict.keys():
                    order = self.user_dict[chat_id]
                else:
                    #from old chat - no name
                    return
                call.data = call.data.replace("cb_hours_", "")
                order.hours = call.data

                markup = self.generate_minutes(order)
                markup = self.add_reset(markup)
                self.bot.send_message(chat_id, "מתי בדיוק ?", reply_markup=markup)
                update_stat(order, call.from_user)
            except Exception as e:
                self.log_error(e)

        # processing minutes
        def process_minutes_step(call):
            try:
                chat_id = call.from_user.id
                if chat_id in self.user_dict.keys():
                    order = self.user_dict[chat_id]
                else:
                    #from old chat - no name
                    return
                call.data = call.data.replace("cb_minutes_", "")
                order.minutes = call.data

                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                markup.add(types.KeyboardButton(text="שלח מספר שלי", request_contact=True))

                msg = self.bot.send_message(chat_id, "מה מספר הטלפון ?", reply_markup=markup)
                self.bot.register_next_step_handler(msg, process_phone_step)
                update_stat(order, call.from_user)
            except Exception as e:
                self.log_error(e)

        # processingPhone
        def process_phone_step(message):
            try:
                self.add_message_to_db(message)
                chat_id = message.chat.id
                if chat_id in self.user_dict.keys():
                    order = self.user_dict[chat_id]
                else:
                    #from old chat - no name
                    return
                if message.contact is None:
                    order.phone = message.text
                else:
                    order.phone = message.contact.phone_number
                finalize_the_order(message)
            except Exception as e:
                self.log_error(e)

        # summarizing
        def finalize_the_order(call):
            try:
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
            except Exception as e:
                self.log_error(e)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):

            self.add_message_to_db(call)
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
                self.log_error(e)


    def generate_empty_schedule(self, ):
        hours = {}

        for h in range(self.START_TIME, self.END_TIME):
            slots = {}
            for m in range(0, 60, self.SLOT_SIZE):
                slots[m] = ""
            hours[h] = slots
        return hours

    def generate_hours(self, today=False):
        now = datetime.datetime.now()
        current_hour = int(now.strftime("%H"))
        sched = self.generate_empty_schedule()
        if self.UPDATE_CALENDAR:
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
        if self.UPDATE_CALENDAR:
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



if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    API_TOKEN = config['Telegram']['api_token']
    last_updated_schedule = {}
    OWNER_ID = 0

    bot1 = Schedule_bot(API_TOKEN)

    bot1.start()
