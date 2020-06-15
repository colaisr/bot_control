import pathlib
import threading
from datetime import datetime

import telebot
from telebot.types import InlineKeyboardButton, Message, CallbackQuery

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String,DateTime




# <editor-fold desc="DB Vars">
DATABASE = str(pathlib.Path(__file__).parent.absolute())+"/stats_db.sqlite"
engine = create_engine('sqlite:///'+DATABASE)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# </editor-fold>

# <editor-fold desc="DB classes">
class TeleMessage(Base):
  __tablename__ = 'messages'

  id = Column(Integer, primary_key=True)
  received = Column(DateTime)
  fromUserId = Column(String)
  fromUserUserName = Column(String)
  botID=Column(String)
  messageText=Column(String)

class BotErrors(Base):
  __tablename__ = 'errors'

  id = Column(Integer, primary_key=True)
  occurence = Column(DateTime)
  botID=Column(String)
  errorText=Column(String)

Base.metadata.create_all(engine)
# </editor-fold>


class Bot_base:
  def __init__(self,key,password,bot_id):
    self.BOT_SYSTEM_ID=bot_id
    self.bot = telebot.TeleBot(key)
    self.thread = None
    self.OWNER_ID = 0
    self.CUSTOMPROPERTY_OWNER_PASSWORD=password
    self.CUSTOMPROPERTY_API_KEY=key

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

        if message.text.lower() == self.CUSTOMPROPERTY_OWNER_PASSWORD:
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
    try:
      self.thread = threading.Thread(name=self.bot.token, target=self.bot.polling)
      self.thread.start()
    except Exception as e:
      self.log_error(e)

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

  def add_message_to_db(self,message):
    naive_dt = datetime.now()
    if type(message) == Message:
      db_message = TeleMessage(received=naive_dt,fromUserId=message.from_user.id,fromUserUserName=message.from_user.username,botID=self.BOT_SYSTEM_ID,messageText=message.html_text)
    elif type(message) == CallbackQuery:
      db_message = TeleMessage(received=naive_dt,fromUserId=message.from_user.id,
                               fromUserUserName=message.from_user.username,
                               botID=self.BOT_SYSTEM_ID,messageText=message.data)

    session.add(db_message)
    session.commit()

  def log_error(self,error):
    problem=error.args[0]
    naive_dt = datetime.now()
    db_error = BotErrors(received=naive_dt,  botID=self.BOT_SYSTEM_ID,
                             errorText=problem)

    session.add(db_error)
    session.commit()

