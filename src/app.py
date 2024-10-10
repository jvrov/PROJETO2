from flask import Flask, render_template, request, redirect, url_for, flash
from flask.views import MethodView
from src.controllers.controller import (
    OlaController,
    RegisterController,
    LoginController,
    ConfirmationController,
    LoginConfirmationController,
    HomeController,
    LogoutController,
    CreateBetController,
    ListEventsController,
    ListBetsController
)

app = Flask(__name__)
app.secret_key = '1234'

# Rotas e seus controladores
app.add_url_rule('/', view_func=OlaController.as_view('ola_controller'))
app.add_url_rule('/register', view_func=RegisterController.as_view('register'))
app.add_url_rule('/login', view_func=LoginController.as_view('login'))
app.add_url_rule('/confirmation', view_func=ConfirmationController.as_view('confirmation'))
app.add_url_rule('/confirmationlogin', view_func=LoginConfirmationController.as_view('confirmationlogin'))
app.add_url_rule('/home', view_func=HomeController.as_view('home'))
app.add_url_rule('/create_bet', view_func=CreateBetController.as_view('create_bet'))
app.add_url_rule('/logout', view_func=LogoutController.as_view('logout'))
app.add_url_rule('/confirm_bet', view_func=CreateBetController.as_view('confirm_bet'))  # Supondo que você quer usar o mesmo controlador para confirmar a aposta
app.add_url_rule('/listar_eventos', view_func=ListEventsController.as_view('listar_eventos'))
app.add_url_rule('/listar_bets', view_func=ListBetsController.as_view('listar_bets'))  # Corrigido o nome da rota para refletir corretamente o controlador

if __name__ == '__main__':
    app.run(debug=True)
