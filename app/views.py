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
from app.models import open_db_pool, fetch_row, fetch_val, fetch_many, execute_job, User, fetch_user
from app import app
import asyncio
import logging
from sanic.exceptions import SanicException
from sanic_auth import Auth
from wtforms import SubmitField, TextField, StringField, PasswordField, Form
from wtforms.validators import DataRequired, Length, Email, EqualTo
import inspect
import ujson
import hashlib, binascii
app.config['SECRET_KEY'] = 'top secret !!!'

env = Environment(loader=PackageLoader('app', 'templates'))
session_interface = InMemorySessionInterface()
app.static('/static', './app/static')
app.config.AUTH_LOGIN_ENDPOINT = 'login'

with open('./app/config/config.json') as f:
    CONFIG = ujson.loads(f.read())

def template(tpl, *args, **kwargs):
    template = env.get_template(tpl)
    request = get_stack_variable('request')
    user = None
    if request['session'].get('logged_in'):
        user = request['session']['user']
    kwargs['request'] = request
    kwargs['session'] = request['session']
    kwargs['user'] = user
    kwargs.update(globals())
    return html(template.render(*args,**kwargs))

@app.listener('before_server_start')
async def server_begin(app, loop):
    app.session = aiohttp.ClientSession(loop=loop)
    app.db_pool = await open_db_pool(CONFIG.get('dns'))


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
            user = await fetch_user(email)
            if user is None:
                user = await User.new_user(email=email, password=form.password.data)
                login_user(request, user)
                return template('home.html', user=get_user(request))
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
            hashed_pw = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt', 20000)
            hashed_pw = (binascii.hexlify(hashed_pw)).decode('utf-8')
            user = await fetch_user(email=email)
            if user is not None:
                if dict(await fetch_row('SELECT * FROM details WHERE email=$1', user.email))['password'] == hashed_pw:
                    login_user(request,user)
                    return template('home.html', user=get_user(request))
            form.email.errors.append('Incorrect username or password')
        return template('login.html', form=form)
    return template('login.html', form=LoginForm())


def login_user(request, user):
    if request['session'].get('logged_in', False):
        return template('home.html', user=user)
    request['session']['logged_in'] = True
    request['session']['user'] = user

def get_user(request):
    return request['session']['user']


def get_stack_variable(name):
    stack = inspect.stack()
    try:
        for frames in stack:
            try:
                frame = frames[0]
                current_locals = frame.f_locals
                if name in current_locals:
                    return current_locals[name]
            finally:
                del frame
    finally:
        del stack
    
@app.route('/')
async def home(request):
    return text('hi')


