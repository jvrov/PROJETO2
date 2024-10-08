from flask.views import MethodView
from flask import Flask, render_template, redirect, url_for, flash
import pymysql
from flask import session, url_for, flash
from flask import Flask, render_template, request

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
        bet_name = request.form.get('bet_name')
        bet_value = request.form.get('bet_value')

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'  
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO bets (name, value) VALUES (%s, %s)",
                    (bet_name, bet_value)
                )
                connection.commit()  
            flash('Aposta criada com sucesso!', 'success')  
            return redirect(url_for('home'))  
        except Exception as e:
            flash('Ocorreu um erro ao criar a aposta: {}'.format(str(e)), 'danger')
            return redirect(url_for('create_bet'))  

        finally:
            connection.close()  


class LogoutController(MethodView):
    def get(self):
        session.pop('user_id', None)  
        flash('Você saiu com sucesso.')
        return redirect(url_for('login'))  