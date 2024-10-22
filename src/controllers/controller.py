from flask.views import MethodView
from flask import Flask, render_template, redirect, url_for, flash, request, session
import pymysql
import random
from decimal import Decimal



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


        print("Dados recebidos:", username, email, password, birthdate)  

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
                print("Inserindo novo usuárioaa")  
                if existing_user:
                    flash('Usuário já existe.', 'danger')
                    return redirect(url_for('register'))

                print("Inserindo novo usuário")  

                cursor.execute(
                    "INSERT INTO users (username, email, password, birthdate) VALUES (%s, %s, %s, %s)",
                    (username, email, password, birthdate)
                )
                connection.commit()
                flash('Cadastro bem-sucedido!', 'success')
                return redirect(url_for('confirmation'))

        except Exception as e:
            print(f'Ocorreu um erro: {str(e)}')  
            flash(f'Ocorreu um erro: {str(e)}', 'danger')
            return redirect(url_for('register'))

        finally:
            connection.close()

            
class LoginController(MethodView):
    def get(self):
        print("GET request recebido na rota /login")
        return render_template('public/login.html')

    def post(self):
        print("POST request recebido na rota /login")

        # Pegar os dados do formulário
        email = request.form['email']
        password = request.form['password']
        print(f"Email recebido: {email}")
        print(f"Senha recebida: {password}")

        # Conexão com o banco de dados
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro'
            )
            print("Conexão com o banco de dados estabelecida com sucesso.")
        except Exception as e:
            print(f"Erro ao conectar com o banco de dados: {e}")
            flash('Erro ao conectar com o banco de dados.', 'danger')
            return redirect(url_for('login'))

        try:
            with connection.cursor() as cursor:
                # Verifica se o email e a senha correspondem
                print("Executando query para verificar email e senha...")
                cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
                user = cursor.fetchone()
                print(f"Resultado da consulta SQL: {user}")

        except Exception as e:
            print(f"Erro ao executar a consulta SQL: {e}")
            flash('Erro ao realizar a verificação do login.', 'danger')
            return redirect(url_for('login'))
        finally:
            connection.close()

        # Verificação do login
        # Verificação do login
        if user:
            print("Usuário encontrado no banco de dados.")
            session['user_id'] = user[0]  # Guarda o ID do usuário na sessão
            session['username'] = user[1]  # Guarda o nome do usuário na sessão
            print(f"ID do usuário salvo na sessão: {user[0]}")
            print(f"Nome do usuário salvo na sessão: {user[1]}")  # Debug

            is_admin = user[-1]  # Assumindo que 'is_admin' é a última coluna
            print(f"Valor de is_admin: {is_admin}")

            # Verifica se o usuário é administrador
            if is_admin == 1:
                session['is_admin'] = True
                print("Usuário é administrador. Redirecionando para admin_dashboard...")
                flash('Bem-vindo, administrador!', 'success')
                return redirect(url_for('admin_dashboard'))  # Redireciona para o dashboard de admin
            else:
                session['is_admin'] = False
                print("Usuário não é administrador. Redirecionando para confirmationlogin...")
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('confirmationlogin'))  # Redireciona para a página de usuário comum
        else:
            print("Usuário não encontrado no banco de dados. Login falhou.")
            flash('Email ou senha incorretos.', 'danger')
            return redirect(url_for('login'))


class AdminDashboardController(MethodView):
    def get(self):
        # Verifica se o usuário está logado e se é um administrador
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar essa página.', 'danger')
            return redirect(url_for('login'))

        # Verifica se o usuário é um administrador (assumindo que 'is_admin' esteja na sessão ou no banco de dados)
        if session.get('is_admin') == True:
            return render_template('public/dashboard.html')  # Renderiza a página do dashboard de admin
        else:
            flash('Acesso negado! Somente administradores podem acessar esta página.', 'danger')
            return redirect(url_for('home'))


class EventosAgoraController(MethodView):
    def get(self):
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

            if not events:
                flash('Nenhum evento encontrado.', 'info')  # Mensagem se não houver eventos
            
        except Exception as e:
            flash(f'Ocorreu um erro ao buscar eventos: {str(e)}', 'danger')  # Mensagem de erro
            return redirect(url_for('home'))  # Redireciona para a página inicial
        finally:
            connection.close()  # Fecha a conexão com o banco de dados

        return render_template('public/eventosagora.html', events=events)

class DeleteEventController(MethodView):
    def post(self, event_id):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                # Primeiro, exclua as participações associadas ao evento
                cursor.execute("DELETE FROM participacoes WHERE event_id = %s", (event_id,))
                
                # Depois, exclua o evento
                cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
                connection.commit()  # Salva as alterações no banco de dados

            flash('Evento excluído com sucesso!', 'success')
        except Exception as e:
            flash(f'Ocorreu um erro ao excluir o evento: {str(e)}', 'danger')
        finally:
            connection.close()  # Fecha a conexão com o banco de dados

        return redirect(url_for('eventosagora'))  # Redireciona para a lista de eventos

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
        print("Iniciando renderização da página home")
        
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro'
            )
            print("Conexão com o banco de dados bem-sucedida.")
        except Exception as e:
            print(f"Erro ao conectar com o banco de dados: {str(e)}")
            flash(f"Erro ao conectar com o banco de dados: {str(e)}", "danger")
            return redirect(url_for('login'))

        try:
            with connection.cursor() as cursor:
                print("Executando consulta para eventos próximos de vencer...")
                cursor.execute("SELECT * FROM events WHERE fim_apostas > NOW() ORDER BY fim_apostas ASC LIMIT 5")
                eventos_vencendo = cursor.fetchall()
                print(f"Eventos próximos de vencer retornados: {eventos_vencendo}")

                print("Executando consulta para eventos mais apostados...")
                cursor.execute("SELECT * FROM events ORDER BY num_apostas DESC LIMIT 5")
                eventos_mais_apostados = cursor.fetchall()
                print(f"Eventos mais apostados retornados: {eventos_mais_apostados}")

            # Categorias automáticas
            categorias = ['Olimpíada', 'Catástrofes', 'Eleições', 'Bolsa de Valores']
            print(f"Categorias: {categorias}")

            return render_template('public/home.html',
                                   eventos_vencendo=eventos_vencendo,
                                   eventos_mais_apostados=eventos_mais_apostados,
                                   categorias=categorias)

        except Exception as e:
            print(f"Ocorreu um erro ao carregar a página inicial: {str(e)}")
            flash(f"Ocorreu um erro ao carregar a página inicial: {str(e)}", "danger")
            return redirect(url_for('login'))

        finally:
            try:
                connection.close()
                print("Conexão com o banco de dados fechada.")
            except Exception as e:
                print(f"Erro ao fechar a conexão com o banco de dados: {str(e)}")


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

            if not events:
                flash('Nenhum evento encontrado.', 'info')  # Mensagem se não houver eventos
            
            
        except Exception as e:
            flash(f'Ocorreu um erro ao buscar eventos: {str(e)}', 'danger')  # Mensagem de erro
            
            return redirect(url_for('home'))  # Redireciona para a página inicial

        finally:
            connection.close()  # Fecha a conexão com o banco de dados

      
        return render_template('public/listar_eventos.html', events = events)  


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
                cursor.execute("SELECT wallet, username FROM users WHERE id = %s", (user_id,))
                user_info = cursor.fetchone()

                if user_info:
                    wallet_value = float(user_info[0])  # Converte o valor da wallet para float
                    username = user_info[1]  # Nome do usuário
                else:
                    wallet_value = 0.0
                    username = "Usuário não encontrado"

            return render_template('public/wallet.html', wallet=wallet_value, username=username)

        except Exception as e:
            flash(f'Ocorreu um erro ao acessar a wallet: {str(e)}', 'danger')
            return redirect(url_for('home'))

        finally:
            connection.close()


class DepositController(MethodView):
    def get(self, user_id):
        return render_template('public/deposito.html', user_id=user_id)

    def post(self, user_id):
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
                current_wallet = float(current_wallet)  # passa para float

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
                

                new_wallet_balance = current_wallet - withdraw_amount

                if new_wallet_balance < 0:
                    flash('O saque não pode ser realizado, saldo insuficiente.', 'danger')
                    return redirect(url_for('sacar', user_id=user_id))

                try:
                    cursor.execute("UPDATE users SET wallet = %s WHERE id = %s", (new_wallet_balance, user_id))
                    connection.commit()
                    print("Saldo atualizado com sucesso.")  # Debug: Saldo atualizado
                except Exception as update_error:
                    flash('Ocorreu um erro ao tentar atualizar o saldo.', 'danger')
                    return redirect(url_for('home'))

                amount_received = withdraw_amount - taxa

                flash('Saque realizado com sucesso!', 'success')
                return render_template('public/sacar.html', user_id=user_id, amount_received=amount_received, withdraw_amount=withdraw_amount)

        except Exception as e:
            print(f"Erro no processo de saque: {str(e)}")  # Debug: erro genérico
            flash(f'Ocorreu um erro ao realizar o saque: {str(e)}', 'danger')
            return render_template('public/sacar.html', user_id=user_id, withdraw_amount=withdraw_amount)

        finally:
            connection.close()

class ParticipateController(MethodView):
    def post(self, event_id):
        # ve se o usuário está logado
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
                # ve se o usuário já participou do evento
                cursor.execute("SELECT * FROM participacoes WHERE user_id = %s AND event_id = %s", (user_id, event_id))
                participation = cursor.fetchone()

                if participation:
                    flash('Você já está participando deste evento.', 'warning')
                else:
                    # ve o valor da cota do evento
                    cursor.execute("SELECT value FROM events WHERE id = %s", (event_id,))
                    event = cursor.fetchone()

                    if event is None:
                        flash('Evento não encontrado.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    event_value = float(event[0])  # passa para float

                    # ve o saldo do usuário
                    cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
                    current_wallet = cursor.fetchone()[0]
                    current_wallet = float(current_wallet)  # passa para float

                    # ve se paga
                    if event_value > current_wallet:
                        flash('Saldo insuficiente. Faça um crédito na sua carteira.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    # Att o saldo do usuário
                    new_wallet_balance = current_wallet - event_value
                    cursor.execute("UPDATE users SET wallet = %s WHERE id = %s", (new_wallet_balance, user_id))
                    connection.commit()

                    
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
        user_id = session.get('user_id')  
        
        if user_id:
            
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro'
            )
            cursor = connection.cursor()

            query = """
                SELECT e.id, e.titulo, e.descricao, e.valor_cota, e.inicio_apostas, e.fim_apostas, e.data_evento
                FROM events e
                JOIN participacoes p ON e.id = p.event_id
                WHERE p.user_id = %s
            """
            cursor.execute(query, (user_id,))
            meus_eventos = cursor.fetchall()  # Recupera todos os eventos
            cursor.close()
            connection.close()  
            
            return render_template('public/meus_eventos.html', meus_eventos=meus_eventos)
        else:
            return redirect(url_for('home'))
        
        
class ParticipateController(MethodView):
    def post(self, event_id):
        
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
         
                cursor.execute("SELECT * FROM participacoes WHERE user_id = %s AND event_id = %s", (user_id, event_id))
                participation = cursor.fetchone()

                if participation:
                    flash('Você já está participando deste evento.', 'warning')
                else:
                    
                    cursor.execute("SELECT valor_cota FROM events WHERE id = %s", (event_id,))
                    event = cursor.fetchone()

                    if event:
                        valor_cota = event[0]  # Corrigido para usar índice 0
                        print(f"Valor da cota: {valor_cota}")

                        # ve o saldo da wallet do usuário
                        cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
                        user_wallet = cursor.fetchone()
                        print(f"Wallet do usuário: {user_wallet}")

                        if user_wallet:
                            if user_wallet[0] >= valor_cota:  # acesso correto ao saldo da wallet
                                
                                novo_saldo = user_wallet[0] - valor_cota
                                cursor.execute("UPDATE users SET wallet = %s WHERE id = %s", (novo_saldo, user_id))
                                connection.commit()  # confirma a transação
                            
                                cursor.execute("INSERT INTO participacoes (user_id, event_id, data_participacao) VALUES (%s, %s, NOW())", (user_id, event_id))
                                connection.commit()  
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
            connection.close()  
            print("Conexão fechada.")

    def realizar_sorteio(self, event_id):
        connection = pymysql.connect(host='localhost', user='root', password='', db='db_cadastro')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id FROM apostas WHERE event_id = %s", (event_id,))
                participantes = cursor.fetchall()
                
                if participantes:
                    # pega um dos jogadores aleatoriamente
                    ganhador = random.choice(participantes)
                    flash(f'O ganhador do evento {event_id} é o usuário {ganhador["user_id"]}!', 'success')
                else:
                    flash('Nenhum participante para sortear.', 'warning')
        finally:
            connection.close()

class JogoController(MethodView):
    def get(self):
        return render_template('public/jogo.html')

    def post(self):
        # Obtendo o user_id da sessão
        user_id = session.get('user_id')
        
        # Verifica se o usuário está logado
        if user_id is None:
            flash('Você precisa estar logado para apostar.', 'danger')
            return redirect(url_for('login'))  # Redirecione para a página de login

        numero_apostado = int(request.form['numero_apostado'])
        valor_apostado = Decimal(request.form['valor_apostado'])

        print(f"Usuário: {user_id}, Número apostado: {numero_apostado}, Valor apostado: {valor_apostado}")

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                
                numero_sortiado = random.randint(1, 6)
                print(f"Número sorteado: {numero_sortiado}")

                # Verifica se o jogador ganhou
                if numero_apostado == numero_sortiado:
                    valor_final = valor_apostado * 3
                    resultado = 'ganhou'
                    mensagem_resultado = f'Parabéns! Você acertou! O número foi {numero_sortiado} e você ganhou R${valor_final:.2f}!'
                else:
                    valor_final = Decimal(0)
                    resultado = 'perdeu'
                    mensagem_resultado = f'Que pena! O número sorteado foi {numero_sortiado}. Você perdeu R${valor_apostado:.2f}.'

                cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
                saldo_atual = cursor.fetchone()[0]
                print(f"Saldo atual do usuário: {saldo_atual}")

                if saldo_atual < valor_apostado:
                    flash('Saldo insuficiente para apostar.', 'danger')
                    print("Saldo insuficiente.")
                    return redirect(url_for('jogo'))

                novo_saldo = saldo_atual - valor_apostado + valor_final
                print(f"Novo saldo calculado: {novo_saldo}")

                cursor.execute("UPDATE users SET wallet = %s WHERE id = %s", (novo_saldo, user_id))

                cursor.execute(""" 
                    INSERT INTO bets (user_id, valor_apostado, numero_apostado, numero_sortiado, resultado, valor_final)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, valor_apostado, numero_apostado, numero_sortiado, resultado, valor_final))

                connection.commit()
                print("Aposta registrada com sucesso.")

            return render_template('public/jogo.html', numero_sortiado=numero_sortiado, mensagem_resultado=mensagem_resultado)

        except Exception as e:
            flash(f'Ocorreu um erro: {str(e)}', 'danger')
            print(f"Erro: {str(e)}")
            return redirect(url_for('jogo'))

        finally:
            connection.close()
            print("Conexão com o banco de dados fechada.")


class JogoCorController(MethodView):
    def get(self):
        return render_template('public/jogo_cor.html')

    def post(self):
        user_id = session.get('user_id')  # Obtém o ID do usuário logado

        if user_id is None:
            flash('Você precisa estar logado para apostar.', 'danger')
            return redirect(url_for('login'))

        cor_apostada = request.form['cor_apostada']
        valor_apostado = Decimal(request.form['valor_apostado'])

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                # Números de 0 a 30
                numero_sorteado = random.randint(0, 30)

                # Determina a cor do número sorteado
                if numero_sorteado == 0:
                    cor_sorteada = 'verde'
                    valor_final = valor_apostado * 14
                    mensagem_resultado = f'Você apostou no {cor_apostada}. A cor sorteada foi {cor_sorteada}. Você ganhou R${valor_final:.2f}!'
                elif numero_sorteado % 2 == 0:
                    cor_sorteada = 'preto'
                    if cor_apostada == cor_sorteada:
                        valor_final = valor_apostado * 2
                        mensagem_resultado = f'Você apostou no {cor_apostada}. A cor sorteada foi {cor_sorteada}. Você ganhou R${valor_final:.2f}!'
                    else:
                        valor_final = 0
                        mensagem_resultado = f'Você apostou no {cor_apostada}. A cor sorteada foi {cor_sorteada}. Você perdeu R${valor_apostado:.2f}.'
                else:
                    cor_sorteada = 'vermelho'
                    if cor_apostada == cor_sorteada:
                        valor_final = valor_apostado * 2
                        mensagem_resultado = f'Você apostou no {cor_apostada}. A cor sorteada foi {cor_sorteada}. Você ganhou R${valor_final:.2f}!'
                    else:
                        valor_final = 0
                        mensagem_resultado = f'Você apostou no {cor_apostada}. A cor sorteada foi {cor_sorteada}. Você perdeu R${valor_apostado:.2f}.'

                # Obter o saldo atual do usuário
                cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
                saldo_atual = cursor.fetchone()

                if saldo_atual is None:
                    flash('Usuário não encontrado.', 'danger')
                    return redirect(url_for('jogo_cor'))

                saldo_atual = saldo_atual[0]

                if saldo_atual < valor_apostado:
                    flash('Saldo insuficiente para apostar.', 'danger')
                    return redirect(url_for('jogo_cor'))

                novo_saldo = saldo_atual - valor_apostado + valor_final

                # Atualizar o saldo do usuário no banco de dados
                cursor.execute("UPDATE users SET wallet = %s WHERE id = %s", (novo_saldo, user_id))

                # Registrar a aposta na nova tabela
                cursor.execute("""
                    INSERT INTO color_bets (user_id, valor_apostado, cor_apostada, numero_sorteado, cor, valor_final)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, valor_apostado, cor_apostada, numero_sorteado, cor_sorteada, valor_final))

                connection.commit()

            # Passa as variáveis necessárias para o template
            return render_template(
                'public/jogo_cor.html',
                cor_sorteada=cor_sorteada,
                mensagem_resultado=mensagem_resultado,
                saldo_atual=novo_saldo,
                mensagens=[mensagem_resultado]  # Adiciona a mensagem ao contexto
            )

        except Exception as e:
            flash(f'Ocorreu um erro: {str(e)}', 'danger')
            return redirect(url_for('jogo_cor'))

        finally:
            connection.close()


class ListarUsuariosController(MethodView):
    def get(self):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, email, birthdate FROM users WHERE is_admin != 1")
                usuarios = cursor.fetchall()
        finally:
            connection.close()

        return render_template('public/listar_usuarios.html', usuarios=usuarios) 
    

class UserProfileController(MethodView):
    def get(self):
        user_id = session.get('user_id')  # Obtém o ID do usuário logado
        print(f"ID do usuário obtido da sessão: {user_id}")

        if user_id is None:
            flash('Você precisa estar logado para acessar o perfil.', 'danger')
            return redirect(url_for('login'))

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )
        print("Conexão com o banco de dados estabelecida.")

        try:
            with connection.cursor() as cursor:
                # Buscar informações do usuário
                print(f"Buscando informações do usuário com ID: {user_id}")
                cursor.execute("SELECT username, email, birthdate, wallet FROM users WHERE id = %s", (user_id,))
                user_info = cursor.fetchone()
                print(f"Informações do usuário: {user_info}")

                if not user_info:
                    flash('Usuário não encontrado.', 'danger')
                    return redirect(url_for('home'))

            print("Renderizando o template profile.html")
            return render_template('public/profile.html', user_info=user_info)

        except Exception as e:
            print(f"Erro ao carregar o perfil: {str(e)}")
            flash(f'Ocorreu um erro ao carregar o perfil: {str(e)}', 'danger')
            return redirect(url_for('home'))

        finally:
            connection.close()
            print("Conexão com o banco de dados fechada.")
