# Configuração de E-mail para Reset de Senha

## Problema Atual

A funcionalidade de reset de senha não está funcionando porque a configuração de e-mail precisa ser ajustada.

## Solução: Configurar Senha de Aplicativo do Gmail

### Passo 1: Ativar Verificação em 2 Etapas

1. Acesse [myaccount.google.com](https://myaccount.google.com)
2. Vá em "Segurança"
3. Ative a "Verificação em duas etapas" se ainda não estiver ativada

### Passo 2: Gerar Senha de Aplicativo

1. Na mesma página de Segurança, procure por "Senhas de app"
2. Clique em "Senhas de app"
3. Selecione "E-mail" como aplicativo
4. Selecione "Outro (nome personalizado)" como dispositivo
5. Digite "Ponto Eletrônico" como nome
6. Clique em "Gerar"
7. **Copie a senha gerada (16 caracteres)**

### Passo 3: Atualizar o arquivo .env

1. Abra o arquivo `backend/.env`
2. Substitua `your_app_password_here` pela senha de aplicativo gerada
3. Exemplo:
   ```
   MAIL_PASSWORD=abcd efgh ijkl mnop
   ```

### Passo 4: Reiniciar o Servidor

```bash
cd backend
python app.py
```

## Teste da Funcionalidade

### 1. Testar Esqueci Senha

1. Acesse `forgot-password.html`
2. Digite um e-mail cadastrado
3. Clique em "Enviar Link"
4. Verifique se o e-mail foi recebido

### 2. Testar Reset de Senha

1. Clique no link do e-mail OU
2. Acesse `reset-password.html` e digite o código manualmente
3. Digite a nova senha
4. Confirme a nova senha
5. Clique em "Salvar Nova Senha"

## Melhorias Implementadas

### Frontend

- ✅ Corrigida animação dos labels em todos os campos
- ✅ Suporte tanto para token na URL quanto no campo manual
- ✅ Validações melhoradas
- ✅ Mensagens de erro mais claras
- ✅ Links de navegação melhorados

### Backend

- ✅ E-mail HTML formatado com botão e código
- ✅ Tratamento de erros robusto
- ✅ Logs para debug
- ✅ Validação de e-mail
- ✅ Limpeza de token em caso de erro

### Segurança

- ✅ Token seguro de 32 caracteres
- ✅ Expiração de 1 hora
- ✅ Remoção automática de tokens usados
- ✅ Não exposição de informações sensíveis

## Estrutura do E-mail Enviado

O e-mail contém:

- Botão clicável para reset
- Link completo para copiar/colar
- Código de redefinição para uso manual
- Instruções claras
- Aviso de expiração

## Troubleshooting

### Se o e-mail não chegar:

1. Verifique a pasta de spam
2. Confirme se a senha de aplicativo está correta
3. Verifique os logs do servidor Python
4. Teste com outro provedor de e-mail

### Se o reset não funcionar:

1. Verifique se o token não expirou (1 hora)
2. Confirme se o código foi copiado corretamente
3. Verifique se o servidor está rodando
4. Teste a conexão com o MongoDB
