from __future__ import print_function

import configparser
import pathlib

from Bots.bot_base import Bot_base

config = configparser.ConfigParser()
config.read('config.ini')

import datetime
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton




class Order:
    def __init__(self, name):
        self.name = name
        self.date = "None"
        self.hours = "None"
        self.minutes = "None"
        self.phone = "None"


class Inherited_bot(Bot_base):

    def __init__(self, key,bot_ID,password="rrr", setting1="",setting2=""):
        super().__init__(key,password,bot_id=bot_ID)
        self.type="Echo bot"
        self.description="Simplest bot possible testing API testing Settings "
        self.user_dict = {}
        self.CUSTOMPROPERTY_CUSTOM_SETTING1 = setting1
        self.CUSTOMPROPERTY_CUSTOM_SETTING2 = setting2

        # Handle '/start'
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):

            msg = self.bot.reply_to(message, """\
            Hello im working properly - say something:
            """)
        # steps

        # processing name

        @self.bot.message_handler(func=lambda call: True)
        def callback_query(message):
            try:
                msg = self.bot.reply_to(message, """\
                You told:
                """+message.text)

            except Exception as e:
                print(e)





# if __name__ == '__main__':
#     config = configparser.ConfigParser()
#     config.read('config.ini')
#
#     API_TOKEN = config['Telegram']['api_token']
#     last_updated_schedule = {}
#     OWNER_ID = 0
#
#     bot1 = ScheduleR_bot(API_TOKEN)
#
#     bot1.start()
