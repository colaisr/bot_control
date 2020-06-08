from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField
from wtforms.validators import DataRequired
from wtforms.widgets import HiddenInput

# class LoginForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     remember_me = BooleanField('Remember Me')
#     submit = SubmitField('Sign In')

class BotCreateForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    api_key = StringField('api_key')
    calendar_id = StringField('calendar_id')
    submit = SubmitField('Submit')


class BotUpdateForm(BotCreateForm):
    id = IntegerField(widget=HiddenInput())

class DeleteForm(FlaskForm):
    id = IntegerField(widget=HiddenInput())