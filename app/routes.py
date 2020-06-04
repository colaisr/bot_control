import configparser
import datetime

from flask import Flask, render_template_string, request, url_for
from flask_babelex import Babel
# from flask_login import current_user
# from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
# Class-based application configuration
from werkzeug import utils
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from wtforms.widgets import HiddenInput

from Bots import bot_tele
# from flask_user import UserMixin, UserManager, login_required, roles_required
# from flask_user import UserManager, login_required, roles_required

# LILI imports
from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

from app import db


# The Home page is accessible to anyone
@app.route('/')
@app.route('/home')
def home_page():
    # if current_user.is_authenticated:
    #     return utils.redirect(url_for('bots_page'))
    # else:
    #     return render_template('home.html', title='Home')
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
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home_page'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))


# Initialize Flask-BabelEx
babel = Babel(app)

# Initialize Flask-SQLAlchemy
# db = SQLAlchemy(app)

ALL_RUNNING_BOTS = {}

# Setup Flask-User and specify the User data-model
# user_manager = UserManager(app, db, User)

# Create all database tables
# db.create_all()

# Create 'member@example.com' user with no roles
if not User.query.filter(User.email == 'member@example.com').first():
    user = User(
        email='member@example.com',
        email_confirmed_at=datetime.datetime.utcnow()
        # password_hash=user_manager.hash_password('Password1'),
    )
    user.set_password('Password1');
    db.session.add(user)
    db.session.commit()

# Create 'admin@example.com' user with 'Admin' and 'Agent' roles
if not User.query.filter(User.email == 'admin@example.com').first():
    user = User(
        email='admin@example.com',
        email_confirmed_at=datetime.datetime.utcnow()
        # password_hash=user_manager.hash_password('Password1'),
    )
    user.set_password('Password1');
    # user.roles.append(Role(name='Admin'))
    # user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()


class BotCreateForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    api_key = StringField('api_key')
    calendar_id = StringField('calendar_id')
    submit = SubmitField('Submit')


class BotUpdateForm(BotCreateForm):
    id = IntegerField(widget=HiddenInput())


# @app.route('/createbotform', methods=('GET', 'POST'))
# @login_required
# def register_bot():
#     form = BotCreateForm()
#     r = form.validate_on_submit()
#     if r:
#         user_id = current_user.id
#
#         bot = Bot(
#             name=form.name.data,
#             api_key=form.api_key.data,
#             calendar_id=form.calendar_id.data,
#             created_at=datetime.datetime.now()
#         )
#         user_in_db = User.query.filter(User.id == user_id).first()
#         user_in_db.bots.append(bot)
#         db.session.add(bot)
#         db.session.commit()
#
#         return utils.redirect(url_for('bots_page'))
#     return render_template('bot_create_form.html', form=form)
#
#
# @app.route('/editbot/<botId>', methods=['GET', 'POST'])
# @login_required
# def edit_bot(botId):
#     bot_in_db = Bot.query.filter(Bot.id == botId).first()
#     if bot_in_db:
#
#         form = BotUpdateForm(obj=bot_in_db)
#         r = form.validate_on_submit()
#         if r:
#             form.populate_obj(bot_in_db)
#
#             db.session.commit()
#
#             return utils.redirect(url_for('bots_page'))
#         else:
#             return render_template('bot_update_form.html', form=form, BotId=bot_in_db.id)
#     else:
#         return 'Error loading #{id}'.format(id=botId)
#
#
# @app.route('/action')
# @login_required
# def action():
#     global ALL_RUNNING_BOTS
#     bot_id = request.args.get("botId", None)
#     is_start = request.args.get("isStart", 'false')
#     if is_start.lower() == 'true':
#         bot_in_db = Bot.query.filter(Bot.id == bot_id).first()
#         if bot_in_db:
#             ALL_RUNNING_BOTS[str(bot_in_db.id)] = bot_tele.Bot(bot_in_db.api_key, update=True)
#             ALL_RUNNING_BOTS[str(bot_in_db.id)].start()
#         else:
#             return 'Error starting #{id}'.format(id=bot_id)
#     else:
#         if bot_id in ALL_RUNNING_BOTS:
#
#             ALL_RUNNING_BOTS[bot_id].stop()
#             del ALL_RUNNING_BOTS[bot_id]
#         else:
#             return 'Error stopping #{id}'.format(id=bot_id)
#     return utils.redirect(url_for('bots_page'))
#
# @app.route('/createbot')
# @login_required
# def create_bot():
#     user_id = current_user.id
#     bot_name = request.form['botname']
#
#     bot = Bot(
#         name=request.form['botname'],
#         api_key=request.form['api_key'],
#         calendar_id=request.form['googlecalendar_id'],
#         created_at=datetime.datetime.now(),
#
#     )
#     user_in_db = User.query.filter(User.id == user_id).first()
#     user_in_db.bots.append(bot)
#     db.session.add(bot)
#     db.session.commit()
#
#     return utils.redirect(url_for('bots_page'))


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
# @roles_required('Admin')  # Use of @roles_required decorator
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
