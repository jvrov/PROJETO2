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
    CreateBetController
)

app = Flask(__name__)
app.secret_key = '1234'


routes = {
    "ola_route": "/",
    "olaController": OlaController.as_view('ola_controller'),
    "register_route": "/register",
    "registerController": RegisterController.as_view('register'),
    "login_route": "/login",
    "loginController": LoginController.as_view('login'),
    "confirmation_route": "/confirmation",
    "confirmationController": ConfirmationController.as_view('confirmation'),
    "confirmationlogin_route": "/confirmationlogin",
    "confirmationloginController": LoginConfirmationController.as_view('confirmationlogin'),
    "home_route": "/home",
    "homeController": HomeController.as_view('home'),
    "create_bet_route": "/create_bet", 
    "createBetController": CreateBetController.as_view('create_bet'),
    "logout_route": "/logout", 
    "logoutController": LogoutController.as_view('logout')
}

# rotas
app.add_url_rule(routes["ola_route"], view_func=routes["olaController"])
app.add_url_rule(routes["register_route"], view_func=routes["registerController"])
app.add_url_rule(routes["login_route"], view_func=routes["loginController"])
app.add_url_rule(routes["confirmation_route"], view_func=routes["confirmationController"])
app.add_url_rule(routes["confirmationlogin_route"], view_func=routes["confirmationloginController"])
app.add_url_rule(routes["home_route"], view_func=routes["homeController"])  
app.add_url_rule(routes["create_bet_route"], view_func=routes["createBetController"])  
app.add_url_rule(routes["logout_route"], view_func=routes["logoutController"])  


if __name__ == '__main__':
    app.run(debug=True)
