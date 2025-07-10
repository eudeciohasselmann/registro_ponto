# Sistema de Registro de Ponto

Sistema web para controle de ponto eletrônico com funcionalidades de login, registro de horários e recuperação de senha.

## ⚠️ Problemas Resolvidos - MongoDB não carregava após deploy

### Correções Implementadas:

1. **Conexão MongoDB melhorada**: Adicionado timeout e teste de conexão
2. **URI MongoDB corrigida**: Incluído nome do banco de dados explicitamente
3. **CORS aprimorado**: Debug detalhado e configuração mais robusta
4. **Health Check**: Nova rota `/health` para diagnóstico
5. **Logs detalhados**: Melhor visibilidade de erros e configurações

### Como usar as correções:

1. **Configure as variáveis no Render** (veja `CONFIGURACAO_RENDER.md`)
2. **Teste o health check**: `https://registro-ponto-api.onrender.com/health`
3. **Use o script de deploy**: `./deploy.sh`

## 🚀 Deploy no Render

### Pré-requisitos

1. **Conta no Render**: Crie uma conta gratuita em [render.com](https://render.com)
2. **MongoDB Atlas**: Tenha uma instância do MongoDB Atlas configurada
3. **Email Gmail**: Configure uma senha de app para envio de emails

### Passo a Passo para Deploy

#### 1. Preparação do Repositório

1. Faça commit de todas as alterações:

```bash
git add .
git commit -m "Preparação para deploy no Render"
git push origin main
```

#### 2. Deploy do Backend

1. Acesse o [Dashboard do Render](https://dashboard.render.com)
2. Clique em "New +" → "Blueprint"
3. Conecte seu repositório GitHub
4. Selecione o repositório `registro_ponto`
5. O Render detectará automaticamente o arquivo `render.yaml` e criará o backend

#### 3. Configuração das Variáveis de Ambiente

No painel do Render, configure as seguintes variáveis para o **Backend (registro-ponto-api)**:

##### Variáveis Obrigatórias:

```
MONGODB_URI=xxxxxx
MAIL_USERNAME=xxxxxxx
MAIL_PASSWORD=xxxxxx
FRONTEND_URL=https://registro-ponto-frontend.onrender.com
```

##### Variáveis Automáticas (já configuradas):

- `MAIL_SERVER=smtp.gmail.com`
- `MAIL_PORT=587`
- `MAIL_USE_TLS=True`
- `FLASK_ENV=production`

#### 4. Deploy do Frontend

1. No [Dashboard do Render](https://dashboard.render.com), clique em "New +" → "Static Site"
2. Conecte o mesmo repositório GitHub
3. Configure:
   - **Name**: `registro-ponto-frontend`
   - **Branch**: `main`
   - **Build Command**: (deixe vazio)
   - **Publish Directory**: `.` (raiz do projeto)
4. Clique em "Create Static Site"

#### 5. Configuração Final

1. Após o deploy do frontend, copie a URL gerada (ex: `https://registro-ponto-frontend.onrender.com`)
2. No painel do backend, atualize a variável `FRONTEND_URL` com esta URL
3. Atualize também o arquivo `js/config.js` se necessário com a URL correta do backend

### 🔒 Segurança

- ✅ **MongoDB URI**: Protegida via variáveis de ambiente
- ✅ **Credenciais de Email**: Protegidas via variáveis de ambiente
- ✅ **CORS**: Configurado para permitir apenas o domínio do frontend
- ✅ **Logs Seguros**: Sem exposição de dados sensíveis

### 📁 Estrutura do Projeto

```
registro_ponto/
├── backend/
│   ├── app.py              # Aplicação Flask principal
│   ├── requirements.txt    # Dependências Python
│   ├── gunicorn.conf.py   # Configuração do servidor
│   ├── .env               # Variáveis locais (não commitado)
│   └── .env.example       # Exemplo de variáveis
├── css/                   # Estilos CSS
├── js/                    # Scripts JavaScript
├── *.html                 # Páginas HTML
├── render.yaml           # Configuração do Render
└── README.md             # Este arquivo
```

### 🛠️ Desenvolvimento Local

1. Clone o repositório:

```bash
git clone https://github.com/eudeciohasselmann/registro_ponto.git
cd registro_ponto
```

2. Configure o backend:

```bash
cd backend
cp .env.example .env
# Edite o .env com suas configurações
pip install -r requirements.txt
python app.py
```

3. Abra o frontend:

```bash
# Abra index.html em um servidor local (ex: Live Server)
```

### 📝 Funcionalidades

- **Autenticação**: Login seguro com hash de senhas
- **Registro de Ponto**: Controle de entrada/saída
- **Recuperação de Senha**: Via email com tokens seguros
- **Relatórios**: Visualização de registros por mês
- **Responsivo**: Interface adaptável para mobile

### 🔧 Tecnologias

- **Backend**: Flask, MongoDB, Flask-Mail, Gunicorn
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Deploy**: Render.com
- **Banco**: MongoDB Atlas

### 📞 Suporte

Para dúvidas ou problemas, verifique os logs no painel do Render ou entre em contato.
