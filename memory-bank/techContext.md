# Tech Context - Sistema de Ponto Eletrônico

## Stack Tecnológico

### Frontend

- **HTML5**: Estrutura semântica das páginas
- **CSS3**: Estilização moderna com variáveis CSS e flexbox
- **JavaScript ES6+**: Lógica do cliente com async/await e fetch API
- **Boxicons**: Biblioteca de ícones para interface

### Backend

- **Python 3.x**: Linguagem principal do servidor
- **Flask**: Framework web minimalista e flexível
- **Flask-CORS**: Habilitação de requisições cross-origin
- **Flask-Mail**: Sistema de envio de emails
- **bcrypt**: Criptografia segura de senhas
- **python-dotenv**: Gerenciamento de variáveis de ambiente

### Banco de Dados

- **MongoDB Atlas**: Banco NoSQL na nuvem
- **PyMongo**: Driver Python para MongoDB
- **BSON**: Formato de dados binário do MongoDB

### Infraestrutura

- **Gmail SMTP**: Serviço de email para recuperação de senha
- **Local Development**: Servidor de desenvolvimento local
- **Environment Variables**: Configurações sensíveis isoladas

## Configuração de Desenvolvimento

### Estrutura de Arquivos

```
/home/eudecio/sistemas/ponto/
├── index.html              # Página de login/registro
├── ponto.html              # Interface principal
├── forgot-password.html    # Recuperação de senha
├── reset-password.html     # Redefinição de senha
├── css/
│   ├── login.css          # Estilos da página de login
│   └── styles.css         # Estilos da página principal
├── js/
│   ├── login.js           # Lógica de autenticação
│   ├── ponto.js           # Lógica de registro de ponto
│   ├── forgot-password.js # Lógica de recuperação
│   └── reset-password.js  # Lógica de redefinição
├── backend/
│   ├── app.py             # Servidor Flask
│   ├── .env               # Variáveis de ambiente
│   └── requirements.txt   # Dependências Python
├── memory-bank/           # Documentação do projeto
├── CONFIGURACAO_EMAIL.md  # Guia de configuração de email
└── .clinerules            # Regras do assistente Cline
```

### Dependências Python

```txt
Flask==2.3.3
Flask-CORS==4.0.0
Flask-Mail==0.9.1
pymongo==4.5.0
bcrypt==4.0.1
python-dotenv==1.0.0
```

### Variáveis de Ambiente (.env)

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password_here
```

## Configurações Técnicas

### MongoDB Atlas

- **Cluster**: Cluster0.qjac7.mongodb.net
- **Database**: ponto_db
- **Collections**: users, records
- **Connection String**: mongodb+srv://eudecio:H210716h@cluster0.qjac7.mongodb.net/

### Flask Configuration

```python
app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Configuração de email
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
```

### API Configuration

- **Base URL**: http://127.0.0.1:5000
- **Content-Type**: application/json
- **CORS**: Habilitado para desenvolvimento local

## Padrões de Desenvolvimento

### JavaScript Moderno

```javascript
// Uso de async/await para requisições
async function fetchRecords() {
  try {
    const response = await fetch(
      `${API_URL}/records/${usuario}?month=${currentFilterMonth}`
    );
    if (!response.ok) {
      throw new Error("Falha ao buscar registros");
    }
    return await response.json();
  } catch (error) {
    console.error("Erro:", error);
    return [];
  }
}

// Uso de template literals
const resetLink = `http://127.0.0.1:5500/reset-password.html?token=${token}`;

// Destructuring e spread operator
const [h, m] = calculateTimeDifference(entryTime, exitTime)
  .split(":")
  .map(Number);
```

### CSS Moderno

```css
/* Variáveis CSS para consistência */
:root {
  --primary-color: #3b82f6;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --error-color: #ef4444;
}

/* Flexbox para layouts responsivos */
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Grid para formulários */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 1rem;
  align-items: end;
}
```

### Python Best Practices

```python
# Type hints implícitos através de validações
def create_user():
    data = request.get_json()
    if not data or 'nome' not in data or 'senha' not in data:
        return jsonify({'error': 'Dados obrigatórios'}), 400

# Context managers para recursos
with app.app_context():
    mail.send(msg)

# List comprehensions e generators
records = list(records_collection.find(query, {'_id': 0}))
```

## Ferramentas de Desenvolvimento

### Editor/IDE

- **VSCode**: Editor principal com extensões Python e JavaScript
- **Live Server**: Extensão para servir arquivos estáticos
- **Python Extension**: Suporte completo para desenvolvimento Python

### Debugging

- **Browser DevTools**: Debug do frontend
- **Flask Debug Mode**: `app.run(debug=True)`
- **Console Logging**: `console.log()` no frontend, `print()` no backend

### Testing

- **Manual Testing**: Testes funcionais através da interface
- **API Testing**: Testes diretos dos endpoints via browser/Postman
- **Email Testing**: Verificação do fluxo de recuperação de senha

## Constraints Técnicas

### Limitações Atuais

- **Single User Session**: Apenas um usuário logado por vez no navegador
- **Local Storage**: Dados de sessão armazenados localmente
- **No Authentication Tokens**: Sistema simples sem JWT
- **Manual Email Config**: Requer configuração manual de senha de app

### Dependências Externas

- **Internet Connection**: Necessária para MongoDB Atlas
- **Gmail SMTP**: Dependente do serviço do Google
- **Browser Compatibility**: Requer navegador moderno com ES6+

### Performance Considerations

- **Database Queries**: Filtradas por usuário para eficiência
- **Frontend Calculations**: Cálculos locais para responsividade
- **Minimal Dependencies**: Stack enxuto para rapidez

## Configuração de Email

### Gmail App Password Setup

1. **Ativar 2FA**: Verificação em duas etapas no Google
2. **Gerar App Password**: Senha específica para aplicações
3. **Configurar .env**: Adicionar credenciais no arquivo de ambiente
4. **Testar Conexão**: Verificar envio através do sistema

### Email Templates

```python
# Template HTML para reset de senha
msg.html = f"""
<html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Redefinição de Senha - Ponto Eletrônico</h2>
        <p>Olá, <strong>{user['nome']}</strong>!</p>
        <a href="{reset_link}" style="background-color: #3b82f6; color: white; padding: 12px 30px;">
            Redefinir Senha
        </a>
        <p><strong>Código:</strong> {token}</p>
    </body>
</html>
"""
```

## Deployment Considerations

### Local Development

```bash
# Backend
cd backend
python app.py

# Frontend (Live Server)
# Servir arquivos estáticos na porta 5500
```

### Production Readiness

- **Environment Variables**: Configurações sensíveis isoladas
- **Error Handling**: Tratamento robusto de exceções
- **Security**: Hash de senhas e tokens seguros
- **Logging**: Registro de operações importantes

### Scaling Considerations

- **Database Indexing**: Índices para consultas frequentes
- **Connection Pooling**: Para múltiplas conexões simultâneas
- **Caching**: Implementação de cache para dados frequentes
- **Load Balancing**: Para distribuição de carga

## Troubleshooting

### Problemas Comuns

1. **CORS Errors**: Verificar configuração Flask-CORS
2. **Email Not Sending**: Validar credenciais Gmail
3. **Database Connection**: Confirmar string de conexão MongoDB
4. **JavaScript Errors**: Verificar console do navegador

### Debug Checklist

- [ ] Servidor Flask rodando na porta 5000
- [ ] Frontend servido na porta 5500
- [ ] Variáveis de ambiente configuradas
- [ ] MongoDB Atlas acessível
- [ ] Gmail app password válida

### Logs Importantes

```python
# Backend logging
print(f"E-mail de reset enviado com sucesso para: {email}")
print(f"Erro ao enviar e-mail para {email}: {str(e)}")
print(f"Token não encontrado: {token}")

# Frontend logging
console.error("Erro:", error);
console.log("Dados enviados:", payload);
```

## Próximas Melhorias Técnicas

### Segurança

- **JWT Tokens**: Implementar autenticação baseada em tokens
- **Rate Limiting**: Limitar tentativas de login
- **Input Sanitization**: Validação mais rigorosa de dados

### Performance

- **Database Indexing**: Otimizar consultas MongoDB
- **Frontend Bundling**: Minificação e bundling de assets
- **Caching Strategy**: Implementar cache de dados

### Funcionalidades

- **Real-time Updates**: WebSockets para atualizações em tempo real
- **Offline Support**: Service Workers para funcionamento offline
- **Mobile App**: Desenvolvimento de aplicativo nativo

### DevOps

- **Containerization**: Docker para deployment
- **CI/CD Pipeline**: Automação de deploy
- **Monitoring**: Logs e métricas de produção
