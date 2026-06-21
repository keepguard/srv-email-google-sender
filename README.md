
# srv-email-google-sender

Microserviço FastAPI para envio de e-mail via Gmail API.
Arquitetura: Hexagonal / DDD / SOLID / Clean Code.

## Rotas
- `GET /health`
- `POST /send/mail`

### Payload
```json
{
  "to": "destinatario@exemplo.com",
  "subject": "Assunto",
  "message": "Texto simples",
  "html": "<h1>HTML opcional</h1>",
  "cc": "copia@exemplo.com",
  "replyTo": "responder@exemplo.com"
}
```

## Execução Local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export APP_ENV=local
python app/main.py
```

## Geração de token (uma vez)
```bash
python scripts/generate_token.py --client-secrets ./secure/credentials-local.json --token-file ./secure/token.json
```

## Docker
```bash
docker compose -f docker-compose.srv-email-google-sender.yml up --build -d
```

Monte `./secure` com `credentials.json` e `token.json`.
