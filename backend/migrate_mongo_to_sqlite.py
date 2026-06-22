"""
Script de migração de dados do MongoDB para SQLite
Execute este script se você tiver dados no MongoDB que deseja migrar para SQLite
"""

from pymongo import MongoClient
import sqlite3
import json
from datetime import datetime

# Configuração do MongoDB
MONGO_URI = 'mongodb+srv://eudecio:H210716h@cluster0.qjac7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
MONGO_DB = 'ponto_db'

# Configuração do SQLite
SQLITE_DB = 'ponto.db'

def migrate_data():
    """Migra dados do MongoDB para SQLite"""
    
    print("Iniciando migração do MongoDB para SQLite...")
    
    # Conecta ao MongoDB
    try:
        mongo_client = MongoClient(MONGO_URI)
        mongo_db = mongo_client[MONGO_DB]
        users_collection = mongo_db.users
        records_collection = mongo_db.records
        print("✓ Conectado ao MongoDB")
    except Exception as e:
        print(f"✗ Erro ao conectar ao MongoDB: {e}")
        return
    
    # Conecta ao SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cursor = sqlite_conn.cursor()
        print("✓ Conectado ao SQLite")
    except Exception as e:
        print(f"✗ Erro ao conectar ao SQLite: {e}")
        return
    
    # Migra usuários
    print("\nMigrando usuários...")
    users = list(users_collection.find())
    users_migrated = 0
    
    for user in users:
        try:
            sqlite_cursor.execute('''
                INSERT OR IGNORE INTO users (nome, email, senha, horas, termsAccepted, createdAt, reset_token, reset_token_expiry)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.get('nome'),
                user.get('email'),
                user.get('senha'),
                user.get('horas', '08:00'),
                1 if user.get('termsAccepted') else 0,
                user.get('createdAt', datetime.now()),
                user.get('reset_token'),
                user.get('reset_token_expiry')
            ))
            users_migrated += 1
        except Exception as e:
            print(f"  ✗ Erro ao migrar usuário {user.get('nome')}: {e}")
    
    sqlite_conn.commit()
    print(f"✓ {users_migrated} usuários migrados")
    
    # Migra registros de ponto
    print("\nMigrando registros de ponto...")
    records = list(records_collection.find())
    records_migrated = 0
    
    for record in records:
        try:
            # Converte periods para JSON string se for uma lista
            periods = record.get('periods')
            if isinstance(periods, list):
                periods = json.dumps(periods)
            elif isinstance(periods, str):
                # Já é string, mantém como está
                pass
            else:
                periods = json.dumps([])
            
            sqlite_cursor.execute('''
                INSERT OR REPLACE INTO records (user, date, periods, total, credit, debit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record.get('user'),
                record.get('date'),
                periods,
                record.get('total', '00:00'),
                record.get('credit', '00:00'),
                record.get('debit', '00:00')
            ))
            records_migrated += 1
        except Exception as e:
            print(f"  ✗ Erro ao migrar registro {record.get('date')} do usuário {record.get('user')}: {e}")
    
    sqlite_conn.commit()
    print(f"✓ {records_migrated} registros migrados")
    
    # Fecha conexões
    mongo_client.close()
    sqlite_conn.close()
    
    print("\n✓ Migração concluída com sucesso!")
    print(f"\nResumo:")
    print(f"  - Usuários migrados: {users_migrated}")
    print(f"  - Registros migrados: {records_migrated}")
    print(f"\nO banco de dados SQLite foi criado em: {SQLITE_DB}")

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRAÇÃO DE DADOS: MongoDB → SQLite")
    print("=" * 60)
    print("\nAVISO: Este script irá copiar todos os dados do MongoDB")
    print("para o SQLite. Certifique-se de que:")
    print("  1. O MongoDB está acessível")
    print("  2. Você tem backup dos dados")
    print("  3. O arquivo ponto.db será criado/atualizado")
    print("\n" + "=" * 60)
    
    resposta = input("\nDeseja continuar? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        migrate_data()
    else:
        print("\nMigração cancelada.")