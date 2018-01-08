from datetime import datetime
from sanic import Sanic
from sanic.response import html, text, json, HTTPResponse
from sanic_wtf import SanicForm
from jinja2 import Environment, PackageLoader
from sanic.views import HTTPMethodView
import os
from sanic_session import InMemorySessionInterface
import motor.motor_asyncio

app = Sanic(__name__)
#STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://oommenb:Manny12345@smarthas-shard-00-00-mxxin.mongodb.net:27017,smarthas-shard-00-01-mxxin.mongodb.net:27017,smarthas-shard-00-02-mxxin.mongodb.net:27017/test?ssl=true&replicaSet=SmartHAS-shard-0&authSource=admin')
db = client.user_details

app.config['SECRET_KEY'] = 'top secret !!!'

env = Environment(loader=PackageLoader('app', 'templates'))
session_interface = InMemorySessionInterface()

app.static('/static', './static')

@app.middleware('request')
async def add_session_to_request(request):
        # before each request initialize a session
        # using the client's request
    await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
        # after each request save the session,
        # pass the response to set client cookies
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
        return template('signup.html')

    async def post(self, request):
        
        

app.add_route(SignUpView.as_view(), '/signup')

@app.route('/')
async def home(request):
    return text('hi')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)