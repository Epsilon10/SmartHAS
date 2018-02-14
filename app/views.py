import datetime

## Sanic imports ##
from sanic import Sanic, response
from sanic.response import html, text, json, HTTPResponse, redirect
from sanic.exceptions import SanicException
from jinja2 import Environment, PackageLoader

## app imports ##
from app import app
from app.forms import SignUpForm, LoginForm
from app.models import open_db_pool, fetch_row, fetch_val, fetch_many, execute_job, User, fetch_user, Redis

## external imports ##
from app.redis_session_interface import MyRedisInterface
import os
import aiohttp
import asyncio
import logging
import inspect
import ujson
import hashlib, binascii
import discord
from functools import wraps
import time

################
## app config ##
################

redis = Redis()

app.config['SECRET_KEY'] = 'top secret !!!'
env = Environment(loader=PackageLoader('app', 'templates'))
session_interface = MyRedisInterface(redis.get_redis_pool, expiry=604800)
app.static('/static', './app/static')
app.config.AUTH_LOGIN_ENDPOINT = 'login'

show_deploy = False




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

##############################################
## app middleware for server backed session ##
##############################################

@app.listener('before_server_start')
async def server_begin(app, loop):
    app.session = aiohttp.ClientSession(loop=loop)
    app.db_pool = await open_db_pool(CONFIG.get('dns'))
    #app.device_pool = 
    app.redis_pool = await redis.get_redis_pool()
    app.webhook_url = CONFIG.get('webhook_url')
    if app.webhook_url and show_deploy:
        await app.session.post(app.webhook_url, json=format_embed())


@app.listener('after_server_stop')
async def server_end(app, loop):
    await app.db_pool.close()
    app.redis_pool.close()
    await app.redis_pool.wait_closed()
    app.session.close()

@app.middleware('request')
async def add_session_to_request(request):
    await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
    await session_interface.save(request, response)

###################
## routes/views ##
##################

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
                return response.redirect(app.url_for('home'))
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
                    return response.redirect('/home')
            form.email.errors.append('Incorrect username or password')
        return template('login.html', form=form)
    return template('login.html', form=LoginForm())

@app.get('/logout')
async def _logout(request):
    request['session'].clear()
    return text('logged out')

@app.get('/home')
async def home(request):
    return template('home.html', user=get_user(request))

@app.get('/')
# @auth_required()  
async def home(request):
    return text('hi')

####################
## app utilities ##
####################

def auth_required():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authorized = request['session'].get('logged_in', False)
            if is_authorized:
                resp = await f(request, *args, **kwargs)
                return resp
            return response.redirect('/login')
        return decorated_function
    return decorator


def login_user(request, user):
    if request['session'].get('logged_in', False):
        return template('home.html', user=user)
    request['session']['logged_in'] = True
    request['session']['user'] = user

def get_user(request):
    return request['session'].get('user')

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

def format_embed():
    embed = discord.Embed()
    embed.title = "[Success] App has been deployed!"
    embed.color = discord.Color.blue()
    embed.timestamp = datetime.datetime.now()
    embed.description = "[SmartHAS](https://github.com/Epsilon10/SmartHAS)" 
    return {'embeds':[embed.to_dict()]}

  
@app.post('/devicedata')
async def post_handler(request):
    payload = request.json()
    #TODO: validate this payload

    await app.redis_pool.select(1)
    email = payload['email']
    data = payload['data'] 
    await app.redis_pool.set(email,data, expire=86400)
    await app.redis_pool.select(0)
    return response.text(payload)



