from datetime import datetime
from sanic import Sanic, response
from sanic_wtf import SanicForm
from wtforms import SubmitField, TextField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from wtforms.fields.html5 import EmailField
from sanic import Sanic, response
import asyncio
import sys
import motor.motor_asyncio

def uniqueDB():
        message = 'An account already exists for this email'
        loop = asyncio.get_event_loop()
        email_exists = loop.create_task(db_find()).result()
        if email_exists:
            raise ValidationError(message)
    
async def db_find():
    return await app.db.find({form.data:{'$exists':True}})

class SignUpForm(SanicForm):
    email = EmailField('Email', validators=[DataRequired(), Email(), uniqueDB])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=25)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=3, max=25)])


    
