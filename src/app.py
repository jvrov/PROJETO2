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
    ListBetsController,
    WalletController,
    DepositController,
    WithdrawController,
    ParticipateController,
    MeusEventosController,
    JogoController,
    JogoCorController,
    AdminDashboardController,
    EventosAgoraController,
    DeleteEventController,
    ListarUsuariosController,
    UserProfileController
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
app.add_url_rule('/deposito/<int:user_id>', view_func=DepositController.as_view('deposito'))  # Rota para a página de depósito
app.add_url_rule('/realizar_deposito/<int:user_id>', view_func=WalletController.as_view('realizar_deposito'), methods=['POST'])  # Rota para processar o depósito
app.add_url_rule('/sacar/<int:user_id>', view_func=WithdrawController.as_view('sacar'))
app.add_url_rule('/participate/<int:event_id>', view_func=ParticipateController.as_view('participate_event'))
app.add_url_rule('/meus_eventos', view_func=MeusEventosController.as_view('meus_eventos'))
app.add_url_rule('/wallet/<int:user_id>', view_func=WalletController.as_view('wallet'))
app.add_url_rule('/jogo', view_func=JogoController.as_view('jogo'))
app.add_url_rule('/jogo_cor', view_func=JogoCorController.as_view('jogo_cor'))
app.add_url_rule('/admin_dashboard', view_func=AdminDashboardController.as_view('admin_dashboard'))
app.add_url_rule('/eventosagora', view_func=EventosAgoraController.as_view('eventosagora'))
app.add_url_rule('/delete_event/<int:event_id>', view_func=DeleteEventController.as_view('delete_event'))
app.add_url_rule('/listar_usuarios', view_func=ListarUsuariosController.as_view('listar_usuarios'))
app.add_url_rule('/profile', view_func=UserProfileController.as_view('user_profile'))




if __name__ == '__main__':
    app.run(debug=True)
