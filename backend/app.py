
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from flask_mail import Mail, Message
import secrets # Para gerar tokens seguros

load_dotenv() # Carrega as variáveis de ambiente do .env

app = Flask(__name__)

# Configuração do CORS para produção
flask_env = os.getenv('FLASK_ENV', 'development')
frontend_url = os.getenv('FRONTEND_URL', '')

print(f"🔧 FLASK_ENV: {flask_env}")
print(f"🔧 FRONTEND_URL: {frontend_url}")

if flask_env == 'production':
    # Em produção, permite apenas o domínio do frontend
    if frontend_url:
        CORS(app, origins=[frontend_url])
        print(f"✅ CORS configurado para produção com origem: {frontend_url}")
    else:
        print("⚠️ FRONTEND_URL não definida, usando CORS permissivo")
        CORS(app)
else:
    # Em desenvolvimento, permite qualquer origem
    CORS(app)
    print("✅ CORS configurado para desenvolvimento (todas as origens)")

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

# Conexão com o MongoDB
mongodb_uri = os.getenv('MONGODB_URI')
if not mongodb_uri:
    raise ValueError("MONGODB_URI não encontrada nas variáveis de ambiente")

try:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    # Testa a conexão
    client.admin.command('ping')
    print("✅ Conexão com MongoDB estabelecida com sucesso")
    db = client.ponto_db
    users_collection = db.users
    records_collection = db.records
except Exception as e:
    print(f"❌ Erro ao conectar com MongoDB: {str(e)}")
    print(f"URI utilizada: {mongodb_uri[:20]}...")  # Mostra apenas o início da URI por segurança
    raise

# --- Rota de Health Check ---

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Testa a conexão com MongoDB
        client.admin.command('ping')
        
        # Conta documentos nas coleções principais
        users_count = users_collection.count_documents({})
        records_count = records_collection.count_documents({})
        
        return jsonify({
            'status': 'healthy',
            'mongodb': 'connected',
            'database': 'ponto_db',
            'collections': {
                'users': users_count,
                'records': records_count
            },
            'environment': {
                'flask_env': os.getenv('FLASK_ENV'),
                'frontend_url': os.getenv('FRONTEND_URL'),
                'has_mongodb_uri': bool(os.getenv('MONGODB_URI'))
            },
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

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

    if users_collection.find_one({'$or': [{'nome': nome}, {'email': email}]}):
        return jsonify({'error': 'Usuário ou e-mail já cadastrado'}), 409

    user_id = users_collection.insert_one({
        'nome': nome,
        'email': email,
        'senha': hashed_password,
        'horas': horas,
        'termsAccepted': data['termsAccepted'],
        'createdAt': datetime.now() # Adiciona data de criação
    }).inserted_id

    return jsonify({'message': 'Usuário criado com sucesso', 'id': str(user_id)}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'nome' not in data or 'senha' not in data:
        return jsonify({'error': 'Nome de usuário e senha são obrigatórios'}), 400

    user = users_collection.find_one({'nome': data['nome']})

    if user and bcrypt.checkpw(data['senha'].encode('utf-8'), user['senha']):
        return jsonify({'message': 'Login bem-sucedido', 'user': {'nome': user['nome'], 'horas': user['horas']}}), 200
    
    return jsonify({'error': 'Credenciais inválidas'}), 401

@app.route('/users/<username>', methods=['GET'])
def get_user_hours(username):
    user = users_collection.find_one({'nome': username}, {'_id': 0, 'horas': 1})
    if user:
        return jsonify(user), 200
    return jsonify({'error': 'Usuário não encontrado'}), 404

# --- Rotas de Registros de Ponto ---

@app.route('/records', methods=['POST'])
def save_record():
    data = request.get_json()
    if not data or 'date' not in data or 'periods' not in data or 'user' not in data:
        return jsonify({'error': 'Dados incompletos para salvar o registro'}), 400
    
    # Adiciona o nome de usuário ao registro
    record_data = {
        'user': data['user'],
        'date': data['date'],
        'periods': data['periods'],
        'total': data.get('total', '00:00'),
        'credit': data.get('credit', '00:00'),
        'debit': data.get('debit', '00:00'),
    }

    # Remove registros existentes para esta data e usuário antes de inserir o novo
    records_collection.delete_many({'user': data['user'], 'date': data['date']})
    
    record_id = records_collection.insert_one(record_data).inserted_id
    return jsonify({'message': 'Registro salvo com sucesso', 'id': str(record_id)}), 201

@app.route('/records/<username>', methods=['GET'])
def get_records(username):
    month = request.args.get('month') # Formato YYYY-MM
    query = {'user': username}
    if month:
        query['date'] = {'$regex': f'^{month}'}
    
    records = list(records_collection.find(query, {'_id': 0}))
    return jsonify(records), 200

@app.route('/records/<date>', methods=['PUT'])
def update_records_by_date(date):
    data = request.get_json()
    if not data or 'periods' not in data or 'user' not in data:
        return jsonify({'error': 'Dados incompletos para atualizar'}), 400

    user = data['user']
    
    # Remove os registros antigos
    records_collection.delete_many({'user': user, 'date': date})
    
    # Insere os novos registros
    result = records_collection.insert_many(data['records'])
    
    if result.inserted_ids:
        return jsonify({'message': f'Registros para {date} atualizados com sucesso'}), 200
    
    return jsonify({'error': 'Nenhum registro atualizado'}), 400


@app.route('/records/<date>', methods=['DELETE'])
def delete_records_by_date(date):
    user = request.args.get('user')
    if not user:
        return jsonify({'error': 'Nome de usuário é obrigatório para deletar'}), 400

    result = records_collection.delete_many({'user': user, 'date': date})

    if result.deleted_count > 0:
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

        user = users_collection.find_one({'email': email})
        if not user:
            # Por segurança, não informamos se o e-mail foi encontrado ou não
            print(f"Tentativa de reset para e-mail não encontrado: {email}")
            return jsonify({'message': 'Se um usuário com este e-mail existir, um link de redefinição de senha será enviado.'}), 200

        # Gera um token seguro
        token = secrets.token_urlsafe(32)
        # Define um tempo de expiração (ex: 1 hora)
        expiry_time = datetime.now() + timedelta(hours=1)

        # Salva o token e a data de expiração no documento do usuário
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'reset_token': token, 'reset_token_expiry': expiry_time}}
        )

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
            users_collection.update_one(
                {'_id': user['_id']},
                {'$unset': {'reset_token': '', 'reset_token_expiry': ''}}
            )
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

        # Procura o usuário com o token
        user = users_collection.find_one({'reset_token': token})
        if not user:
            print(f"Token não encontrado: {token}")
            return jsonify({'error': 'Token inválido ou expirado'}), 400

        # Verifica se o token não expirou
        if user.get('reset_token_expiry') and datetime.now() > user['reset_token_expiry']:
            print(f"Token expirado para usuário: {user.get('nome', 'desconhecido')}")
            # Remove o token expirado
            users_collection.update_one(
                {'_id': user['_id']},
                {'$unset': {'reset_token': '', 'reset_token_expiry': ''}}
            )
            return jsonify({'error': 'Token expirado. Solicite um novo link de redefinição.'}), 400

        # Atualiza a senha
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        result = users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'senha': hashed_password}, '$unset': {'reset_token': '', 'reset_token_expiry': ''}}
        )

        if result.modified_count > 0:
            print(f"Senha redefinida com sucesso para usuário: {user.get('nome', 'desconhecido')}")
            return jsonify({'message': 'Senha redefinida com sucesso'}), 200
        else:
            print(f"Falha ao atualizar senha para usuário: {user.get('nome', 'desconhecido')}")
            return jsonify({'error': 'Erro ao atualizar a senha'}), 500

    except Exception as e:
        print(f"Erro geral em reset_password: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True)
