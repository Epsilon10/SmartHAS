from datetime import datetime
from sanic import Sanic, response
from sanic.response import html, text, json, HTTPResponse, redirect
from sanic_wtf import SanicForm
from jinja2 import Environment, PackageLoader
from sanic.views import HTTPMethodView
import os
from sanic_session import InMemorySessionInterface
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
from app.forms import SignUpForm, LoginForm
from pprint import pprint
from app.models import open_db_pool, fetch_row, fetch_val, fetch_many, execute_job
from app import app
import asyncio
import logging
from sanic.exceptions import SanicException
from sanic_auth import Auth, User
from wtforms import SubmitField, TextField, StringField, PasswordField, Form
from wtforms.validators import DataRequired, Length, Email, EqualTo

app.config['SECRET_KEY'] = 'top secret !!!'

env = Environment(loader=PackageLoader('app', 'templates'))
session_interface = InMemorySessionInterface()
app.static('/static', './app/static')
app.config.AUTH_LOGIN_ENDPOINT = 'login'
app.config.DSN = open('./app/config/dns.txt').read()
auth = Auth(app)

def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))

@app.listener('before_server_start')
async def server_begin(app, loop):
    app.session = aiohttp.ClientSession(loop=loop)
    app.db_pool = await open_db_pool(app.config.DSN)


@app.listener('after_server_stop')
async def server_end(app, loop):
    await app.db_pool.close()
    app.session.close()

@app.middleware('request')
async def add_session_to_request(request):
    await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
    await session_interface.save(request, response)

@app.route('/signup', methods=['GET', 'POST'])
async def _signup(request):
    form = SignUpForm(request.form)
    if request.method == 'POST':
        print(form.errors)
        if form.validate():
            email = form.email.data
            unique_email = (await fetch_row('SELECT * FROM details WHERE email = $1', email)) == None
            if unique_email:
                await execute_job('INSERT INTO details (email,password) VALUES ($1, $2)', email, form.password.data)
                #TODO: Sign in and other stuff + auth 
                return template('login.html')
            form.email.errors.append('An account with this email already exists!')
        return template('signup.html', form=form)
    return template('signup.html', form=SignUpForm())

@app.route('/login', methods=['GET','POST'])
async def _login(request):
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            email = form.email.data
            password = form.password.data
            account_data = await fetch_row('SELECT * FROM details WHERE email = $1', email)
            valid_account = False
            if account_data is not None:
                valid_account = account_data['email'] == email and account_data['password'] == password
            if valid_account:
                user = User(id=1,name=email)
                auth.login_user(user, request)
                return response.redirect('/')
            form.email.errors.append('An account does not exist with this email.')
        return template('login.html', form=form)
    return template('login.html', form=LoginForm())



@app.route('/')
async def home(request):
    return text('hi')

