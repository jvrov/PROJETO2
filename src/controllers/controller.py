from flask.views import MethodView
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, current_app
from werkzeug.security import check_password_hash
import pymysql
import random
from decimal import Decimal
from datetime import datetime
import traceback
from flask_mail import Message


def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='db_cadastro',
        cursorclass=pymysql.cursors.DictCursor
    )

class OlaController(MethodView):
    def get(self):
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = connection.cursor()
            
            # Buscar eventos aprovados
            cursor.execute("""
                SELECT e.*, u.username as organizador
                FROM events e
                JOIN users u ON e.user_id = u.id
                WHERE e.aprovado = 1
                ORDER BY e.data_evento DESC
                LIMIT 5
            """)
            eventos = cursor.fetchall()
            
            # Buscar eventos com mais participações
            cursor.execute("""
                SELECT 
                    e.*,
                    u.username as organizador,
                    COUNT(p.id) as total_participacoes
                FROM events e
                JOIN users u ON e.user_id = u.id
                LEFT JOIN participacoes p ON e.id = p.event_id
                WHERE e.aprovado = 1
                GROUP BY e.id
                ORDER BY total_participacoes DESC
                LIMIT 3
            """)
            eventos_populares = cursor.fetchall()
            
            return render_template('public/index.html', 
                                 eventos=eventos,
                                 eventos_populares=eventos_populares)
            
        except Exception as e:
            print(f"Erro na página inicial: {str(e)}")
            return str(e)
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


class RegisterController(MethodView):
    def get(self):
        return render_template('public/register.html')

    def post(self):
        try:
            # Pegando os dados do formulário incluindo birthdate
            name = request.form['name']
            email = request.form['email']
            birthdate = request.form['birthdate']  # Novo campo
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            # Validações
            if not name or not email or not password or not confirm_password:
                flash('Todos os campos são obrigatórios.')
                return redirect(url_for('register'))

            if password != confirm_password:
                flash('As senhas não coincidem.')
                return redirect(url_for('register'))

            connection = get_db_connection()
            cursor = connection.cursor()

            # Verificar se o email já existe
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            if cursor.fetchone():
                flash('Email já cadastrado.')
                return redirect(url_for('register'))

            # Inserir novo usuário com a data de nascimento
            cursor.execute('''
                INSERT INTO users (
                    username, 
                    email, 
                    password, 
                    birthdate,
                    wallet,
                    is_admin,
                    valor_ganho
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                name,
                email,
                password,
                birthdate,  # Usando a data do formulário
                0.00,
                0,
                0.00
            ))
            
            connection.commit()
            flash('Conta criada com sucesso! Faça login para continuar.')
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Erro no registro: {str(e)}")
            flash('Erro ao criar conta. Tente novamente.')
            return redirect(url_for('register'))

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()


class LoginController(MethodView):
    def get(self):
        return render_template('public/login.html')
        
    def post(self):
        print("\n=== INÍCIO DO LOGIN ===")
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Dados recebidos - Email: {email}, Senha: {'*' * len(password)}")
        
        if not email or not password:
            print("Erro: Campos vazios")
            flash('Por favor, preencha todos os campos!', 'error')
            return redirect(url_for('login'))
            
        try:
            print("\nTentando conectar ao banco de dados...")
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = connection.cursor()
            print("Conexão estabelecida com sucesso!")
            
            print("\nExecutando query de busca do usuário...")
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
            print(f"Resultado da query: {user}")
            
            if user:
                print("\nUsuário encontrado!")
                print(f"ID: {user['id']}")
                print(f"Username: {user['username']}")
                print(f"is_admin: {user.get('is_admin')}")
                print(f"Wallet: {user.get('wallet')}")
                
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['wallet'] = float(user['wallet'])
                session['is_admin'] = user['is_admin']
                print(f"\nSessão configurada - Wallet set to: {session['wallet']}")
                
                print("\nVerificando tipo de usuário...")
                if user['is_admin'] == 2:
                    print("Usuário é moderador - Redirecionando para moderator_dashboard")
                    return redirect(url_for('moderator_dashboard'))
                elif user['is_admin'] == 1:
                    print("Usuário é admin - Redirecionando para admin_dashboard")
                    return redirect(url_for('admin_dashboard'))
                else:
                    print("Usuário comum - Redirecionando para home")
                    return redirect(url_for('home'))
            else:
                print("\nUsuário não encontrado!")
                flash('Email ou senha inválidos!', 'error')
                return redirect(url_for('login'))
                
        except Exception as e:
            print(f"\n❌ ERRO NO LOGIN: {str(e)}")
            print("Stack trace:")
            import traceback
            traceback.print_exc()
            flash(f'Erro ao fazer login: {str(e)}', 'error')
            return redirect(url_for('login'))
            
        finally:
            print("\nFechando conexões...")
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
            print("Conexões fechadas!")
            print("=== FIM DO LOGIN ===\n")



class AdminDashboardController(MethodView):
    def get(self):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar essa página.', 'danger')
            return redirect(url_for('login'))

        if session.get('is_admin') == True:
            return render_template('public/dashboard.html')  # Renderiza a página do dashboard de admin
        else:
            flash('Acesso negado! Somente administradores podem acessar esta página.', 'danger')
            return redirect(url_for('home'))

class ModeratorDashboardController(MethodView):
    def get(self):
        print("\n=== INÍCIO MODERATOR DASHBOARD ===")
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = connection.cursor()
            
            # Buscar eventos pendentes
            cursor.execute('''
                SELECT * FROM eventos_pendentes 
                WHERE status = 'pending'
            ''')
            eventos_pendentes = cursor.fetchall()
            print(f"Eventos pendentes encontrados: {len(eventos_pendentes)}")
            
            # Buscar participações pendentes
            cursor.execute('''
                SELECT p.*, u.username, e.titulo as evento_titulo
                FROM participacoes p
                JOIN users u ON p.user_id = u.id
                JOIN events e ON p.event_id = e.id
                WHERE p.status = 'pending'
            ''')
            participacoes = cursor.fetchall()
            print(f"Participações pendentes encontradas: {len(participacoes)}")
            
            return render_template('public/moderator_dashboard.html', 
                                eventos_pendentes=eventos_pendentes,
                                participacoes=participacoes)
                                
        except Exception as e:
            print(f"\nErro no dashboard do moderador: {str(e)}")
            traceback.print_exc()  # Isso vai mostrar o stack trace completo
            return redirect(url_for('home'))
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


class EventApprovalController(MethodView):
    def post(self, event_id, action):
        print(f"\n=== Iniciando {action} do evento {event_id} ===")
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = connection.cursor()

            if action == 'approve':
                print("Buscando evento pendente...")
                cursor.execute("""
                    SELECT * FROM eventos_pendentes 
                    WHERE id = %s AND status = 'pending'
                """, (event_id,))
                evento = cursor.fetchone()
                
                if evento:
                    print("Evento encontrado:", evento)
                    try:
                        print("Inserindo na tabela events...")
                        cursor.execute("""
                            INSERT INTO events 
                            (titulo, descricao, valor_cota, inicio_apostas, 
                             fim_apostas, data_evento, user_id, aprovado)
                            VALUES 
                            (%s, %s, %s, %s, %s, %s, %s, 1)
                        """, (
                            evento['titulo'],
                            evento['descricao'],
                            evento['valor_cota'],
                            evento['inicio_apostas'],
                            evento['fim_apostas'],
                            evento['data_evento'],
                            evento['user_id']
                        ))
                        
                        print("Atualizando status na tabela eventos_pendentes...")
                        cursor.execute("""
                            UPDATE eventos_pendentes 
                            SET status = 'approved'
                            WHERE id = %s
                        """, (event_id,))
                        
                        connection.commit()
                        print("Transação commitada com sucesso!")
                        return jsonify({'success': True, 'message': 'Evento aprovado com sucesso!'})
                        
                    except Exception as e:
                        print(f"ERRO durante aprovação: {str(e)}")
                        connection.rollback()
                        return jsonify({'error': str(e)}), 500
                else:
                    print("Evento não encontrado ou já processado")
                    return jsonify({'error': 'Evento não encontrado ou já processado'}), 404

            elif action == 'reject':
                dados = request.get_json()
                motivos = dados.get('motivos', [])
                print(f"Rejeitando evento com motivos: {motivos}")
                
                cursor.execute("""
                    UPDATE eventos_pendentes 
                    SET status = 'rejected',
                        motivos_rejeicao = %s
                    WHERE id = %s AND status = 'pending'
                """, (', '.join(motivos), event_id))
                
                connection.commit()
                print("Evento rejeitado com sucesso!")
                return jsonify({'success': True, 'message': 'Evento rejeitado com sucesso!'})
                    
        except Exception as e:
            print(f"ERRO GERAL: {str(e)}")
            if connection:
                connection.rollback()
            return jsonify({'error': str(e)}), 500
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            print("=== Finalizado ===\n")

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
                events = cursor.fetchall()  

            if not events:
                flash('Nenhum evento encontrado.', 'info')  
            
        except Exception as e:
            flash(f'Ocorreu um erro ao buscar eventos: {str(e)}', 'danger')  
            return redirect(url_for('home'))  
        finally:
            connection.close()  

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
                cursor.execute("DELETE FROM participacoes WHERE event_id = %s", (event_id,))
                
               
                cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
                connection.commit()  # altera o db

            flash('Evento excluído com sucesso!', 'success')
        except Exception as e:
            flash(f'Ocorreu um erro ao excluir o evento: {str(e)}', 'danger')
        finally:
            connection.close()  # fecha a conexão com o db

        return redirect(url_for('eventosagora')) 

class ConfirmationController(MethodView):
    def get(self):
        return render_template('public/confirmation.html')

class LogoutController(MethodView):
    def get(self):
        session.clear()
        flash('Você saiu com sucesso!', 'success')
        return redirect(url_for('home'))



class LoginConfirmationController(MethodView):
    def get(self):
        return render_template('public/confirmationlogin.html')


class HomeController(MethodView):
    def get(self):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Contagem de apostas em Dados
            try:
                cursor.execute("SELECT COUNT(*) as total FROM bets")
                result = cursor.fetchone()
                dados_apostas = result['total'] if result else 0
                print(f"Dados apostas: {dados_apostas}")
            except Exception as e:
                print(f"Erro ao contar bets: {str(e)}")
                dados_apostas = 0

            # Contagem de apostas em Cores
            try:
                cursor.execute("SELECT COUNT(*) as total FROM color_bet")
                result = cursor.fetchone()
                cores_apostas = result['total'] if result else 0
                print(f"Cores apostas: {cores_apostas}")
            except Exception as e:
                print(f"Erro ao contar color_bet: {str(e)}")
                cores_apostas = 0

            # Contagem de eventos esportivos
            try:
                cursor.execute("SELECT COUNT(*) as total FROM events")
                result = cursor.fetchone()
                total_eventos = result['total'] if result else 0
                print(f"Total eventos: {total_eventos}")
            except Exception as e:
                print(f"Erro ao contar events: {str(e)}")
                total_eventos = 0

            return render_template('public/home.html', 
                                dados_apostas=dados_apostas,
                                cores_apostas=cores_apostas,
                                eventos_ativos=total_eventos)

        except Exception as e:
            print(f"Erro principal: {str(e)}")
            return render_template('public/home.html', 
                                dados_apostas=0,
                                cores_apostas=0,
                                eventos_ativos=0)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


class CreateBetController(MethodView):
    def get(self):
        # Método para mostrar o formulário de criação de evento
        if 'user_id' not in session:
            flash('Você precisa estar logado para criar um evento.', 'danger')
            return redirect(url_for('login'))
        return render_template('public/create_bet.html')

    def post(self):
        # Método para processar o formulário enviado
        if 'user_id' not in session:
            flash('Você precisa estar logado para criar um evento.', 'danger')
            return redirect(url_for('login'))

        title = request.form.get('title')
        description = request.form.get('description')
        bet_value = request.form.get('bet_value')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        event_date = request.form.get('event_date')

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro',
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                # Modificando a query para incluir is_approved = 0
                sql = """
                    INSERT INTO eventos_pendentes (titulo, descricao, valor_cota, inicio_apostas, 
                                      fim_apostas, data_evento, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (title, description, bet_value, start_time, 
                                   end_time, event_date, session['user_id']))
                connection.commit()
                
                return redirect(url_for('home'))

        except Exception as e:
            print(f"Erro ao criar evento: {e}")
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
        print("\n=== LISTANDO EVENTOS ===")
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                print("1. Executando query...")
                cursor.execute("SELECT * FROM events")
                events = cursor.fetchall()
                print(f"2. Eventos encontrados: {len(events)}")

            if not events:
                print("3. Nenhum evento encontrado")
                flash('Nenhum evento encontrado.', 'info')
            
        except Exception as e:
            print(f"\n❌ ERRO: {str(e)}")
            flash(f'Ocorreu um erro ao buscar eventos: {str(e)}', 'danger')
            return redirect(url_for('home'))
            
        finally:
            connection.close()
            print("4. Conexão fechada")

        print("5. Renderizando template...")
        return render_template('public/listar_eventos.html', events=events)


class WalletController(MethodView):
    def get(self):
        if not session.get('user_id'):
            return redirect(url_for('login'))

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, wallet 
                    FROM users 
                    WHERE id = %s
                """, (session['user_id'],))
                user = cursor.fetchone()
                return render_template('public/wallet.html', user=user)
        finally:
            connection.close()

class DepositController(MethodView):
    def get(self):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('public/deposito.html')

    def post(self):
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        try:
            valor = abs(float(request.form.get('valor', 0)))  # Garantindo que o valor é positivo
            
            if valor < 10:
                return render_template('public/payment_result.html', 
                                     success=False, 
                                     message='O valor mínimo para depósito é R$ 10,00')
                
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = connection.cursor()
            
            # Registra a transação (tipo 1 = depósito)
            cursor.execute('''
                INSERT INTO transacoes (user_id, tipo, valor, data) 
                VALUES (%s, 1, %s, NOW())
            ''', (session['user_id'], valor))  # Garantindo tipo 1 para depósito
            
            # Atualiza o saldo
            cursor.execute('UPDATE users SET wallet = wallet + %s WHERE id = %s',
                         (valor, session['user_id']))
            
            connection.commit()
            session['wallet'] = float(session['wallet']) + valor
            
            return render_template('public/payment_result.html', 
                                 success=True, 
                                 message=f'Depósito de R$ {valor:.2f} realizado com sucesso!',
                                 valor=valor)
            
        except Exception as e:
            return render_template('public/payment_result.html', 
                                 success=False, 
                                 message=f'Erro ao processar o pagamento: {str(e)}')
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

class WithdrawController(MethodView):
    def get(self):
        if not session.get('user_id'):
            return redirect(url_for('login'))

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, wallet 
                    FROM users 
                    WHERE id = %s
                """, (session['user_id'],))
                user = cursor.fetchone()
                return render_template('public/sacar.html', user=user)
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
                SELECT e.id, e.titulo, e.descricao, e.valor_cota, e.inicio_apostas, e.fim_apostas, e.data_evento, p.confirmacao
                FROM events e
                JOIN participacoes p ON e.id = p.event_id
                WHERE p.user_id = %s
            """
            cursor.execute(query, (user_id,))
            meus_eventos = cursor.fetchall()  # recupera todos os eventos
            cursor.close()
            connection.close()  
            
            return render_template('public/meus_eventos.html', meus_eventos=meus_eventos)
        else:
            return redirect(url_for('home'))
        


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
                    # Pega o valor da cota do evento
                    cursor.execute("SELECT valor_cota FROM events WHERE id = %s", (event_id,))
                    event = cursor.fetchone()

                    if event is None:
                        flash('Evento não encontrado.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    event_value = float(event[0])  # Converte para float

                    # Pega o saldo do usuário
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

                    # Salva a confirmação na tabela
                    confirmation = request.form.get('confirmacao')
                    print(f"Confirmação recebida: {confirmation}")  # Print para depuração

                    confirmation_value = 'SIM' if confirmation == 'sim' else 'NAO'
                    
                    cursor.execute("INSERT INTO participacoes (user_id, event_id, confirmacao) VALUES (%s, %s, %s)", 
                                   (user_id, event_id, confirmation_value))
                    connection.commit()
                    print(f"Participação inserida: user_id={user_id}, event_id={event_id}, confirmacao='{confirmation_value}'")  # Print da inserção
                    
                    # Verifica se a inserção foi bem-sucedida
                    cursor.execute("SELECT * FROM participacoes WHERE user_id = %s AND event_id = %s", (user_id, event_id))
                    inserted_participation = cursor.fetchone()
                    print(f"Participação registrada na tabela: {inserted_participation}")  # Print da nova participação
                    
                    # Adiciona a transação na tabela de transações
                    cursor.execute(
                        "INSERT INTO transacoes (user_id, tipo, valor) VALUES (%s, %s, %s)",
                        (user_id, 'participacao', event_value)
                    )
                    connection.commit()
                    print(f"Transação registrada: user_id={user_id}, tipo='participacao', valor={event_value}")

                    flash('Você participou do evento com sucesso!', 'success')

                return redirect(url_for('listar_eventos'))

        except Exception as e:
            flash(f'Ocorreu um erro ao participar do evento: {str(e)}', 'danger')
            return redirect(url_for('listar_eventos'))

        finally:
            connection.close()


class JogoController(MethodView):
    def get(self):
        if not session.get('user_id'):
            flash('Você precisa estar logado para jogar!', 'danger')
            return redirect(url_for('login'))

        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro',
                cursorclass=pymysql.cursors.DictCursor  # Para retornar resultados como dicionário
            )
            cursor = connection.cursor()
            
            # Busca dados do usuário
            cursor.execute('SELECT wallet FROM users WHERE id = %s', (session['user_id'],))
            user = cursor.fetchone()
            
            # Busca transações do jogo
            cursor.execute('''
                SELECT * FROM transacoes 
                WHERE user_id = %s AND tipo IN (3, 4)
                ORDER BY data DESC
            ''', (session['user_id'],))
            transacoes = cursor.fetchall()
            
            if user:
                return render_template('public/jogo.html', 
                                    saldo=float(user['wallet']),
                                    transacoes=transacoes)
            else:
                flash('Usuário não encontrado!', 'danger')
                return redirect(url_for('home'))
                
        except Exception as e:
            print(f"Erro ao carregar jogo: {str(e)}")  # Debug
            flash(f'Erro ao carregar o jogo: {str(e)}', 'danger')
            return redirect(url_for('home'))
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def post(self):
        print("\n=== INÍCIO DA APOSTA ===")
        if 'user_id' not in session:
            print("Erro: Usuário não está logado")
            return jsonify({
                'status': 'error',
                'message': 'Usuário não está logado'
            })

        try:
            print("\n1. Dados recebidos do formulário:")
            print(f"Form data: {request.form}")
            valor_aposta = float(request.form.get('valor_aposta', 0))
            numero_escolhido = int(request.form.get('numero_escolhido'))
            
            print(f"\n2. Valores convertidos:")
            print(f"Valor aposta: R$ {valor_aposta}")
            print(f"Número escolhido: {numero_escolhido}")
            print(f"Saldo atual: R$ {session['wallet']}")
            
            if float(session['wallet']) < valor_aposta:
                print("Erro: Saldo insuficiente")
                return jsonify({
                    'status': 'error',
                    'message': 'Saldo insuficiente'
                })

            print("\n3. Conectando ao banco de dados...")
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = connection.cursor()
            print("Conexão estabelecida com sucesso!")

            try:
                # Gera o número aleatório
                numero_sorteado = random.randint(1, 6)
                print(f"\n4. Número sorteado: {numero_sorteado}")

                print("\n5. Registrando a aposta...")
                cursor.execute('''
                    INSERT INTO transacoes (user_id, tipo, valor, data) 
                    VALUES (%s, 3, %s, NOW())
                ''', (session['user_id'], valor_aposta))
                print("Aposta registrada!")

                print("\n6. Atualizando saldo do usuário...")
                cursor.execute('UPDATE users SET wallet = wallet - %s WHERE id = %s',
                             (valor_aposta, session['user_id']))
                print("Saldo atualizado!")

                if numero_escolhido == numero_sorteado:
                    print("\n7. JOGADOR GANHOU!")
                    valor_ganho = valor_aposta * 5
                    print(f"Valor ganho: R$ {valor_ganho}")
                    
                    print("Registrando ganho...")
                    cursor.execute('''
                        INSERT INTO transacoes (user_id, tipo, valor, data) 
                        VALUES (%s, 4, %s, NOW())
                    ''', (session['user_id'], valor_ganho))
                    
                    print("Atualizando saldo com o ganho...")
                    cursor.execute('UPDATE users SET wallet = wallet + %s WHERE id = %s',
                                 (valor_ganho, session['user_id']))
                    
                    connection.commit()
                    session['wallet'] = float(session['wallet']) - valor_aposta + valor_ganho
                    print(f"Novo saldo: R$ {session['wallet']}")
                    
                    return jsonify({
                        'status': 'success',
                        'message': f'Parabéns! Você ganhou R$ {valor_ganho:.2f}!',
                        'numero_sorteado': numero_sorteado,
                        'ganhou': True,
                        'novo_saldo': f'R$ {session["wallet"]:.2f}'
                    })
                else:
                    print("\n7. JOGADOR PERDEU!")
                    connection.commit()
                    session['wallet'] = float(session['wallet']) - valor_aposta
                    print(f"Novo saldo: R$ {session['wallet']}")
                    
                    return jsonify({
                        'status': 'success',
                        'message': 'Não foi dessa vez! Tente novamente!',
                        'numero_sorteado': numero_sorteado,
                        'ganhou': False,
                        'novo_saldo': f'R$ {session["wallet"]:.2f}'
                    })

            except Exception as e:
                print("\nERRO NO BANCO DE DADOS:")
                print(f"Erro: {str(e)}")
                print("Stack trace:")
                import traceback
                traceback.print_exc()
                connection.rollback()
                return jsonify({
                    'status': 'error',
                    'message': f'Erro ao processar aposta: {str(e)}'
                })

            finally:
                print("\n8. Fechando conexões...")
                cursor.close()
                connection.close()
                print("Conexões fechadas!")

        except Exception as e:
            print("\nERRO GERAL:")
            print(f"Erro: {str(e)}")
            print("Stack trace:")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': f'Erro ao processar aposta: {str(e)}'
            })

        print("\n=== FIM DA APOSTA ===")







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
                cursor.execute("SELECT id, username, email, birthdate FROM users WHERE is_admin = 0")
                usuarios = cursor.fetchall()
        finally:
            connection.close()

        return render_template('public/listar_usuarios.html', usuarios=usuarios)
    
class ConfirmParticipationController(MethodView):
    def post(self):
        user_id = request.form.get('user_id')
        event_id = request.form.get('event_id')
        resultado = request.form.get('resultado')  # O resultado pode ser 'positivo' ou 'negativo'

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )

        try:
            with connection.cursor() as cursor:
                # Atualiza a participação do usuário com o resultado do moderador
                cursor.execute("UPDATE participacoes SET confirmacao = %s WHERE user_id = %s AND event_id = %s", 
                               (resultado, user_id, event_id))
                connection.commit()
                flash('Participação confirmada com sucesso!', 'success')
        except Exception as e:
            flash(f'Ocorreu um erro ao confirmar a participação: {str(e)}', 'danger')
        finally:
            connection.close()


class UserProfileController(MethodView):
    def get(self):
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = connection.cursor()
        
        try:
            # Busca dados do usuário
            cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
            user = cursor.fetchone()
            
            # Busca transações do usuário
            cursor.execute('''
                SELECT * FROM transacoes 
                WHERE user_id = %s 
                ORDER BY data DESC
            ''', (session['user_id'],))
            transactions = cursor.fetchall()
            
            return render_template('public/profile.html', 
                                 user=user,
                                 transactions=transactions)
                                 
        finally:
            cursor.close()
            connection.close()

def add_valor_ganho_column():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro'
        )
        cursor = connection.cursor()
        
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS valor_ganho DECIMAL(10,2) DEFAULT 0.00
        """)
        
        connection.commit()
        print("Coluna valor_ganho adicionada com sucesso!")
        
    except Exception as e:
        print(f"Erro ao adicionar coluna: {e}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

class BalanceController(MethodView):
    def get(self):
        if 'user_id' not in session:
            return jsonify({'error': 'Usuário não logado'}), 401
            
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro'
            )
            cursor = connection.cursor()
            
            cursor.execute('SELECT wallet FROM users WHERE id = %s', (session['user_id'],))
            result = cursor.fetchone()
            
            if result:
                session['wallet'] = float(result[0])  # Atualiza o saldo na sessão
                return jsonify({'balance': float(result[0])})
            
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()



class JogoCorController(MethodView):
    def get_db_connection(self):
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro',
            charset='utf8mb4'
        )

    def get(self):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            # Buscar informações do usuário
            cursor.execute('SELECT username, wallet FROM users WHERE id = %s', 
                         (session['user_id'],))
            user = cursor.fetchone()

            if not user:
                return redirect(url_for('login'))

            # Buscar total de apostas do usuário
            cursor.execute('SELECT COUNT(*) FROM color_bet WHERE user_id = %s', 
                         (session['user_id'],))
            total_apostas = cursor.fetchone()[0]

            # Buscar total de apostas globais
            cursor.execute('SELECT COUNT(*) FROM color_bet')
            total_apostas_global = cursor.fetchone()[0]

            return render_template('public/jogo_cor.html',
                                name=user[0],
                                saldo=float(user[1]),
                                total_apostas=total_apostas,
                                total_apostas_global=total_apostas_global)

        except Exception as e:
            print(f"Erro ao carregar página jogo de cores: {str(e)}")
            return redirect(url_for('login'))

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

class GetBalanceController(MethodView):
    def get(self):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
            
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro'
            )
            cursor = connection.cursor()
            
            cursor.execute('SELECT wallet FROM users WHERE id = %s', (session['user_id'],))
            result = cursor.fetchone()
            
            if result:
                session['wallet'] = float(result[0])
                return jsonify({'balance': float(result[0])})
                
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

class SaldoController(MethodView):
    def get_db_connection(self):
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro',
            charset='utf8mb4'
        )

    def get(self):
        if not session.get('user_id'):
            return jsonify({
                'success': False,
                'message': 'Usuário não autenticado'
            }), 401

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute('SELECT wallet FROM users WHERE id = %s', 
                         (session['user_id'],))
            result = cursor.fetchone()
            
            if result:
                return jsonify({
                    'success': True,
                    'saldo': float(result[0])
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Usuário não encontrado'
                }), 404

        except Exception as e:
            print(f"Erro ao buscar saldo: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erro ao buscar saldo: {str(e)}'
            }), 500

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

def registrar_transacao(user_id, tipo, valor, connection):
    """
    Função auxiliar para registrar transações
    tipos:
    1 = depósito
    2 = saque
    3 = aposta realizada
    4 = ganho de aposta
    5 = reembolso
    """
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO transacoes (user_id, tipo, valor, data) 
        VALUES (%s, %s, %s, NOW())
    ''', (user_id, tipo, valor))
    connection.commit()

# No WithdrawController (Saque)
class WithdrawController(MethodView):
    def get_db_connection(self):
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro',
            charset='utf8mb4'
        )

    def get(self):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            # Buscar informações do usuário
            cursor.execute('SELECT username, wallet FROM users WHERE id = %s', 
                         (session['user_id'],))
            user = cursor.fetchone()

            if not user:
                return redirect(url_for('login'))

            return render_template('public/sacar.html',  # Corrigido para sacar.html
                                name=user[0],
                                saldo=float(user[1]))

        except Exception as e:
            print(f"Erro ao carregar página de saque: {str(e)}")
            return redirect(url_for('login'))

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def post(self):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        try:
            valor = float(request.form['valor'])
            
            if valor <= 0:
                flash('O valor do saque deve ser maior que zero.')
                return redirect(url_for('sacar'))  # Corrigido para sacar

            connection = self.get_db_connection()
            cursor = connection.cursor()

            # Verificar saldo
            cursor.execute('SELECT wallet FROM users WHERE id = %s', 
                         (session['user_id'],))
            saldo_atual = float(cursor.fetchone()[0])

            if valor > saldo_atual:
                flash('Saldo insuficiente para realizar o saque.')
                return redirect(url_for('sacar'))  # Corrigido para sacar

            # Atualizar saldo
            novo_saldo = saldo_atual - valor
            cursor.execute('UPDATE users SET wallet = %s WHERE id = %s',
                         (novo_saldo, session['user_id']))

            connection.commit()
            flash('Saque realizado com sucesso!')
            return redirect(url_for('sacar'))  # Corrigido para sacar

        except ValueError:
            flash('Valor inválido para saque.')
            return redirect(url_for('sacar'))  # Corrigido para sacar

        except Exception as e:
            print(f"Erro ao processar saque: {str(e)}")
            flash('Erro ao processar saque. Tente novamente.')
            return redirect(url_for('sacar'))  # Corrigido para sacar

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

# No ParticipateController (Apostas)
class ParticipateController(MethodView): 
    def post(self, event_id):
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
                    # Pega o valor da cota do evento
                    cursor.execute("SELECT valor_cota FROM events WHERE id = %s", (event_id,))
                    event = cursor.fetchone()

                    if event is None:
                        flash('Evento não encontrado.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    try:
                        event_value = float(event[0]) if event[0] is not None else 0.0
                    except (ValueError, TypeError):
                        flash('Erro ao processar valor do evento.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    # Pega o saldo do usuário
                    cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
                    user_result = cursor.fetchone()
                    
                    if user_result is None or user_result[0] is None:
                        flash('Erro ao verificar saldo.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    try:
                        current_wallet = float(user_result[0])
                    except (ValueError, TypeError):
                        flash('Erro ao processar saldo da carteira.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    # Verifica se o usuário tem saldo suficiente
                    if event_value > current_wallet:
                        flash('Saldo insuficiente. Faça um crédito na sua carteira.', 'danger')
                        return redirect(url_for('listar_eventos'))

                    # Atualiza o saldo do usuário
                    new_wallet_balance = current_wallet - event_value
                    cursor.execute("UPDATE users SET wallet = %s WHERE id = %s", (new_wallet_balance, user_id))
                    
                    # Salva a confirmação na tabela
                    confirmation = request.form.get('confirmacao')
                    confirmation_value = 'SIM' if confirmation == 'sim' else 'NAO'
                    
                    cursor.execute("""
                        INSERT INTO participacoes (user_id, event_id, confirmacao) 
                        VALUES (%s, %s, %s)
                    """, (user_id, event_id, confirmation_value))
                    
                    # Adiciona a transação
                    cursor.execute("""
                        INSERT INTO transacoes (user_id, tipo, valor) 
                        VALUES (%s, %s, %s)
                    """, (user_id, 'participacao', event_value))
                    
                    connection.commit()
                    flash('Você participou do evento com sucesso!', 'success')

        except Exception as e:
            print(f"Erro ao participar do evento: {str(e)}")  # Debug
            connection.rollback()
            flash(f'Ocorreu um erro ao participar do evento: {str(e)}', 'danger')
        
        finally:
            connection.close()
            
        return redirect(url_for('listar_eventos'))

# Quando um usuário ganha uma aposta
def processar_ganho_aposta(user_id, valor_ganho, connection):
    # Registra o ganho
    registrar_transacao(user_id, 4, valor_ganho, connection)
    
    cursor = connection.cursor()
    # Atualiza o saldo
    cursor.execute('UPDATE users SET wallet = wallet + %s WHERE id = %s',
                  (valor_ganho, user_id))
    connection.commit()

# Se houver reembolso de aposta
def processar_reembolso(user_id, valor_reembolso, connection):
    # Registra o reembolso
    registrar_transacao(user_id, 5, valor_reembolso, connection)
    
    cursor = connection.cursor()
    # Atualiza o saldo
    cursor.execute('UPDATE users SET wallet = wallet + %s WHERE id = %s',
                  (valor_reembolso, user_id))
    connection.commit()

class EventoController(MethodView):
    def get(self):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT * FROM events ORDER BY data DESC')
            eventos = cursor.fetchall()
            return render_template('public/eventos.html', eventos=eventos)
        finally:
            cursor.close()
            connection.close()

    def post(self):
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Usuário não está logado'
            })

        evento_id = request.form.get('evento_id')
        
        if not evento_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do evento não fornecido'
            })

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = connection.cursor()

        try:
            # Verifica se o evento existe
            cursor.execute('SELECT * FROM events WHERE id = %s', (evento_id,))
            evento = cursor.fetchone()

            if not evento:
                return jsonify({
                    'status': 'error',
                    'message': 'Evento não encontrado'
                })

            # Verifica se já participou
            cursor.execute('''
                SELECT * FROM participacoes 
                WHERE user_id = %s AND event_id = %s
            ''', (session['user_id'], evento_id))
            
            if cursor.fetchone():
                return jsonify({
                    'status': 'error',
                    'message': 'Você já está participando deste evento'
                })

            # Registra a participação
            cursor.execute('''
                INSERT INTO participacoes (user_id, event_id, data)
                VALUES (%s, %s, NOW())
            ''', (session['user_id'], evento_id))
            
            connection.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Participação registrada com sucesso!'
            })

        except Exception as e:
            print(f"Erro ao participar do evento: {str(e)}")
            connection.rollback()
            return jsonify({
                'status': 'error',
                'message': f'Erro ao registrar participação: {str(e)}'
            })

        finally:
            cursor.close()
            connection.close()

class AprovarParticipacaoController(MethodView):
    def post(self, participacao_id):
        print(f"\n=== Iniciando aprovação da participação {participacao_id} ===")
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = connection.cursor()
            
            # 1. Buscar informações da participação
            cursor.execute("""
                SELECT p.*, e.valor_cota, u.wallet, u.valor_ganho
                FROM participacoes p
                JOIN events e ON p.event_id = e.id
                JOIN users u ON p.user_id = u.id
                WHERE p.id = %s AND p.status = 'pending'
            """, (participacao_id,))
            
            participacao = cursor.fetchone()
            print(f"Participação encontrada: {participacao}")
            
            if participacao:
                # 2. Calcular novos valores
                novo_wallet = participacao['wallet'] + participacao['valor_cota']
                novo_valor_ganho = participacao['valor_ganho'] + participacao['valor_cota']
                
                print(f"Valores atuais - Wallet: {participacao['wallet']}, Valor ganho: {participacao['valor_ganho']}")
                print(f"Novos valores - Wallet: {novo_wallet}, Valor ganho: {novo_valor_ganho}")
                
                # 3. Atualizar o usuário
                cursor.execute("""
                    UPDATE users 
                    SET wallet = %s,
                        valor_ganho = %s
                    WHERE id = %s
                """, (novo_wallet, novo_valor_ganho, participacao['user_id']))
                
                # 4. Atualizar a participação
                cursor.execute("""
                    UPDATE participacoes 
                    SET status = 'approved', 
                        confirmacao = 1
                    WHERE id = %s
                """, (participacao_id,))
                
                connection.commit()
                print("Transação concluída com sucesso!")
                return jsonify({'success': True, 'message': 'Participação aprovada com sucesso!'})
            else:
                print("Participação não encontrada ou já processada")
                return jsonify({'success': False, 'message': 'Participação não encontrada ou já processada'})
            
        except Exception as e:
            print(f"ERRO: {str(e)}")
            if connection:
                connection.rollback()
            return jsonify({'success': False, 'message': str(e)})
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            print("=== Finalizado ===\n")

class RecusarParticipacaoController(MethodView):
    def post(self, participacao_id):
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                db='db_cadastro',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE participacoes 
                SET status = 'rejected'
                WHERE id = %s AND status = 'pending'
            """, (participacao_id,))
            
            connection.commit()
            return jsonify({'success': True, 'message': 'Participação recusada com sucesso!'})
            
        except Exception as e:
            print(f"Erro ao recusar participação: {str(e)}")
            return jsonify({'success': False, 'message': str(e)})
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

class ColorBetController(MethodView):
    def post(self):
        try:
            # Pegar dados do formulário
            data = request.get_json()
            color = data.get('color')
            amount = float(data.get('amount', 0))
            user_id = session.get('user_id')
            
            # Validações básicas
            if not user_id:
                return jsonify({
                    "success": False,
                    "message": "Usuário não está logado!"
                }), 401
            
            if not color or amount <= 0:
                return jsonify({
                    "success": False,
                    "message": "Dados da aposta inválidos! Verifique a cor e o valor."
                }), 400

            connection = get_db_connection()
            cursor = connection.cursor()
            
            try:
                # Verificar saldo do usuário
                cursor.execute("SELECT wallet FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                
                if not user or float(user['wallet']) < amount:
                    return jsonify({
                        "success": False,
                        "message": "Saldo insuficiente para realizar a aposta!"
                    }), 400

                # Registrar a aposta
                cursor.execute("""
                    INSERT INTO color_bets (user_id, color, amount, status)
                    VALUES (%s, %s, %s, 'pending')
                """, (user_id, color, amount))
                
                # Atualizar saldo do usuário
                new_balance = float(user['wallet']) - amount
                cursor.execute("""
                    UPDATE users 
                    SET wallet = %s 
                    WHERE id = %s
                """, (new_balance, user_id))
                
                connection.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Aposta realizada com sucesso!",
                    "new_balance": new_balance
                })

            except Exception as e:
                connection.rollback()
                print(f"Erro ao processar aposta: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": "Erro ao processar a aposta. Tente novamente."
                }), 500
                
        except Exception as e:
            print(f"Erro geral: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Erro ao processar a aposta. Tente novamente."
            }), 500
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()


from flask import jsonify, session
from flask.views import MethodView
import pymysql
from datetime import datetime

class HistoricoApostasController(MethodView):
    def get_db_connection(self):
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='db_cadastro',
            charset='utf8mb4'
        )

    def get(self):
        print("\n=== CARREGANDO HISTÓRICO DE APOSTAS ===")
        
        if not session.get('user_id'):
            print("Erro: Usuário não logado")
            return jsonify({
                'success': False, 
                'message': 'Usuário não logado'
            }), 401
            
        try:
            print("1. Conectando ao banco de dados...")
            connection = self.get_db_connection()
            cursor = connection.cursor()
            
            print("2. Buscando histórico de apostas...")
            cursor.execute('''
                SELECT 
                    id,
                    data_aposta,
                    valor_apostado,
                    cor_apostada,
                    cor_sorteada,
                    multiplicador,
                    valor_ganho,
                    status
                FROM color_bet 
                WHERE user_id = %s 
                ORDER BY data_aposta DESC 
                LIMIT 10
            ''', (session['user_id'],))
            
            historico = []
            for row in cursor.fetchall():
                historico.append({
                    'id': row[0],
                    'data_aposta': row[1].strftime('%Y-%m-%d %H:%M:%S'),
                    'valor_apostado': float(row[2]),
                    'cor_apostada': row[3],
                    'cor_sorteada': row[4],
                    'multiplicador': float(row[5]),
                    'valor_ganho': float(row[6]),
                    'status': row[7]
                })

            print(f"3. {len(historico)} apostas encontradas")
            return jsonify({
                'success': True,
                'historico': historico
            })
            
        except Exception as e:
            print(f"ERRO: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erro ao carregar histórico: {str(e)}'
            }), 500
            
        finally:
            print("5. Fechando conexões...")
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
            print("=== FIM DO CARREGAMENTO DO HISTÓRICO ===\n")