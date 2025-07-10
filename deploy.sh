#!/bin/bash

echo "🚀 Iniciando deploy do Registro de Ponto..."

# Verifica se estamos no diretório correto
if [ ! -f "render.yaml" ]; then
    echo "❌ Erro: render.yaml não encontrado. Execute este script na raiz do projeto."
    exit 1
fi

# Adiciona todas as mudanças
echo "📦 Adicionando arquivos ao Git..."
git add .

# Solicita mensagem de commit
echo "💬 Digite a mensagem do commit:"
read commit_message

if [ -z "$commit_message" ]; then
    commit_message="Deploy: correções de conectividade MongoDB"
fi

# Faz o commit
echo "📝 Fazendo commit..."
git commit -m "$commit_message"

# Faz o push
echo "🔄 Enviando para o repositório..."
git push origin main

echo "✅ Deploy enviado! O Render fará o deploy automaticamente."
echo ""
echo "🔍 Para verificar o status:"
echo "1. Acesse: https://dashboard.render.com"
echo "2. Verifique o serviço 'registro-ponto-api'"
echo "3. Teste: https://registro-ponto-api.onrender.com/health"
echo ""
echo "📋 Lembre-se de configurar as variáveis de ambiente no Render:"
echo "- MONGODB_URI"
echo "- MAIL_USERNAME"
echo "- MAIL_PASSWORD"
echo "- FRONTEND_URL"
echo ""
echo "📖 Consulte CONFIGURACAO_RENDER.md para mais detalhes."
