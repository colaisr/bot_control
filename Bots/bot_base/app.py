import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading

class Bot:

    def __init__(self, key, owner_id=0):
        self.bot = telebot.TeleBot(key)
        self.user_dict = {}
        # self.START_TIME = start_time
        # self.END_TIME = end_time
        # self.SLOT_SIZE = interval
        # self.UPDATE_CALENDAR = update
        self.OWNER_ID = owner_id
        self.thread = None

        def start(self):

            self.thread = threading.Thread(name=self.bot.token, target=self.bot.polling)
            self.thread.start()

        def stop(self):
            self.bot.stop_bot()



