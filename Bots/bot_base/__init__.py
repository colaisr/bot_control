import threading

import telebot
from telebot.types import InlineKeyboardButton


class Bot_base:
  def __init__(self,key,password):
    self.bot = telebot.TeleBot(key)
    self.thread = None
    self.OWNER_ID = 0
    self.OWNER_PASSWORD=password

    # Handle '/master command
    @self.bot.message_handler(commands=['master'])
    def confirm_master(message):

      msg = self.bot.reply_to(message, """\
        Are you the Master ? Password: 
        """)
      self.bot.register_next_step_handler(msg, process_master_set)

    # processing the belonging
    def process_master_set(message):
      try:
        chat_id = message.chat.id
        name = message.text
        user_id = message.chat.id

        if message.text.lower() == self.OWNER_PASSWORD:
          self.OWNER_ID = user_id
          self.bot.reply_to(message, 'Great ! Updated')
        else:
          self.bot.reply_to(message, 'Wrong password -please restart')

      except Exception as e:
        self.bot.reply_to(message, 'oooops')

  def start(self):
    """
Starts the bot in separate thread
    """
    self.thread = threading.Thread(name=self.bot.token, target=self.bot.polling)
    self.thread.start()

  def stop(self):
    """
Stops the bot thread
    """
    self.bot.stop_bot()

  def add_reset(self, markup):
    """
Add restart button to the bottom of the markup
    :param markup: the telebot markup
    :return: standard telebot markup
    """
    new_row = []
    new_row.append(InlineKeyboardButton("התחל מחדש", callback_data="cb_restart"))
    markup.add(*new_row)
    return markup


