# RabbitMQ Consumer - Email Google Sender

## Visão Geral

Este serviço implementa um consumer RabbitMQ assíncrono que processa mensagens de envio de e-mail de forma assíncrona, seguindo arquitetura hexagonal, DDD, SOLID e clean code.

## Arquitetura

### Estrutura de Pastas
```
app/
├── domain/
│   ├── messaging/
│   │   └── email_message.py          # Entity de domínio
│   └── errors.py                     # Exceções de domínio
├── application/
│   ├── port/in/messaging/
│   │   └── message_consumer_port.py  # Port de entrada
│   └── usecases/
│       └── send_email_usecase.py     # Use case existente
└── infrastructure/
    └── messaging/
        ├── rabbitmq/
        │   ├── config/
        │   │   └── rabbitmq_config.py        # Configuração RabbitMQ
        │   ├── consumer/
        │   │   ├── email_message_consumer.py # Consumer principal
        │   │   └── email_message_processor.py # Adapter do usecase
        │   └── dto/
        │       └── email_message_dto.py      # DTO para deserialização
        └── lifecycle.py                      # Gerenciamento de lifecycle
```

## Configuração

### RabbitMQ (application.yaml)
```yaml
rabbitmq:
  host: localhost
  port: 5672
  user: guest
  password: guest
  vhost: /
  queues:
    email_send: email.google.sender.message.send
    email_send_dlt: email.google.sender.message.send.dlt
  retry:
    max_attempts: 3
    initial_delay_seconds: 5
```

### Dependências (pyproject.toml)
- `aio-pika`: Cliente RabbitMQ assíncrono
- `fastapi`: Framework web
- `pydantic`: Validação de dados
- `google-api-python-client`: Integração Gmail

## Filas RabbitMQ

### Fila Principal
- **Nome**: `email.google.sender.message.send`
- **Propósito**: Mensagens de e-mail para processamento
- **DLT**: Após 3 tentativas, mensagens vão para DLT

### Fila DLT (Dead Letter)
- **Nome**: `email.google.sender.message.send.dlt`
- **Propósito**: Mensagens que falharam após todas as tentativas

## Formato da Mensagem

```json
{
  "x_application": "ms-communication",
  "x_correlation_id": "uuid-correlation-id",
  "to": "usuario@exemplo.com",
  "subject": "Assunto do e-mail",
  "html": "<h1>Conteúdo HTML</h1>",
  "cc": "copia@exemplo.com",
  "reply_to": "resposta@exemplo.com"
}
```

### Campos Obrigatórios
- `x_application`: Identificador da aplicação origem
- `x_correlation_id`: ID de correlação para rastreamento
- `to`: E-mail destinatário
- `subject`: Assunto do e-mail

### Campos Opcionais
- `html`: Conteúdo HTML do e-mail
- `cc`: E-mail em cópia
- `reply_to`: E-mail para resposta

## Funcionamento

### 1. Recebimento da Mensagem
- Consumer recebe mensagem da fila principal
- Deserializa JSON para `EmailMessageDTO`
- Valida campos obrigatórios

### 2. Processamento
- Converte DTO para `EmailMessage` (domain entity)
- Validações de domínio (formato de e-mail, etc.)
- Converte para `EmailPayload` para o usecase
- Chama `SendEmailUseCase.execute()`

### 3. Tratamento de Erros
- **Validação**: NACK sem requeue → DLT
- **Processamento**: NACK com requeue (até 3 tentativas) → DLT
- **Sucesso**: ACK da mensagem

### 4. Retry Logic
- Máximo 3 tentativas configurável
- Usa header `x-death` para contar tentativas
- TTL de 5 minutos na fila principal

## Health Checks

### Endpoint Geral
```
GET /health
```

### Endpoint RabbitMQ
```
GET /health/rabbitmq
```

Resposta:
```json
{
  "status": "UP",
  "message": "RabbitMQ Consumer funcionando"
}
```

## Logs

### Estrutura dos Logs
- **Correlation ID**: Rastreamento de mensagens
- **Delivery Tag**: Identificação da mensagem no RabbitMQ
- **Níveis**: INFO, WARNING, ERROR

### Exemplos
```
INFO: Processando mensagem: correlation_id=abc-123, delivery_tag=1
INFO: E-mail enviado com sucesso: correlation_id=abc-123, message_id=gmail-msg-id
WARNING: Tentativa 2 falhou: Erro de conexão Gmail
ERROR: Mensagem enviada para DLT após 3 tentativas: delivery_tag=1
```

## Inicialização

### Desenvolvimento
```bash
# Instalar dependências
poetry install

# Executar aplicação
poetry run python run.py
```

### Docker
```bash
# Build da imagem
docker build -t srv-email-google-sender .

# Executar container
docker run -p 8601:8601 srv-email-google-sender
```

## Monitoramento

### Métricas Importantes
- Mensagens processadas com sucesso
- Mensagens enviadas para DLT
- Tempo de processamento
- Erros de validação vs processamento

### Alertas Sugeridos
- Consumer parado
- Alta taxa de mensagens para DLT
- Erros de conexão RabbitMQ
- Falhas de autenticação Gmail

## Troubleshooting

### Consumer não inicia
1. Verificar conexão RabbitMQ
2. Verificar configurações no YAML
3. Verificar logs de startup

### Mensagens na DLT
1. Verificar logs de erro
2. Verificar configuração Gmail
3. Verificar formato da mensagem

### Performance
1. Ajustar `prefetch_count` no RabbitMQConfig
2. Verificar recursos do servidor
3. Monitorar filas no RabbitMQ Management
