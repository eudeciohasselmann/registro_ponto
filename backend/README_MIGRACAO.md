# Migração de MongoDB para SQLite

## 📋 Resumo das Mudanças

O backend do sistema de ponto eletrônico foi migrado de **MongoDB** para **SQLite** para simplificar a infraestrutura e facilitar o desenvolvimento local.

## 🔄 O que mudou?

### Antes (MongoDB)

- Banco de dados na nuvem (MongoDB Atlas)
- Dependência: `pymongo`
- Conexão remota necessária
- Estrutura de documentos NoSQL

### Depois (SQLite)

- Banco de dados local (arquivo `ponto.db`)
- Sem dependências externas de banco de dados
- Funciona offline
- Estrutura de tabelas SQL

## 📦 Instalação

1. **Instale as dependências atualizadas:**

```bash
cd backend
pip install -r requirements.txt
```

2. **O banco de dados SQLite será criado automaticamente** quando você iniciar o servidor pela primeira vez.

## 🚀 Como usar

### Iniciar o servidor (novo banco vazio)

```bash
cd backend
python app.py
```

O banco de dados `ponto.db` será criado automaticamente com as tabelas necessárias.

### Migrar dados existentes do MongoDB

Se você tem dados no MongoDB que deseja migrar para SQLite:

1. **Certifique-se de que o pymongo ainda está instalado** (temporariamente):

```bash
pip install pymongo
```

2. **Execute o script de migração:**

```bash
cd backend
python migrate_mongo_to_sqlite.py
```

3. **Siga as instruções na tela** para confirmar a migração.

4. **Após a migração, você pode desinstalar o pymongo:**

```bash
pip uninstall pymongo
```

## 🗄️ Estrutura do Banco de Dados SQLite

### Tabela: `users`

```sql
CREATE TABLE users (
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
```

### Tabela: `records`

```sql
CREATE TABLE records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    date TEXT NOT NULL,
    periods TEXT NOT NULL,  -- JSON string
    total TEXT DEFAULT '00:00',
    credit TEXT DEFAULT '00:00',
    debit TEXT DEFAULT '00:00',
    UNIQUE(user, date)
)
```

## 🔍 Principais Diferenças na Implementação

### Conexão com o Banco

**Antes (MongoDB):**

```python
from pymongo import MongoClient
client = MongoClient('mongodb+srv://...')
db = client.ponto_db
```

**Depois (SQLite):**

```python
import sqlite3
db = sqlite3.connect('ponto.db')
```

### Consultas

**Antes (MongoDB):**

```python
user = users_collection.find_one({'nome': username})
```

**Depois (SQLite):**

```python
cursor.execute('SELECT * FROM users WHERE nome = ?', (username,))
user = cursor.fetchone()
```

### Inserção de Dados

**Antes (MongoDB):**

```python
user_id = users_collection.insert_one(data).inserted_id
```

**Depois (SQLite):**

```python
cursor.execute('INSERT INTO users (...) VALUES (...)', data)
db.commit()
user_id = cursor.lastrowid
```

## ⚠️ Observações Importantes

1. **Backup**: O arquivo `ponto.db` contém todos os seus dados. Faça backup regularmente!

2. **Períodos como JSON**: Os períodos de ponto são armazenados como strings JSON na coluna `periods` da tabela `records`.

3. **Senhas**: Continuam sendo hasheadas com bcrypt, mantendo a mesma segurança.

4. **Tokens de Reset**: Funcionam da mesma forma, armazenados nas colunas `reset_token` e `reset_token_expiry`.

5. **Compatibilidade**: A API REST permanece 100% compatível. O frontend não precisa de alterações.

## 🛠️ Ferramentas Úteis

### Visualizar o banco de dados SQLite

**Opção 1: SQLite Browser (GUI)**

- Download: https://sqlitebrowser.org/
- Interface gráfica para visualizar e editar o banco

**Opção 2: Linha de comando**

```bash
sqlite3 ponto.db
```

Comandos úteis:

```sql
.tables                    -- Lista todas as tabelas
.schema users             -- Mostra estrutura da tabela users
SELECT * FROM users;      -- Lista todos os usuários
SELECT * FROM records;    -- Lista todos os registros
.quit                     -- Sair
```

## 🐛 Solução de Problemas

### Erro: "database is locked"

- Certifique-se de que apenas uma instância do servidor está rodando
- Feche qualquer ferramenta que esteja acessando o banco

### Erro: "no such table"

- Delete o arquivo `ponto.db` e reinicie o servidor
- O banco será recriado automaticamente

### Dados não aparecem após migração

- Verifique se o script de migração foi executado com sucesso
- Confirme que o arquivo `ponto.db` existe no diretório backend

## 📝 Notas de Desenvolvimento

- O SQLite é perfeito para desenvolvimento e aplicações de pequeno/médio porte
- Para produção com muitos usuários simultâneos, considere PostgreSQL ou MySQL
- O código está preparado para fácil migração para outros bancos SQL se necessário

## ✅ Vantagens da Migração

✓ Sem necessidade de conexão com internet  
✓ Configuração mais simples  
✓ Backup mais fácil (apenas um arquivo)  
✓ Melhor para desenvolvimento local  
✓ Sem custos de hospedagem de banco de dados  
✓ Mesma funcionalidade mantida

## 📞 Suporte

Se encontrar problemas durante a migração, verifique:

1. As dependências estão instaladas corretamente
2. O arquivo `.env` está configurado (para envio de emails)
3. Você tem permissões de escrita no diretório backend
