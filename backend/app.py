from flask import Flask, jsonify, request, g
from flask_cors import CORS
import sqlite3
import bcrypt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from flask_mail import Mail, Message
import secrets
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

DATABASE = 'ponto.db'

def get_db():
    """Obtém conexão com o banco de dados SQLite"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Fecha a conexão com o banco de dados ao final da requisição"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha BLOB NOT NULL,
                horas TEXT DEFAULT '08:00',
                termsAccepted INTEGER DEFAULT 1,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reset_token TEXT,
                reset_token_expiry TIMESTAMP
            )
        ''')
        
        # Tabela de registros de ponto
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                date TEXT NOT NULL,
                periods TEXT NOT NULL,
                total TEXT DEFAULT '00:00',
                credit TEXT DEFAULT '00:00',
                debit TEXT DEFAULT '00:00',
                UNIQUE(user, date)
            )
        ''')
        
        db.commit()
        print("Banco de dados SQLite inicializado com sucesso!")

# Inicializa o banco de dados ao iniciar a aplicação
init_db()

# --- Rotas de Usuário ---

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'nome' not in data or 'senha' not in data or 'email' not in data:
        return jsonify({'error': 'Nome, e-mail e senha são obrigatórios'}), 400

    if not data.get('termsAccepted'):
        return jsonify({'error': 'É necessário aceitar os termos de uso'}), 400

    nome = data['nome']
    email = data['email']
    hashed_password = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt())
    horas = data.get('horas', '08:00')

    db = get_db()
    cursor = db.cursor()
    
    # Verifica se usuário ou email já existe
    cursor.execute('SELECT id FROM users WHERE nome = ? OR email = ?', (nome, email))
    if cursor.fetchone():
        return jsonify({'error': 'Usuário ou e-mail já cadastrado'}), 409

    try:
        cursor.execute('''
            INSERT INTO users (nome, email, senha, horas, termsAccepted, createdAt)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, email, hashed_password, horas, 1, datetime.now()))
        db.commit()
        user_id = cursor.lastrowid
        return jsonify({'message': 'Usuário criado com sucesso', 'id': str(user_id)}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Usuário ou e-mail já cadastrado'}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'nome' not in data or 'senha' not in data:
        return jsonify({'error': 'Nome de usuário e senha são obrigatórios'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT nome, senha, horas FROM users WHERE nome = ?', (data['nome'],))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(data['senha'].encode('utf-8'), user['senha']):
        return jsonify({
            'message': 'Login bem-sucedido',
            'user': {'nome': user['nome'], 'horas': user['horas']}
        }), 200
    
    return jsonify({'error': 'Credenciais inválidas'}), 401

@app.route('/users/<username>', methods=['GET'])
def get_user_hours(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT horas FROM users WHERE nome = ?', (username,))
    user = cursor.fetchone()
    
    if user:
        return jsonify({'horas': user['horas']}), 200
    return jsonify({'error': 'Usuário não encontrado'}), 404

# --- Rotas de Registros de Ponto ---

@app.route('/records', methods=['POST'])
def save_record():
    data = request.get_json()
    if not data or 'date' not in data or 'periods' not in data or 'user' not in data:
        return jsonify({'error': 'Dados incompletos para salvar o registro'}), 400
    
    user = data['user']
    date = data['date']
    periods = json.dumps(data['periods'])  # Converte lista para JSON string
    total = data.get('total', '00:00')
    credit = data.get('credit', '00:00')
    debit = data.get('debit', '00:00')

    db = get_db()
    cursor = db.cursor()
    
    try:
        # Remove registros existentes para esta data e usuário
        cursor.execute('DELETE FROM records WHERE user = ? AND date = ?', (user, date))
        
        # Insere o novo registro
        cursor.execute('''
            INSERT INTO records (user, date, periods, total, credit, debit)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user, date, periods, total, credit, debit))
        
        db.commit()
        record_id = cursor.lastrowid
        return jsonify({'message': 'Registro salvo com sucesso', 'id': str(record_id)}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Erro ao salvar registro: {str(e)}'}), 500

@app.route('/records/<username>', methods=['GET'])
def get_records(username):
    month = request.args.get('month')  # Formato YYYY-MM
    
    db = get_db()
    cursor = db.cursor()
    
    if month:
        cursor.execute('''
            SELECT user, date, periods, total, credit, debit
            FROM records
            WHERE user = ? AND date LIKE ?
            ORDER BY date
        ''', (username, f'{month}%'))
    else:
        cursor.execute('''
            SELECT user, date, periods, total, credit, debit
            FROM records
            WHERE user = ?
            ORDER BY date
        ''', (username,))
    
    records = cursor.fetchall()
    
    # Converte os resultados para dicionários e parseia o JSON dos períodos
    result = []
    for record in records:
        result.append({
            'user': record['user'],
            'date': record['date'],
            'periods': json.loads(record['periods']),
            'total': record['total'],
            'credit': record['credit'],
            'debit': record['debit']
        })
    
    return jsonify(result), 200

@app.route('/records/<date>', methods=['PUT'])
def update_records_by_date(date):
    data = request.get_json()
    if not data or 'periods' not in data or 'user' not in data:
        return jsonify({'error': 'Dados incompletos para atualizar'}), 400

    user = data['user']
    periods = json.dumps(data['periods'])
    total = data.get('total', '00:00')
    credit = data.get('credit', '00:00')
    debit = data.get('debit', '00:00')
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Remove os registros antigos
        cursor.execute('DELETE FROM records WHERE user = ? AND date = ?', (user, date))
        
        # Insere os novos registros
        cursor.execute('''
            INSERT INTO records (user, date, periods, total, credit, debit)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user, date, periods, total, credit, debit))
        
        db.commit()
        return jsonify({'message': f'Registros para {date} atualizados com sucesso'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Erro ao atualizar: {str(e)}'}), 400

@app.route('/records/<date>', methods=['DELETE'])
def delete_records_by_date(date):
    user = request.args.get('user')
    if not user:
        return jsonify({'error': 'Nome de usuário é obrigatório para deletar'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM records WHERE user = ? AND date = ?', (user, date))
    db.commit()
    
    if cursor.rowcount > 0:
        return jsonify({'message': f'Registros do dia {date} foram removidos'}), 200
    
    return jsonify({'error': 'Nenhum registro encontrado para esta data'}), 404

# --- Rota de Recuperação de Senha ---

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'O e-mail é obrigatório'}), 400

        email = data['email'].strip().lower()
        
        # Validação básica de e-mail
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Formato de e-mail inválido'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, nome, email FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            # Por segurança, não informamos se o e-mail foi encontrado ou não
            print(f"Tentativa de reset para e-mail não encontrado: {email}")
            return jsonify({'message': 'Se um usuário com este e-mail existir, um link de redefinição de senha será enviado.'}), 200

        # Gera um token seguro
        token = secrets.token_urlsafe(32)
        # Define um tempo de expiração (ex: 1 hora)
        expiry_time = datetime.now() + timedelta(hours=1)

        # Salva o token e a data de expiração
        cursor.execute('''
            UPDATE users
            SET reset_token = ?, reset_token_expiry = ?
            WHERE id = ?
        ''', (token, expiry_time, user['id']))
        db.commit()

        # Cria o link de redefinição
        frontend_url = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5500')
        reset_link = f"{frontend_url}/reset-password.html?token={token}"

        # Envia o e-mail
        try:
            msg = Message(
                subject="Redefinição de Senha - Ponto Eletrônico",
                sender=app.config['MAIL_USERNAME'],
                recipients=[user['email']]
            )
            msg.html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #3b82f6;">Redefinição de Senha - Ponto Eletrônico</h2>
                        <p>Olá, <strong>{user['nome']}</strong>!</p>
                        <p>Você solicitou a redefinição de sua senha. Para continuar, clique no botão abaixo:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" style="background-color: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Redefinir Senha</a>
                        </div>
                        <p>Ou copie e cole este link no seu navegador:</p>
                        <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 3px;">{reset_link}</p>
                        <p><strong>Código de redefinição:</strong> {token}</p>
                        <p style="color: #666; font-size: 14px;">
                            <strong>Importante:</strong><br>
                            • Este link expira em 1 hora<br>
                            • Se você não solicitou esta alteração, ignore este e-mail<br>
                            • Você também pode usar o código acima diretamente na página de redefinição
                        </p>
                    </div>
                </body>
            </html>
            """
            mail.send(msg)
            print(f"E-mail de reset enviado com sucesso para: {email}")
        except Exception as e:
            print(f"Erro ao enviar e-mail para {email}: {str(e)}")
            # Remove o token se não conseguiu enviar o e-mail
            cursor.execute('''
                UPDATE users
                SET reset_token = NULL, reset_token_expiry = NULL
                WHERE id = ?
            ''', (user['id'],))
            db.commit()
            return jsonify({'error': 'Não foi possível enviar o e-mail de redefinição. Verifique sua conexão e tente novamente.'}), 500

        return jsonify({'message': 'Se um usuário com este e-mail existir, um link de redefinição de senha será enviado.'}), 200
    
    except Exception as e:
        print(f"Erro geral em forgot_password: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        if not data or 'token' not in data or 'new_password' not in data:
            return jsonify({'error': 'Token e nova senha são obrigatórios'}), 400

        token = data['token'].strip()
        new_password = data['new_password']

        # Validação da senha
        if len(new_password) < 6:
            return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400

        db = get_db()
        cursor = db.cursor()
        
        # Procura o usuário com o token
        cursor.execute('''
            SELECT id, nome, reset_token_expiry
            FROM users
            WHERE reset_token = ?
        ''', (token,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Token não encontrado: {token}")
            return jsonify({'error': 'Token inválido ou expirado'}), 400

        # Verifica se o token não expirou
        if user['reset_token_expiry']:
            expiry = datetime.fromisoformat(user['reset_token_expiry'])
            if datetime.now() > expiry:
                print(f"Token expirado para usuário: {user['nome']}")
                # Remove o token expirado
                cursor.execute('''
                    UPDATE users
                    SET reset_token = NULL, reset_token_expiry = NULL
                    WHERE id = ?
                ''', (user['id'],))
                db.commit()
                return jsonify({'error': 'Token expirado. Solicite um novo link de redefinição.'}), 400

        # Atualiza a senha
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('''
            UPDATE users
            SET senha = ?, reset_token = NULL, reset_token_expiry = NULL
            WHERE id = ?
        ''', (hashed_password, user['id']))
        db.commit()

        if cursor.rowcount > 0:
            print(f"Senha redefinida com sucesso para usuário: {user['nome']}")
            return jsonify({'message': 'Senha redefinida com sucesso'}), 200
        else:
            print(f"Falha ao atualizar senha para usuário: {user['nome']}")
            return jsonify({'error': 'Erro ao atualizar a senha'}), 500

    except Exception as e:
        print(f"Erro geral em reset_password: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)