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
from forms import SignUpForm
from pprint import pprint
app = Sanic(__name__)

app.config['SECRET_KEY'] = 'top secret !!!'

env = Environment(loader=PackageLoader('app', 'templates'))
session_interface = InMemorySessionInterface()
connection_string = open('connection_string.txt').read()
app.static('/static', './static')

def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))

@app.listener('before_server_start')
async def server_begin(app, loop):
    app.session = aiohttp.ClientSession(loop=loop)
    motor_client = AsyncIOMotorClient(host='127.0.0.1',port=27017)
    app.db = motor_client.smarthas
    print('Connected to MongoDB')

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

class SignUpView(HTTPMethodView):
    async def get(self, request):
        form = SignUpForm()
        return template('signup.html', form=form)

    async def post(self, request):
        data =  {str(request.form.get('email')):{'password':str(request.form.get('password'))}}
        try:
            await app.db.user_details.update_one({'user':'details'},{'$set': data}, upsert=True)
            return json({'success':True})
        except Exception as e:
            return text(str(e))
        
app.add_route(SignUpView.as_view(), '/signup')

@app.route('/')
async def home(request):
    return text('hi')

