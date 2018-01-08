from datetime import datetime
from sanic import Sanic
from sanic.response import html, text, json, HTTPResponse
from sanic_wtf import SanicForm
from jinja2 import Environment, PackageLoader
from sanic.views import HTTPMethodView
import os
from sanic_session import InMemorySessionInterface
import motor.motor_asyncio
import aiohttp
from forms import SignUpForm
app = Sanic(__name__)
<<<<<<< HEAD
=======
#STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://oommenb:<password>@smarthas-shard-00-00-mxxin.mongodb.net:27017,smarthas-shard-00-01-mxxin.mongodb.net:27017,smarthas-shard-00-02-mxxin.mongodb.net:27017/test?ssl=true&replicaSet=SmartHAS-shard-0&authSource=admin')
db = client.user_details
>>>>>>> 415d0d90bfeb57c6aeef4cafafab14cb1740a403

app.config['SECRET_KEY'] = 'top secret !!!'

env = Environment(loader=PackageLoader('app', 'templates'))
session_interface = InMemorySessionInterface()
connection_string = open('connection_string.txt').read()
app.static('/static', './static')

@app.listener('before_server_start')
async def server_begin(app, loop):
    app.session = aiohttp.ClientSession(loop=loop)
    motor_client = motor.motor_asyncio.AsyncIOMotorClient(str(connection_string).strip('\n'))
    app.db.user_details.insert_one({'user':'details'})

@app.listener('after_server_stop')
async def server_end(app, loop):
    app.session.close()

@app.middleware('request')
async def add_session_to_request(request):
    await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
    await session_interface.save(request, response)

def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))

class LoginView(HTTPMethodView):
    async def get(self, request):
        return template('login.html')

app.add_route(LoginView.as_view(), '/login')

class SignUpView(HTTPMethodView):
    async def get(self, request):
        form = SignUpForm()
        return template('signup.html', form=form)

    async def post(self, request):
        email = request.form.get('Email')
        data = await app.db.user_details.find_one({"Email":email})
        if not data:
            await app.db.user_details.update_one({'user':'details'}, {'$set': {'Email':email}}, upsert=True)
            return redirect('/')
        return text(request.form.get('Email'))
        
app.add_route(SignUpView.as_view(), '/signup')

@app.route('/')
async def home(request):
    return text('hi')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
