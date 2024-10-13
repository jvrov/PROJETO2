from flask.views import MethodView
from flask import Flask, render_template, redirect, url_for, flash, request, session
import pymysql
import random


class OlaController(MethodView):
    def get(self):
        return render_template('public/index.html')


class RegisterController(MethodView):
    def get(self):
        return render_template('public/register.html')

    def post(self):
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        birthdate = request.form['birthdate']


        print("Dados recebidos:", username, email, password, birthdate)  # Adicione isto

        if not username or not email or not password or not birthdate:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('register'))

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                existing_user = cursor.fetchone()
                print("Inserindo novo usuárioaa")  # Adicione isto
                if existing_user:
                    flash('Usuário já existe.', 'danger')
                    return redirect(url_for('register'))

                print("Inserindo novo usuário")  # Adicione isto

                cursor.execute(
                    "INSERT INTO users (username, email, password, birthdate) VALUES (%s, %s, %s, %s)",
                    (username, email, password, birthdate)
                )
                connection.commit()
                flash('Cadastro bem-sucedido!', 'success')
                return redirect(url_for('confirmation'))

        except Exception as e:
            print(f'Ocorreu um erro: {str(e)}')  # Adicione isto
            flash(f'Ocorreu um erro: {str(e)}', 'danger')
            return redirect(url_for('register'))

        finally:
            connection.close()



class LoginController(MethodView):
    def get(self):
        return render_template('public/login.html')

    def post(self):
        email = request.form['email']  
        password = request.form['password']

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]  # Armazena o ID do usuário na sessão
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('confirmationlogin')) 
        else:
            flash('Email ou senha incorretos.', 'danger')
            return redirect(url_for('login'))
        



class ConfirmationController(MethodView):
    def get(self):
        return render_template('public/confirmation.html')

class LogoutController(MethodView):
    def get(self):
        session.pop('user_id', None)    
        flash('Você saiu com sucesso.')
        return redirect(url_for('login'))



class LoginConfirmationController(MethodView):
    def get(self):
        return render_template('public/confirmationlogin.html')


class HomeController(MethodView):
    def get(self):
        return render_template('public/home.html')
    def get(self):
        # Simulação de dados de destaque para eventos
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                # Eventos próximos de vencer
                cursor.execute("SELECT * FROM events WHERE fim_apostas > NOW() ORDER BY fim_apostas ASC LIMIT 5")
                eventos_vencendo = cursor.fetchall()

                # Eventos mais apostados (Simulando ranking por número de apostas)
                cursor.execute("SELECT * FROM events ORDER BY num_apostas DESC LIMIT 5")
                eventos_mais_apostados = cursor.fetchall()

            # Categorias automáticas
            categorias = ['Olimpíada', 'Catástrofes', 'Eleições', 'Bolsa de Valores']

            return render_template('public/home.html')

        except Exception as e:
            flash(f'Ocorreu um erro ao carregar a página inicial: {str(e)}', 'danger')
            return redirect(url_for('login'))

        finally:
            connection.close()


class CreateBetController(MethodView):
    def get(self):
        return render_template('public/create_bet.html')

    def post(self):
        title = request.form.get('title')
        description = request.form.get('description')
        bet_value = request.form.get('bet_value')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        event_date = request.form.get('event_date')

        # Validações básicas
        if float(bet_value) < 1.00:
            flash('O valor mínimo da cota é R$ 1,00', 'danger')
            return redirect(url_for('create_bet'))

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                # Inserir o evento na tabela
                cursor.execute("""
                    INSERT INTO events (titulo, descricao, valor_cota, inicio_apostas, fim_apostas, data_evento)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (title, description, bet_value, start_time, end_time, event_date))

                connection.commit()  # Confirma a transação

                flash('Evento criado com sucesso!', 'success')
                return redirect(url_for('home'))

        except Exception as e:
            flash(f'Ocorreu um erro ao criar o evento: {str(e)}', 'danger')
            return redirect(url_for('create_bet'))

        finally:
            connection.close()


class ListBetsController(MethodView):
    def get(self):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT bet_name, bet_value FROM bets")
                bets = cursor.fetchall()
            return render_template('public/listar_evento.html', bets=bets)

        except Exception as e:
            flash(f'Ocorreu um erro ao listar as apostas: {str(e)}', 'danger')
            print(str(e))
            return redirect(url_for('home'))

        finally:
            connection.close()


class ListEventsController(MethodView):
    def get(self):
        # Conexão ao banco de dados
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM events")
                events = cursor.fetchall()  # Recupera todos os eventos

            # Verifica se existem eventos
            if not events:
                flash('Nenhum evento encontrado.', 'info')  # Mensagem se não houver eventos
            
            
        except Exception as e:
            flash(f'Ocorreu um erro ao buscar eventos: {str(e)}', 'danger')  # Mensagem de erro
            
            return redirect(url_for('home'))  # Redireciona para a página inicial

        finally:
            connection.close()  # Fecha a conexão com o banco de dados

      
        return render_template('public/listar_eventos.html', events = events)  # Renderiza a página de listar eventos com os dados


class WalletController(MethodView):
    def get(self, user_id):
        # Conexão com o banco de dados
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                # Consulta para obter o valor da wallet e o nome do usuário
                cursor.execute("SELECT wallet, username FROM users WHERE id = %s", (user_id,))
                user_info = cursor.fetchone()

                # Verifica se o usuário foi encontrado
                if user_info:
                    wallet_value = float(user_info[0])  # Converte o valor da wallet para float
                    username = user_info[1]  # Nome do usuário
                else:
                    wallet_value = 0.0
                    username = "Usuário não encontrado"

            # Renderiza o template com as informações do usuário
            return render_template('public/wallet.html', wallet=wallet_value, username=username)

        except Exception as e:
            flash(f'Ocorreu um erro ao acessar a wallet: {str(e)}', 'danger')
            return redirect(url_for('home'))

        finally:
            connection.close()


class DepositController(MethodView):
    def get(self, user_id):
        # Renderiza a página de depósito
        return render_template('public/deposito.html', user_id=user_id)

    def post(self, user_id):
        # Lógica para adicionar saldo na wallet
        deposit_amount = request.form.get('deposit_amount')

        # Conexão com o banco de dados
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET wallet = wallet + %s WHERE id = %s", (deposit_amount, user_id))
                connection.commit()
                flash('Saldo depositado com sucesso!', 'success')
                return redirect(url_for('wallet', user_id=user_id))

        except Exception as e:
            flash(f'Ocorreu um erro ao depositar: {str(e)}', 'danger')
            return redirect(url_for('home'))

        finally:
            connection.close()

class WithdrawController(MethodView):
    def get(self, user_id):
        # Renderiza a página de saque sem valor sacado
        return render_template('public/sacar.html', user_id=user_id)

    def post(self, user_id):
        withdraw_amount = request.form.get('withdraw_amount')
        print(f"Valor do saque recebido: {withdraw_amount}")  # Debug: Valor recebido

        try:
            withdraw_amount = float(withdraw_amount)
            print(f"Valor do saque convertido para float: {withdraw_amount}")  # Debug: Valor convertido
        except ValueError:
            flash('Valor inválido para saque.', 'danger')
            return redirect(url_for('sacar', user_id=user_id))

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
                current_wallet = cursor.fetchone()[0]
                current_wallet = float(current_wallet)  # Converte para float

                if withdraw_amount > current_wallet:
                    flash('Saldo insuficiente.', 'danger')
                    return redirect(url_for('sacar', user_id=user_id))

                # Cálculo da taxa
                if withdraw_amount <= 100:
                    taxa = withdraw_amount * 0.04
                elif withdraw_amount <= 1000:
                    taxa = withdraw_amount * 0.03
                elif withdraw_amount <= 5000:
                    taxa = withdraw_amount * 0.02
                elif withdraw_amount <= 100000:
                    taxa = withdraw_amount * 0.01
                else:
                    taxa = 0
                

                # O saldo do usuário é reduzido apenas pelo valor do saque
                new_wallet_balance = current_wallet - withdraw_amount

                # Verifica se o saldo após o saque será negativo
                if new_wallet_balance < 0:
                    flash('O saque não pode ser realizado, saldo insuficiente.', 'danger')
                    return redirect(url_for('sacar', user_id=user_id))

                # Atualiza o saldo do usuário
                try:
                    cursor.execute("UPDATE users SET wallet = %s WHERE id = %s", (new_wallet_balance, user_id))
                    connection.commit()
                    print("Saldo atualizado com sucesso.")  # Debug: Saldo atualizado
                except Exception as update_error:
                    flash('Ocorreu um erro ao tentar atualizar o saldo.', 'danger')
                    return redirect(url_for('home'))

                # Aqui, você pode implementar a lógica para transferir o valor sacado menos a taxa para o usuário
                amount_received = withdraw_amount - taxa

                flash('Saque realizado com sucesso!', 'success')
                # Passa o valor recebido para o template
                return render_template('public/sacar.html', user_id=user_id, amount_received=amount_received, withdraw_amount=withdraw_amount)

        except Exception as e:
            print(f"Erro no processo de saque: {str(e)}")  # Debug: erro genérico
            flash(f'Ocorreu um erro ao realizar o saque: {str(e)}', 'danger')
            # Redirecionar para sacar.html com o valor do saque
            return render_template('public/sacar.html', user_id=user_id, withdraw_amount=withdraw_amount)

        finally:
            connection.close()

class ParticipateController(MethodView):
    def post(self, event_id):
        # Verifica se o usuário está logado
        if 'user_id' not in session:
            flash('Você precisa estar logado para participar de um evento.', 'danger')
            return redirect(url_for('login'))

        user_id = session['user_id']

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                # Verifica se o usuário já participou do evento
                cursor.execute("SELECT * FROM participacoes WHERE user_id = %s AND event_id = %s", (user_id, event_id))
                participation = cursor.fetchone()

                if participation:
                    flash('Você já está participando deste evento.', 'warning')
                else:
                    # Verifica o valor da cota do evento
                    cursor.execute("SELECT value FROM events WHERE id = %s", (event_id,))
                    event = cursor.fetchone()

                    if event is None:
                        flash('Evento não encontrado.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    event_value = float(event[0])  # Converte o valor do evento para float

                    # Verifica o saldo atual do usuário
                    cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
                    current_wallet = cursor.fetchone()[0]
                    current_wallet = float(current_wallet)  # Converte para float

                    # Verifica se o usuário tem saldo suficiente
                    if event_value > current_wallet:
                        flash('Saldo insuficiente. Faça um crédito na sua carteira.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    # Atualiza o saldo do usuário
                    new_wallet_balance = current_wallet - event_value
                    cursor.execute("UPDATE users SET wallet = %s WHERE id = %s", (new_wallet_balance, user_id))
                    connection.commit()

                    # Insere a nova participação
                    cursor.execute("INSERT INTO participacoes (user_id, event_id) VALUES (%s, %s)", (user_id, event_id))
                    connection.commit()
                    flash('Você participou do evento com sucesso!', 'success')

                return redirect(url_for('listar_eventos'))

        except Exception as e:
            flash(f'Ocorreu um erro ao participar do evento: {str(e)}', 'danger')
            return redirect(url_for('listar_eventos'))

        finally:
            connection.close()


class MeusEventosController(MethodView):
    def get(self):
        user_id = session.get('user_id')  # Obtém o ID do usuário da sessão
        
        if user_id:
            # Conecte-se ao banco de dados
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro'
            )
            cursor = connection.cursor()

            # Consulta para obter eventos em que o usuário está participando
            query = """
                SELECT e.id, e.titulo, e.descricao, e.valor_cota, e.inicio_apostas, e.fim_apostas, e.data_evento
                FROM events e
                JOIN participacoes p ON e.id = p.event_id
                WHERE p.user_id = %s
            """
            cursor.execute(query, (user_id,))
            meus_eventos = cursor.fetchall()  # Recupera todos os eventos
            cursor.close()
            connection.close()  # Fecha a conexão
            
            return render_template('public/meus_eventos.html', meus_eventos=meus_eventos)
        else:
            return redirect(url_for('home'))
        
        
class ParticipateController(MethodView):
    def post(self, event_id):
        # Verifica se o usuário está logado
        if 'user_id' not in session:
            flash('Você precisa estar logado para participar de um evento.', 'danger')
            print("Usuário não está logado.")
            return redirect(url_for('login'))

        user_id = session['user_id']
        print(f"Usuário ID: {user_id}")

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                # Verifica se o usuário já participou do evento
                cursor.execute("SELECT * FROM participacoes WHERE user_id = %s AND event_id = %s", (user_id, event_id))
                participation = cursor.fetchone()

                if participation:
                    flash('Você já está participando deste evento.', 'warning')
                else:
                    # Obtém o valor da cota do evento
                    cursor.execute("SELECT valor_cota FROM events WHERE id = %s", (event_id,))
                    event = cursor.fetchone()

                    if event:
                        valor_cota = event[0]  # Corrigido para usar índice 0
                        print(f"Valor da cota: {valor_cota}")

                        # Verifica o saldo da wallet do usuário
                        cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
                        user_wallet = cursor.fetchone()
                        print(f"Wallet do usuário: {user_wallet}")

                        if user_wallet:
                            if user_wallet[0] >= valor_cota:  # Acesso correto ao saldo da wallet
                                # Desconta o valor da wallet
                                novo_saldo = user_wallet[0] - valor_cota
                                cursor.execute("UPDATE users SET wallet = %s WHERE id = %s", (novo_saldo, user_id))
                                connection.commit()  # Confirma a transação

                                # Insere a nova participação
                                cursor.execute("INSERT INTO participacoes (user_id, event_id, data_participacao) VALUES (%s, %s, NOW())", (user_id, event_id))
                                connection.commit()  # Confirma a transação
                                flash('Você participou do evento com sucesso!', 'success')
                            else:
                                flash('Saldo insuficiente na wallet para participar deste evento.', 'danger')
                        else:
                            flash('Usuário não encontrado.', 'danger')
                    else:
                        flash('Evento não encontrado.', 'danger')

                return redirect(url_for('listar_eventos'))

        except Exception as e:
            flash(f'Ocorreu um erro ao participar do evento: {str(e)}', 'danger')
            print(f"Erro ao participar do evento: {str(e)}")
            return redirect(url_for('listar_eventos'))

        finally:
            connection.close()  # Fecha a conexão
            print("Conexão fechada.")

    def realizar_sorteio(self, event_id):
        connection = pymysql.connect(host='localhost', user='root', password='', db='db_cadastro')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id FROM apostas WHERE event_id = %s", (event_id,))
                participantes = cursor.fetchall()
                
                if participantes:
                    # Escolher um ganhador aleatoriamente
                    ganhador = random.choice(participantes)
                    flash(f'O ganhador do evento {event_id} é o usuário {ganhador["user_id"]}!', 'success')
                else:
                    flash('Nenhum participante para sortear.', 'warning')
        finally:
            connection.close()
