from flask.views import MethodView
from flask import Flask, render_template, redirect, url_for, flash, request, session
import pymysql


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
                print("Fez conexão")
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

