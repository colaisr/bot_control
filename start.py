import configparser
import datetime

import logging

# print log in example.log instead of the console, and set the log level to DEBUG (by default, it is set to WARNING)
logging.basicConfig(filename='example.log', filemode='w', level=logging.INFO)

logging.info('Server Started')

import importlib
import os

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

from Bots import schedule_bot, echo_bot
from flask_user import UserMixin, UserManager, login_required, roles_required

# LILI imports
from flask import render_template, flash, redirect, jsonify
# from app import app
# from forms import BotCreateForm, BotUpdateForm
import forms as forms

from config import Config
import json
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)


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
    for x in bots:
        if str(x.id) in ALL_RUNNING_BOTS:
            x.is_running=True
    return render_template('lili/bots_lil.html', bots=bots)


@app.route('/action')
@login_required
def action():
    global ALL_RUNNING_BOTS
    bot_id = request.args.get("botId", None)
    is_start = request.args.get("isStart", 'false')
    try:
        if is_start.lower() == 'true':
            bot_in_db = Bot.query.filter(Bot.id == bot_id).first()
            if bot_in_db:
                ALL_RUNNING_BOTS[str(bot_in_db.id)] = echo_bot.Inherited_bot(key=bot_in_db.api_key,bot_ID=bot_in_db.id)
                ALL_RUNNING_BOTS[str(bot_in_db.id)].start()
            else:
                return 'Error starting #{id}'.format(id=bot_id)
        else:
            if bot_id in ALL_RUNNING_BOTS:

                ALL_RUNNING_BOTS[bot_id].stop()
                del ALL_RUNNING_BOTS[bot_id]
            else:
                return 'Error stopping #{id}'.format(id=bot_id)
    except Exception as inst:
        print("oop")
    return utils.redirect(url_for('bots_page'))


@app.route('/editbot/<botId>', methods=['GET', 'POST'])
@login_required
def edit_bot(botId):
    bot_in_db = Bot.query.filter(Bot.id == botId).first()
    if bot_in_db:

        form = forms.BotUpdateForm(obj=bot_in_db)
        if request.method == 'POST':
            if form.validate_on_submit():
                form.populate_obj(bot_in_db)
                db.session.commit()
                return jsonify(status='ok')
            else:
                data = json.dumps(form.errors, ensure_ascii=False)
                return jsonify(data)
        return render_template('lili/_form_bot_add_or_update.html', form=form, BotId=bot_in_db.id)
    else:
        return 'Error loading #{id}'.format(id=botId)


@app.route('/createbot', methods=['GET', 'POST'])
@login_required
def create_bot():
    user_id = current_user.id

    #getting all available bots
    bots_dir=os.getcwd()+'/Bots'
    dir_and_bot={}
    imported_bots={}
    for d in os.listdir(bots_dir):
        if d.endswith("_bot"):
            dir_and_bot[d]=os.path.join(bots_dir, d)

    all_bots_folders= [os.path.join(bots_dir, d) for d in os.listdir(bots_dir)]
    for k,v in dir_and_bot.items():
        imported_bots[k]=importlib.import_module("Bots"+"."+k, package=None)

    # imported bots is ready for listing and creation

        # selected_bot='echo_bot'
        # new_eco_bot=imported_bots[selected_bot].Inherited_bot("sda","32")

    form = forms.BotCreateForm()
    if request.method == 'POST':
        if form.validate_on_submit():
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
            return jsonify(status='ok')
        else:
            data = json.dumps(form.errors, ensure_ascii=False)
            return jsonify(data)
    return render_template('lili/_form_bot_add_or_update.html', form=form)


@app.route('/deletebot/<botId>', methods=['GET', 'POST'])
@login_required
def delete_bot(botId):
    bot_in_db = Bot.query.filter(Bot.id == botId).first()
    if bot_in_db:
        form = forms.DeleteForm()
        form.id.data = botId
        if request.method == 'POST':
            if form.validate_on_submit():
                db.session.delete(bot_in_db)
                db.session.commit()
                return jsonify(status='ok')
            else:
                data = json.dumps(form.errors, ensure_ascii=False)
                return jsonify(data)
        return render_template('lili/_form_delete.html',
                               question=f'are you sure you want to remove the bot {bot_in_db.name}', form=form,
                               BotId=bot_in_db.id)
    else:
        return 'Error loading #{id}'.format(id=botId)


# @app.route('/detailse/<id>', methods=['GET', 'POST'])
# def user_edit(id):
#     user = User.query.filter_by(id=id).first_or_404()
#     form = ProfileEditForm(user.email)
#     if form.validate_on_submit():
#         user.email = form.email.data
#         db.session.commit()
#         return jsonify(status='ok')
#     elif request.method == 'GET':
#         form.email.data = user.email
#     else:
#         data = json.dumps(form.errors, ensure_ascii=False)
#         return jsonify(data)
#     return render_template('_form_edit.html', title="Редактирование пользователя", form=form)

#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         flash('Login requested for user {}, remember_me={}'.format(
#             form.username.data, form.remember_me.data))
#         return redirect(url_for('home_page'))
#     return render_template('login.html', title='Sign In', form=form)


# Initialize Flask-BabelEx
# babel = Babel(app)

# # Initialize Flask-SQLAlchemy
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


if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
# # comment cola
## test lili
