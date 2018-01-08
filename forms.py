from datetime import datetime
from sanic import Sanic, response
from sanic_wtf import SanicForm
from wtforms import SubmitField, TextField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from wtforms.fields.html5 import EmailField


class SignUpForm(SanicForm):
    email = EmailField('Name', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=25)])