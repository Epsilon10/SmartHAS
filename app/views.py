from datetime import datetime
from sanic import Sanic, response
from sanic.response import html, text, json, HTTPResponse
from sanic_wtf import SanicForm
from jinja2 import Environment, PackageLoader
from sanic.views import HTTPMethodView
import os
from sanic_session import InMemorySessionInterface
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
from app.forms import SignUpForm
from pprint import pprint
from app.models import open_db, unique_db
from app import app
import asyncio

app.config['SECRET_KEY'] = 'top secret !!!'

env = Environment(loader=PackageLoader('app', 'templates'))
session_interface = InMemorySessionInterface()
app.static('/static', './app/static')

def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))

@app.listener('before_server_start')
async def server_begin(app, loop):
    app.session = aiohttp.ClientSession(loop=loop)
    await open_db('127.0.0.1',27017)


@app.listener('after_server_stop')
async def server_end(app, loop):
    app.session.close()

@app.middleware('request')
async def add_session_to_request(request):
    await session_interface.open(request)

@app.middleware('response')
async def save_session(request, response):
    await session_interface.save(request, response)


class LoginView(HTTPMethodView):
    async def get(self, request):
        return template('login.html')

app.add_route(LoginView.as_view(), '/login')

'''
class SignUpView(HTTPMethodView):
    async def get(self, request):
        form = SignUpForm()
        return template('signup.html', form=form)

    async def post(self, request):
        form = SignUpForm(request)
        email = form.email.data
        print(email)
        email_exists = await unique_db(email)
        print(form.errors)
        print ('Form validated: {}, Email Exists: {}'.format(form.validate_on_submit(), email_exists))
        if form.validate_on_submit() and email_exists == False:
            print('Validated')
            await app.db.user_details.update_one({'user':'details'},{'$set': data}, upsert=True)
            return json({'success':True})
        return template('signup.html', form=form)
        
app.add_route(SignUpView.as_view(), '/signup')
'''
@app.route('/signup', methods=['GET', 'POST'])
async def _signup(request):
    form = SignUpForm(request.form)
    if request.method == 'POST':
        print(form.errors)
        if form.validate():
            email = form.email.data
            email_exists = await unique_db(email)
            return json({'success':'true'})
        return template('signup.html', form=form)
    return template('signup.html', form=SignUpForm())

@app.route('/')
async def home(request):
    return text('hi')

