from datetime import datetime
from sanic import Sanic, response
from sanic_wtf import SanicForm
from wtforms import SubmitField, TextField, StringField, PasswordField, Form
from wtforms.validators import DataRequired, Length, Email, EqualTo


class SignUpForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=25), EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])


    
