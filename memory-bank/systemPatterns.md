# System Patterns - Sistema de Ponto Eletrônico

## Arquitetura Geral

### Padrão Arquitetural

**Cliente-Servidor com API RESTful**

- **Frontend**: SPA (Single Page Application) em HTML/CSS/JavaScript vanilla
- **Backend**: API REST em Python Flask
- **Banco de Dados**: MongoDB (NoSQL) hospedado no MongoDB Atlas
- **Comunicação**: HTTP/HTTPS com JSON

### Separação de Responsabilidades

```
Frontend (Cliente)
├── Interface do Usuário (HTML/CSS)
├── Lógica de Apresentação (JavaScript)
├── Validações do Cliente
└── Gerenciamento de Estado (SessionStorage)

Backend (Servidor)
├── API REST (Flask)
├── Lógica de Negócio
├── Validações do Servidor
├── Autenticação e Segurança
└── Integração com Banco de Dados

Banco de Dados
├── Coleção Users
├── Coleção Records
└── Índices e Consultas
```

## Padrões de Design Implementados

### 1. MVC (Model-View-Controller) Adaptado

#### Model (Backend)

- **Users Collection**: Dados de usuários e autenticação
- **Records Collection**: Registros de ponto e cálculos
- **Validações**: Regras de negócio centralizadas

#### View (Frontend)

- **index.html**: Tela de login/registro
- **ponto.html**: Interface principal de registro
- **forgot-password.html**: Recuperação de senha
- **reset-password.html**: Redefinição de senha

#### Controller (JavaScript + Flask)

- **Frontend Controllers**: `login.js`, `ponto.js`, `forgot-password.js`, `reset-password.js`
- **Backend Controllers**: Rotas Flask organizadas por funcionalidade

### 2. Repository Pattern (Implícito)

```python
# Acesso a dados centralizado via MongoDB collections
users_collection = db.users
records_collection = db.records

# Operações CRUD encapsuladas nas rotas Flask
```

### 3. Service Layer Pattern

```python
# Lógica de negócio separada da apresentação
def calculate_time_difference(start, end)
def calculate_credits_debits(total_minutes, standard_minutes)
def send_password_reset_email(user, token)
```

## Estrutura de Dados

### Coleção Users

```json
{
  "_id": ObjectId,
  "nome": "string",
  "email": "string",
  "senha": "hashed_password",
  "horas": "08:00",
  "termsAccepted": boolean,
  "createdAt": datetime,
  "reset_token": "string (opcional)",
  "reset_token_expiry": datetime
}
```

### Coleção Records

```json
{
  "_id": ObjectId,
  "user": "string",
  "date": "YYYY-MM-DD",
  "periods": [
    {
      "start": "HH:MM",
      "end": "HH:MM"
    }
  ],
  "total": "HH:MM",
  "credit": "HH:MM",
  "debit": "HH:MM"
}
```

## Padrões de Comunicação

### API REST Endpoints

#### Autenticação

```
POST /users          - Criar usuário
POST /login          - Autenticar usuário
GET  /users/{name}   - Buscar dados do usuário
```

#### Registros

```
POST   /records           - Salvar registro
GET    /records/{user}    - Buscar registros do usuário
PUT    /records/{date}    - Atualizar registros por data
DELETE /records/{date}    - Deletar registros por data
```

#### Recuperação de Senha

```
POST /forgot-password  - Solicitar reset de senha
POST /reset-password   - Confirmar nova senha
```

### Padrões de Request/Response

```javascript
// Request padrão
{
  "Content-Type": "application/json",
  "body": { /* dados */ }
}

// Response padrão
{
  "message": "string",
  "data": { /* dados opcionais */ },
  "error": "string (em caso de erro)"
}
```

## Padrões de Segurança

### Autenticação

- **Hash de Senhas**: bcrypt para criptografia segura
- **Tokens de Reset**: Geração segura com `secrets.token_urlsafe(32)`
- **Expiração**: Tokens com tempo limite de 1 hora
- **Validação**: Verificação de email e formato de dados

### Autorização

- **Session Storage**: Armazenamento local do usuário logado
- **Verificação por Usuário**: Registros filtrados por nome de usuário
- **Limpeza de Sessão**: Logout remove dados locais

### Proteção de Dados

- **CORS**: Configurado para permitir requisições do frontend
- **Validação Dupla**: Cliente e servidor validam dados
- **Sanitização**: Limpeza de inputs antes do processamento

## Padrões de Interface

### Design System

```css
/* Cores principais */
:root {
  --primary-color: #3b82f6;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --error-color: #ef4444;
  --warning-color: #f59e0b;
}

/* Componentes reutilizáveis */
.btn-submit,
.action-btn,
.control-btn .input-field,
.input-box .badge,
.summary-stat;
```

### Padrões de Interação

- **Feedback Imediato**: Cálculos em tempo real
- **Validação Progressive**: Validação conforme usuário digita
- **Estados Visuais**: Loading, success, error states
- **Navegação Intuitiva**: Fluxos claros entre telas

## Padrões de Tratamento de Erros

### Frontend

```javascript
// Padrão try-catch para requisições
try {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error("Erro na requisição");
  }
  // Processar resposta
} catch (error) {
  console.error("Erro:", error);
  alert("Mensagem amigável para o usuário");
}
```

### Backend

```python
# Padrão de tratamento de exceções
try:
    # Lógica principal
    return jsonify({'message': 'Sucesso'}), 200
except Exception as e:
    print(f"Erro: {str(e)}")
    return jsonify({'error': 'Mensagem de erro'}), 500
```

## Padrões de Validação

### Validação de Dados

```javascript
// Frontend - Validação imediata
function validateTimeEntry() {
  if (!date || !entryTime || !exitTime) {
    alert("Preencha todos os campos");
    return false;
  }
  return true;
}
```

```python
# Backend - Validação robusta
if not data or 'nome' not in data or 'senha' not in data:
    return jsonify({'error': 'Dados obrigatórios'}), 400
```

### Validação de Negócio

- **Horários Consistentes**: Saída deve ser posterior à entrada
- **Datas Válidas**: Não permitir datas futuras
- **Usuários Únicos**: Email e nome devem ser únicos
- **Carga Horária**: Formato HH:MM válido

## Padrões de Performance

### Otimizações Frontend

- **Cálculos Locais**: Total parcial calculado no cliente
- **Cache de Dados**: SessionStorage para dados do usuário
- **Lazy Loading**: Carregamento sob demanda de registros

### Otimizações Backend

- **Consultas Eficientes**: Filtros por usuário e data
- **Índices MongoDB**: Otimização de consultas frequentes
- **Batch Operations**: Múltiplos períodos em uma requisição

## Padrões de Manutenibilidade

### Organização de Código

```
projeto/
├── frontend/
│   ├── css/           # Estilos organizados por funcionalidade
│   ├── js/            # Scripts separados por página
│   └── *.html         # Páginas com responsabilidade única
├── backend/
│   ├── app.py         # Rotas organizadas por funcionalidade
│   ├── .env           # Configurações de ambiente
│   └── requirements.txt
└── memory-bank/       # Documentação do projeto
```

### Convenções de Nomenclatura

- **Variáveis**: camelCase no JavaScript, snake_case no Python
- **Funções**: Verbos descritivos (`calculateTimeDifference`)
- **Classes CSS**: kebab-case com BEM quando aplicável
- **Endpoints**: RESTful com substantivos no plural

### Documentação

- **Comentários**: Explicações para lógica complexa
- **README**: Instruções de setup e uso
- **Memory Bank**: Documentação arquitetural completa
- **Logs**: Registro de erros e operações importantes
