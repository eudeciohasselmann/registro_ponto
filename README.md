# Registro de Ponto Eletrônico

Sistema de controle de ponto eletrônico com backend Flask, frontend HTML/CSS/JS e deploy via Docker Compose.

## Funcionalidades

- **Autenticação** — Login e cadastro de usuários com senhas criptografadas (bcrypt)
- **Registro de Ponto** — Múltiplos períodos por dia (entrada/saída), cálculo automático de horas
- **Dashboard** — Cards com dias trabalhados, média diária, projeção mensal e saldo acumulado
- **Gráficos** — Horas por dia (barras) e proporção crédito vs débito (donut) via Chart.js
- **Filtro Mensal** — Visualização dos registros por mês
- **Recuperação de Senha** — Envio de e-mail com token para redefinição (via SMTP Gmail)
- **Resumo Automático** — Cálculo de total geral, crédito, débito e saldo do período

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3.11 + Flask + SQLite |
| Frontend | HTML5 + CSS3 + JavaScript (vanilla) |
| Gráficos | Chart.js 4 |
| Proxy | Nginx |
| Container | Docker + Docker Compose |
| Email | Flask-Mail (SMTP Gmail) |
| Autenticação | bcrypt + sessionStorage |

## Estrutura do Projeto

```
.
├── docker-compose.yml    # Orquestração dos containers
├── Dockerfile            # Container do frontend (Nginx)
├── nginx.conf            # Proxy reverso para API
├── index.html            # Página de login/cadastro
├── ponto.html            # Página principal com dashboard e registro
├── forgot-password.html  # Solicitação de recuperação de senha
├── reset-password.html   # Redefinição de senha
├── css/
│   ├── login.css         # Estilos da página de login
│   └── styles.css        # Estilos do dashboard e registro
├── js/
│   ├── login.js          # Lógica de login e cadastro
│   ├── ponto.js          # Lógica de registro de ponto
│   ├── dashboard.js      # Lógica dos dashboards e gráficos
│   ├── forgot-password.js
│   └── reset-password.js
└── backend/
    ├── Dockerfile        # Container do backend (Flask)
    ├── app.py            # API Flask com todas as rotas
    ├── requirements.txt  # Dependências Python
    ├── .env              # Configurações de e-mail
    └── ponto.db          # Banco de dados SQLite
```

## Instalação e Uso

### Pré-requisitos

- Docker e Docker Compose instalados

### Passo a passo

```bash
# 1. Clone o repositório
git clone git@github.com:eudeciohasselmann/registro_ponto.git
cd registro_ponto

# 2. Configure as variáveis de ambiente (e-mail para recuperação de senha)
cp backend/.env.example backend/.env
# Edite backend/.env com suas credenciais SMTP

# 3. Inicie os containers
docker compose up -d

# 4. Acesse no navegador
open http://localhost:8080
```

### Comandos úteis

```bash
# Iniciar
docker compose up -d

# Parar
docker compose down

# Ver logs
docker compose logs -f

# Reconstruir após alterações
docker compose up -d --build
```

## API Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/users` | Criar novo usuário |
| GET | `/users/<username>` | Obter dados do usuário |
| POST | `/login` | Autenticar usuário |
| GET | `/records/<username>?month=YYYY-MM` | Listar registros do mês |
| POST | `/records` | Salvar registro de ponto |
| PUT | `/records/<date>` | Atualizar registro |
| DELETE | `/records/<date>?user=<user>` | Remover registro |
| POST | `/forgot-password` | Solicitar redefinição de senha |
| POST | `/reset-password` | Redefinir senha com token |

## Paleta de Cores

- **Primária**: Indigo (`#4f46e5`)
- **Sucesso**: Verde (`#10b981`)
- **Perigo**: Vermelho (`#ef4444`)
- **Aviso**: Amarelo (`#f59e0b`)
- **Fundo**: Slate claro (`#f1f5f9`)
- **Superfície**: Branco (`#ffffff`)
- **Texto**: Slate escuro (`#1e293b`)

## Deploy

### Docker (Railway / Fly.io)

O projeto usa Docker Compose com dois serviços. Para plataformas que não suportam Compose (ex: Render), é necessário adaptar para um único serviço ou deploy separado.

### Variáveis de Ambiente

Configuradas em `backend/.env`:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
```

> ⚠️ Use uma **senha de app** do Google, não a senha da conta.