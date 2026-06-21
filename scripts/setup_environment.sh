#!/bin/bash

# Script para configurar ambiente específico
# Uso: ./scripts/setup_environment.sh [local|dev|prod]

ENV=${1:-local}

echo "🔧 Configurando ambiente: $ENV"

case $ENV in
    "local")
        echo "📱 Configuração LOCAL:"
        echo "  - Token com refresh automático"
        echo "  - Monitor a cada 30 minutos"
        echo "  - Fallback para console habilitado"
        export APP_ENV=local
        ;;
    "dev")
        echo "🛠️  Configuração DESENVOLVIMENTO:"
        echo "  - Token com refresh automático"
        echo "  - Monitor a cada 15 minutos (mais frequente)"
        echo "  - Fallback para console habilitado"
        export APP_ENV=dev
        ;;
    "prod")
        echo "🚀 Configuração PRODUÇÃO:"
        echo "  - Service Account (mais robusto)"
        echo "  - Monitor a cada 60 minutos"
        echo "  - Alertas habilitados"
        echo "  - Sem fallback para console"
        export APP_ENV=prod
        ;;
    *)
        echo "❌ Ambiente inválido. Use: local, dev ou prod"
        exit 1
        ;;
esac

echo "✅ Ambiente $ENV configurado!"
echo "💡 Para iniciar: poetry run python run.py"
