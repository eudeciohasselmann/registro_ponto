# Sistema de Registro de Ponto

Sistema web para controle de ponto eletrônico com funcionalidades de login, registro de horários e recuperação de senha.

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

#### 2. Deploy Automático via render.yaml

1. Acesse o [Dashboard do Render](https://dashboard.render.com)
2. Clique em "New +" → "Blueprint"
3. Conecte seu repositório GitHub
4. Selecione o repositório `registro_ponto`
5. O Render detectará automaticamente o arquivo `render.yaml`

#### 3. Configuração das Variáveis de Ambiente

No painel do Render, configure as seguintes variáveis para o **Backend (registro-ponto-api)**:

##### Variáveis Obrigatórias:

```
MONGODB_URI=mongodb+srv://eudecio:H210716h@cluster0.qjac7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MAIL_USERNAME=eudecio@gmail.com
MAIL_PASSWORD=uvre sbsd xdie zgyr
FRONTEND_URL=https://registro-ponto-frontend.onrender.com
```

##### Variáveis Automáticas (já configuradas):

- `MAIL_SERVER=smtp.gmail.com`
- `MAIL_PORT=587`
- `MAIL_USE_TLS=True`
- `FLASK_ENV=production`

#### 4. Atualização da URL do Frontend

Após o deploy do frontend, atualize a variável `FRONTEND_URL` com a URL real gerada pelo Render.

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
