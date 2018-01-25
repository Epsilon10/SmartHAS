from sanic import Sanic
import logging
app = Sanic(__name__)
from app import views