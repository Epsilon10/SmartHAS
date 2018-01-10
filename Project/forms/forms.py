from datetime import datetime
from sanic import Sanic, response
from sanic_wtf import SanicForm
from wtforms import SubmitField, TextField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from wtforms.fields.html5 import EmailField
from sanic import Sanic, response
import asyncio
import sys
sys.path.append("..")
from main import app
import motor.motor_asyncio

def uniqueDB():
    message = 'An account already exists for this email'
    loop = asyncio.get_event_loop()
    email_exists = loop.create_task(db_find()).result()
    if email_exists:
        raise ValidationError(message)

class SignUpForm(SanicForm):
    uniqueCheck = uniqueDB
    email = EmailField('Email', validators=[DataRequired(), Email(), uniqueDB()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=25)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=3, max=25)])


async def db_find():
    await app.db.find({form.data:{'$exists':True}})
