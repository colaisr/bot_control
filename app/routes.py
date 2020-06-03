import configparser
import datetime

from flask import Flask, render_template_string, request, url_for
from flask_babelex import Babel
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
# Class-based application configuration
from werkzeug import utils
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from wtforms.widgets import HiddenInput

from Bots import bot_tele
from flask_user import UserMixin, UserManager, login_required, roles_required

# LILI imports
from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm


# The Home page is accessible to anyone
@app.route('/')
@app.route('/home')
def home_page():
    user = current_user
    if user.is_authenticated:
        return utils.redirect(url_for('bots_page'))
    else:
        return render_template('home.html', title='Home')

# The Bots page showing the bots per user
@app.route('/bots')
@login_required
def bots_page():
    user_id = current_user.id
    user_in_db = User.query.filter(User.id == user_id).first()
    bots = user_in_db.bots
    return render_template('bots.html', bots=bots)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('home_page'))
    return render_template('login.html', title='Sign In', form=form)




# class ConfigClass(object):
#     """ Flask application config """
#     config = configparser.ConfigParser()
#     config.read('config.ini')
#     # Flask settings
#     SECRET_KEY = config['Security']['secret_key']
#
#     # Flask-SQLAlchemy settings
#     SQLALCHEMY_DATABASE_URI = config['DB']['db_file']  # File-based SQL database
#     SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning
#
#     # Flask-Mail SMTP server settings
#     MAIL_SERVER = 'smtp.gmail.com'
#     MAIL_PORT = 465
#     MAIL_USE_SSL = True
#     MAIL_USE_TLS = False
#     MAIL_USERNAME = config['Mail']['mail']
#     MAIL_PASSWORD = config['Mail']['pass']
#     MAIL_DEFAULT_SENDER = '"Bot Control" <noreply@example.com>'
#
#     # Flask-User settings
#     USER_APP_NAME = "Bot Control"  # Shown in and email templates and page footers
#     USER_APP_VERSION = "1.01"
#     USER_COPYRIGHT_YEAR = "2020"
#     USER_CORPORATION_NAME = "BotGeeks"
#     USER_ENABLE_EMAIL = True  # Enable email authentication
#     USER_ENABLE_USERNAME = False  # Disable username authentication
#     USER_EMAIL_SENDER_NAME = USER_APP_NAME
#     USER_EMAIL_SENDER_EMAIL = "noreply@example.com"


# #app = Flask(__name__)
# app.config.from_object(__name__ + '.ConfigClass')

# Initialize Flask-BabelEx
babel = Babel(app)

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)

ALL_RUNNING_BOTS = {}


# Define the User data-model.
# NB: Make sure to add flask_user UserMixin !!!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')
    # Define the relationship to Bots via UserBots
    bots = db.relationship('Bot', secondary='user_bots')


# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# Define the UserBots association table
class UserBots(db.Model):
    __tablename__ = 'user_bots'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    bot_id = db.Column(db.Integer(), db.ForeignKey('bots.id', ondelete='CASCADE'))


class Bot(db.Model):
    __tablename__ = 'bots'
    id = db.Column(db.Integer, primary_key=True)
    is_running = db.Column(db.Boolean(), nullable=False, server_default='0')

    name = db.Column(db.String(255, collation='NOCASE'), nullable=False, server_default='')
    api_key = db.Column(db.String(255, collation='NOCASE'), nullable=False, server_default='')
    calendar_id = db.Column(db.String(255, collation='NOCASE'), nullable=False, server_default='')
    created_at = db.Column(db.DateTime())


# Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)

# Create all database tables
db.create_all()

# Create 'member@example.com' user with no roles
if not User.query.filter(User.email == 'member@example.com').first():
    user = User(
        email='member@example.com',
        email_confirmed_at=datetime.datetime.utcnow(),
        password=user_manager.hash_password('Password1'),
    )
    db.session.add(user)
    db.session.commit()

# Create 'admin@example.com' user with 'Admin' and 'Agent' roles
if not User.query.filter(User.email == 'admin@example.com').first():
    user = User(
        email='admin@example.com',
        email_confirmed_at=datetime.datetime.utcnow(),
        password=user_manager.hash_password('Password1'),
    )
    user.roles.append(Role(name='Admin'))
    user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()


class BotCreateForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    api_key = StringField('api_key')
    calendar_id = StringField('calendar_id')
    submit = SubmitField('Submit')


class BotUpdateForm(BotCreateForm):
    id = IntegerField(widget=HiddenInput())



@app.route('/createbotform', methods=('GET', 'POST'))
@login_required
def register_bot():
    form = BotCreateForm()
    r = form.validate_on_submit()
    if r:
        user_id = current_user.id

        bot = Bot(
            name=form.name.data,
            api_key=form.api_key.data,
            calendar_id=form.calendar_id.data,
            created_at=datetime.datetime.now()
        )
        user_in_db = User.query.filter(User.id == user_id).first()
        user_in_db.bots.append(bot)
        db.session.add(bot)
        db.session.commit()

        return utils.redirect(url_for('bots_page'))
    return render_template('bot_create_form.html', form=form)


@app.route('/editbot/<botId>', methods=['GET', 'POST'])
@login_required
def edit_bot(botId):
    bot_in_db = Bot.query.filter(Bot.id == botId).first()
    if bot_in_db:

        form = BotUpdateForm(obj=bot_in_db)
        r = form.validate_on_submit()
        if r:
            form.populate_obj(bot_in_db)

            db.session.commit()

            return utils.redirect(url_for('bots_page'))
        else:
            return render_template('bot_update_form.html', form=form, BotId=bot_in_db.id)
    else:
        return 'Error loading #{id}'.format(id=botId)


@app.route('/action')
@login_required
def action():
    global ALL_RUNNING_BOTS
    bot_id = request.args.get("botId", None)
    is_start = request.args.get("isStart", 'false')
    if is_start.lower() == 'true':
        bot_in_db = Bot.query.filter(Bot.id == bot_id).first()
        if bot_in_db:
            ALL_RUNNING_BOTS[str(bot_in_db.id)] = bot_tele.Bot(bot_in_db.api_key, update=True)
            ALL_RUNNING_BOTS[str(bot_in_db.id)].start()
        else:
            return 'Error starting #{id}'.format(id=bot_id)
    else:
        if bot_id in ALL_RUNNING_BOTS:

            ALL_RUNNING_BOTS[bot_id].stop()
            del ALL_RUNNING_BOTS[bot_id]
        else:
            return 'Error stopping #{id}'.format(id=bot_id)
    return utils.redirect(url_for('bots_page'))

@app.route('/createbot')
@login_required
def create_bot():
    user_id = current_user.id
    bot_name = request.form['botname']

    bot = Bot(
        name=request.form['botname'],
        api_key=request.form['api_key'],
        calendar_id=request.form['googlecalendar_id'],
        created_at=datetime.datetime.now(),

    )
    user_in_db = User.query.filter(User.id == user_id).first()
    user_in_db.bots.append(bot)
    db.session.add(bot)
    db.session.commit()

    return utils.redirect(url_for('bots_page'))


# The Members page is only accessible to authenticated users
@app.route('/members')
@login_required  # Use of @login_required decorator
def member_page():
    return render_template_string("""
            {% extends "flask_user_layoutN.html" %}
            {% block content %}
                <h2>{%trans%}Members page{%endtrans%}</h2>
                <p><a href={{ url_for('user.register') }}>{%trans%}Register{%endtrans%}</a></p>
                <p><a href={{ url_for('user.login') }}>{%trans%}Sign in{%endtrans%}</a></p>
                <p><a href={{ url_for('home_page') }}>{%trans%}Home Page{%endtrans%}</a> (accessible to anyone)</p>
                <p><a href={{ url_for('member_page') }}>{%trans%}Member Page{%endtrans%}</a> (login_required: member@example.com / Password1)</p>
                <p><a href={{ url_for('admin_page') }}>{%trans%}Admin Page{%endtrans%}</a> (role_required: admin@example.com / Password1')</p>
                <p><a href={{ url_for('user.logout') }}>{%trans%}Sign out{%endtrans%}</a></p>
            {% endblock %}
            """)


# hm
# The Admin page requires an 'Admin' role.
@app.route('/admin')
@roles_required('Admin')  # Use of @roles_required decorator
def admin_page():
    return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>{%trans%}Admin Page{%endtrans%}</h2>
                <p><a href={{ url_for('user.register') }}>{%trans%}Register{%endtrans%}</a></p>
                <p><a href={{ url_for('user.login') }}>{%trans%}Sign in{%endtrans%}</a></p>
                <p><a href={{ url_for('home_page') }}>{%trans%}Home Page{%endtrans%}</a> (accessible to anyone)</p>
                <p><a href={{ url_for('member_page') }}>{%trans%}Member Page{%endtrans%}</a> (login_required: member@example.com / Password1)</p>
                <p><a href={{ url_for('admin_page') }}>{%trans%}Admin Page{%endtrans%}</a> (role_required: admin@example.com / Password1')</p>
                <p><a href={{ url_for('user.logout') }}>{%trans%}Sign out{%endtrans%}</a></p>
            {% endblock %}
            """)


# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('errors/404.html'), 404


# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('errors/page_not_found.html'), 404


