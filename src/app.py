from flask import Flask, session, jsonify
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
    HistoricoApostasController,
    DeleteEventController,
    ListarUsuariosController,
    UserProfileController,
    ModeratorDashboardController,
    EventApprovalController,
    BalanceController,
    GetBalanceController,
    SaldoController,
    AprovarParticipacaoController,
    RecusarParticipacaoController
)
from flask_mail import Mail, Message
import os
import pymysql

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'emailapostavip@gmail.com'
app.config['MAIL_PASSWORD'] = 'jxni nfej bano sdgp'
app.config['MAIL_DEFAULT_SENDER'] = 'emailapostavip@gmail.com'

mail = Mail(app)

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
app.add_url_rule('/wallet', view_func=WalletController.as_view('wallet'))
app.add_url_rule('/sacar', view_func=WithdrawController.as_view('sacar'))
app.add_url_rule('/participate/<int:event_id>', view_func=ParticipateController.as_view('participate_event'))
app.add_url_rule('/meus_eventos', view_func=MeusEventosController.as_view('meus_eventos'))
app.add_url_rule('/jogo', view_func=JogoController.as_view('jogo'))
app.add_url_rule('/jogo_cor', view_func=JogoCorController.as_view('jogo_cor'))
app.add_url_rule('/admin_dashboard', view_func=AdminDashboardController.as_view('admin_dashboard'))
app.add_url_rule('/eventosagora', view_func=EventosAgoraController.as_view('eventosagora'))
app.add_url_rule('/delete_event/<int:event_id>', view_func=DeleteEventController.as_view('delete_event'))
app.add_url_rule('/listar_usuarios', view_func=ListarUsuariosController.as_view('listar_usuarios'))
app.add_url_rule('/profile', view_func=UserProfileController.as_view('user_profile'))
app.add_url_rule('/moderator_dashboard', view_func=ModeratorDashboardController.as_view('moderator_dashboard'))
app.add_url_rule('/moderator_action/<int:participacao_id>/<action>', view_func=ModeratorDashboardController.as_view('moderator_dashboard_action'))
app.add_url_rule('/moderator/event/<int:event_id>/<action>', view_func=EventApprovalController.as_view('event_action'), methods=['GET', 'POST'])
app.add_url_rule('/get_balance', view_func=GetBalanceController.as_view('get_balance'))
app.add_url_rule('/get_saldo', view_func=SaldoController.as_view('get_saldo'))
app.add_url_rule('/deposito', view_func=DepositController.as_view('deposito'), methods=['GET', 'POST'])
app.add_url_rule('/event_approval/<int:event_id>/<action>', 
                 view_func=EventApprovalController.as_view('event_approval'),
                 methods=['POST'])
app.add_url_rule('/aprovar_participacao/<int:participacao_id>', 
                 view_func=AprovarParticipacaoController.as_view('aprovar_participacao'),
                 methods=['POST'])
app.add_url_rule('/recusar_participacao/<int:participacao_id>', 
                 view_func=RecusarParticipacaoController.as_view('recusar_participacao'),
                 methods=['POST'])
app.add_url_rule(
    '/get_historico_apostas',
    view_func=HistoricoApostasController.as_view('historico_apostas')
)

# Adicione esta nova rota de teste
@app.route('/test_mail')
def test_mail():
    try:
        msg = Message('Teste de Email',
                     sender='emailapostavip@gmail.com',
                     recipients=['emailapostavip@gmail.com'])
        msg.body = "Este é um email de teste do sistema."
        mail.send(msg)
        return "Email enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar email: {str(e)} \nErro detalhado: {repr(e)}"

if __name__ == '__main__':
    app.run(debug=True)
