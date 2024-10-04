from flask.views import MethodView
from flask import render_template, request, redirect, url_for, flash
from src.db import mysql
import pymysql



class OlaController(MethodView):
    def get(self):
        return render_template('public/index.html')  # Retorna a tela inicial

from flask import request, render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash
import pymysql
from flask.views import MethodView

class RegisterController(MethodView):
    def get(self):
        return render_template('public/register.html')  # Retorna o template de registro

    def post(self):
        username = request.form['username']  # Verifique se 'username' está presente
        password = request.form['password']  # Verifique se 'password' está presente



class LoginController(MethodView):
    def get(self):
        return render_template('public/login.html')  # Retorna o template de login

    def post(self):
        username = request.form['username']
        password = request.form['password']
        
        # Conexão com o banco de dados
        connection = pymysql.connect(
            host='localhost',
            user='seu_usuario',  # Substitua pelo seu nome de usuário
            password='sua_senha',  # Substitua pela sua senha
            db='db_cadastro'  # Nome do banco de dados
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
        
        if user:
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('ola_controller'))  # Redireciona para a tela inicial
        else:
            flash('Nome de usuário ou senha incorretos.', 'danger')
            return redirect(url_for('login'))  # Redireciona de volta para a tela de login


class ConfirmationController(MethodView):
    def get(self):
        return render_template('public/confirmation.html')  # Retorna o template de confirmação
