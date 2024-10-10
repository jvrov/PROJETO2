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

                if existing_user:
                    flash('Usuário já existe.', 'danger')
                    return redirect(url_for('register'))

                cursor.execute(
                    "INSERT INTO users (username, email, password, birthdate) VALUES (%s, %s, %s, %s)",
                    (username, email, password, birthdate)
                )
                connection.commit()
                flash('Cadastro bem-sucedido!', 'success')
                return redirect(url_for('confirmation'))

        except Exception as e:
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