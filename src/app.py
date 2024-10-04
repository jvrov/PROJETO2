from flask import Flask
from src.controllers.controller import OlaController, RegisterController, LoginController, ConfirmationController

app = Flask(__name__)

# Defina suas rotas
routes = {
    "ola_route": "/",
    "olaController": OlaController.as_view('ola_controller'),
    "register_route": "/register",
    "registerController": RegisterController.as_view('register'),  # Corrigido para usar RegisterController
    "login_route": "/login",
    "loginController": LoginController.as_view('login'),  # Corrigido para usar o LoginController
    "confirmation_route": "/confirmation",
    "confirmationController": ConfirmationController.as_view('confirmation')
}

# Registre as rotas
app.add_url_rule(routes["ola_route"], view_func=routes["olaController"])
app.add_url_rule(routes["register_route"], view_func=routes["registerController"])
app.add_url_rule(routes["login_route"], view_func=routes["loginController"])  # Corrigido para usar login_route
app.add_url_rule(routes["confirmation_route"], view_func=routes["confirmationController"])  # Corrigido para usar confirmationController

if __name__ == '__main__':
    app.run(debug=True)
