import configparser
import os

class Config(object):
    """ Flask application config """
    config = configparser.ConfigParser()
    config.read('config.ini')
    # Flask settings
    SECRET_KEY = config['Security']['secret_key'] #os.environ.get('SECRET_KEY')

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = config['DB']['new_db_file']  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = config['Mail']['mail']
    MAIL_PASSWORD = config['Mail']['pass']
    MAIL_DEFAULT_SENDER = '"Bot Control" <noreply@example.com>'

    # Flask-User settings
    USER_APP_NAME = "Bot Control"  # Shown in and email templates and page footers
    USER_APP_VERSION = "1.01"
    USER_COPYRIGHT_YEAR = "2020"
    USER_CORPORATION_NAME = "BotGeeks"
    USER_ENABLE_EMAIL = True  # Enable email authentication
    USER_ENABLE_USERNAME = False  # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"