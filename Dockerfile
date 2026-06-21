FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema (incluindo curl para healthcheck)
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY pyproject.toml .
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only=main --no-root

COPY . .

# Configurar cron para monitor de token (executa a cada 30 minutos)
RUN echo "*/30 * * * * cd /app && python scripts/token_monitor.py" | crontab -

# Script de inicialização
COPY scripts/start.sh /start.sh
RUN chmod +x /start.sh

ENV APP_ENV=prod
ENV PYTHONPATH=/app
EXPOSE 8602

# Healthcheck para verificar se a aplicação está respondendo
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8601/health || exit 1

CMD ["/start.sh"]