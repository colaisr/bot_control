import configparser
import datetime

from flask import Flask, render_template, render_template_string, request, url_for
from flask_babelex import Babel
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
# Class-based application configuration
from werkzeug.utils import redirect

from flask_user import UserMixin, UserManager, login_required, roles_required


class ConfigClass(object):
    """ Flask application config """
    config = configparser.ConfigParser()
    config.read('config.ini')
    # Flask settings
    SECRET_KEY = config['Security']['secret_key']

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = config['DB']['db_file']  # File-based SQL database
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


app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')

# Initialize Flask-BabelEx
babel = Babel(app)

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)


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


class Bot(db.Model, UserMixin):
    __tablename__ = 'bots'
    id = db.Column(db.Integer, primary_key=True)
    running = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    name = db.Column(db.String(255, collation='NOCASE'), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')


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


# The Home page is accessible to anyone
@app.route('/')
def home_page():
    user = current_user
    if user.is_authenticated:
        return redirect(url_for('bots_page'))
    else:
        return render_template('home.html')


# The Bots page showing the bots per user
@app.route('/bots')
def bots_page():
    user_id = current_user.id
    user_in_db = User.query.filter(User.id == user_id).first()
    bots = user_in_db.bots
    return render_template('bots.html', bots=bots)


@app.route('/createbot', methods=['POST'])
def create_bot():
    user_id = current_user.id
    bot_name = request.form['botname']

    bot = Bot(
        name=bot_name,

    )
    user_in_db = User.query.filter(User.id == user_id).first()
    user_in_db.bots.append(bot)
    db.session.add(bot)
    db.session.commit()

    return redirect(url_for('bots_page'))


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


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.run()
