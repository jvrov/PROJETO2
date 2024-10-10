from flask import Flask
from flask.views import MethodView
from src.controllers.controller import OlaController, RegisterController, LoginController, HomeController,CreateBetController, ListEventsController
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my_bd_aula.sqlite3"

app.secret_key = os.urandom(24)  

app.add_url_rule('/', view_func=OlaController.as_view('index'))  
app.add_url_rule('/register', view_func=RegisterController.as_view('register'))  
app.add_url_rule('/login', view_func=LoginController.as_view('login'))
app.add_url_rule('/home', view_func=HomeController.as_view('home'))
app.add_url_rule('/create_bet', view_func=CreateBetController.as_view('create_bet'))
app.add_url_rule('/listar_eventos', view_func=ListEventsController.as_view('listar_eventos'))


if __name__ == '__main__':
    app.run(debug=True)
