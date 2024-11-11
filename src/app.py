from flask import Flask
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
    UserProfileController,
    ModeratorDashboardController,
    EventApprovalController
)

app = Flask(__name__)
app.secret_key = '1234'

# rotas
app.add_url_rule('/', view_func=OlaController.as_view('ola_controller'))
app.add_url_rule('/register', view_func=RegisterController.as_view('register'))
app.add_url_rule('/login', view_func=LoginController.as_view('login'))
app.add_url_rule('/confirmation', view_func=ConfirmationController.as_view('confirmation'))
app.add_url_rule('/confirmationlogin', view_func=LoginConfirmationController.as_view('confirmationlogin'))
app.add_url_rule('/home', view_func=HomeController.as_view('home'))
app.add_url_rule('/logout', view_func=LogoutController.as_view('logout'))
app.add_url_rule('/create_bet', view_func=CreateBetController.as_view('create_bet'))
app.add_url_rule('/listar_eventos', view_func=ListEventsController.as_view('listar_eventos'))
app.add_url_rule('/listar_bets', view_func=ListBetsController.as_view('listar_bets'))
app.add_url_rule('/deposito/<int:user_id>', view_func=DepositController.as_view('deposito'))
app.add_url_rule('/realizar_deposito/<int:user_id>', view_func=WalletController.as_view('realizar_deposito'), methods=['POST'])
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
app.add_url_rule('/moderator/dashboard', view_func=ModeratorDashboardController.as_view('moderator_dashboard'))
app.add_url_rule('/moderator_action/<int:participacao_id>/<action>', view_func=ModeratorDashboardController.as_view('moderator_dashboard_action'))
app.add_url_rule('/moderator/approve_event/<int:event_id>', view_func=EventApprovalController.as_view('approve_event'), methods=['POST'])  # Controller para aprovação de eventos
app.add_url_rule('/moderator/reject_event/<int:event_id>', view_func=EventApprovalController.as_view('reject_event'), methods=['POST'])  # Controller para rejeição de eventos

if __name__ == '__main__':
    app.run(debug=True)
