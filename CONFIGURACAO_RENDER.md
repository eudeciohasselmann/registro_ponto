# Configuração do Render para Registro de Ponto

## Problema Identificado

Após o deploy no Render, os dados do MongoDB não estão carregando devido a problemas de configuração de variáveis de ambiente e CORS.

## Variáveis de Ambiente Necessárias no Render

Acesse o painel do Render e configure as seguintes variáveis de ambiente:

### 1. MongoDB

```
MONGODB_URI=mongodb+srv://eudecio:H210716h@cluster0.qjac7.mongodb.net/ponto_db?retryWrites=true&w=majority&appName=Cluster0
```

### 2. Configurações de Email

```
MAIL_USERNAME=eudecio@gmail.com
MAIL_PASSWORD=uvre sbsd xdie zgyr
```

### 3. URL do Frontend (CRÍTICO para CORS)

```
FRONTEND_URL=https://SEU_DOMINIO_FRONTEND.com
```

**⚠️ IMPORTANTE:** Substitua `SEU_DOMINIO_FRONTEND.com` pela URL real onde seu frontend está hospedado.

## Como Configurar no Render

1. Acesse o dashboard do Render
2. Vá para o serviço `registro-ponto-api`
3. Clique em "Environment"
4. Adicione cada variável listada acima
5. Clique em "Save Changes"
6. O serviço será automaticamente redeploy

## Verificação da Configuração

Após configurar as variáveis, você pode verificar se tudo está funcionando:

1. Acesse: `https://registro-ponto-api.onrender.com/health`
2. Você deve ver uma resposta JSON com:
   - `status: "healthy"`
   - `mongodb: "connected"`
   - Contagem de usuários e registros
   - Configurações de ambiente

## Problemas Comuns e Soluções

### 1. Erro de CORS

**Sintoma:** Frontend não consegue fazer requisições para a API
**Solução:** Verifique se `FRONTEND_URL` está configurada corretamente

### 2. Erro de Conexão MongoDB

**Sintoma:** API retorna erro 500 ou "unhealthy" no health check
**Solução:** Verifique se `MONGODB_URI` está correta e inclui o nome do banco (`ponto_db`)

### 3. Dados não carregam

**Sintoma:** Login funciona mas registros não aparecem
**Solução:** Verifique os logs do Render para erros específicos

## Logs de Debug

O código agora inclui logs detalhados que aparecerão no console do Render:

- ✅ Conexão com MongoDB estabelecida
- 🔧 Configurações de CORS
- ❌ Erros de conexão ou configuração

## Próximos Passos

1. Configure as variáveis de ambiente no Render
2. Aguarde o redeploy automático
3. Teste o endpoint `/health`
4. Teste o login e carregamento de dados
5. Se ainda houver problemas, verifique os logs no Render
