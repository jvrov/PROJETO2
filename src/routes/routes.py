from flask import Flask
from flask.views import MethodView
from src.controllers.controller import OlaController, register, LoginController

app = Flask(__name__)

app.add_url_rule('/', view_func=OlaController.as_view('index'))  
app.add_url_rule('/register', view_func=register.as_view('register'))  
app.add_url_rule('/login', view_func=LoginController.as_view('login'))
