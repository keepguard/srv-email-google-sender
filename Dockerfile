FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only=main --no-root

COPY . .

COPY scripts/start.sh /start.sh
RUN chmod +x /start.sh

ENV APP_ENV=prod
ENV PYTHONPATH=/app
EXPOSE 8602

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8601/health || exit 1

CMD ["/start.sh"]
