# 🔐 Gerenciamento de Tokens Gmail

Este documento explica como o sistema gerencia tokens Gmail automaticamente em diferentes ambientes.

## 📋 Estratégias por Ambiente

### 🏠 **Local** (`application-local.yaml`)
```yaml
gmail:
  auth_mode: token-only  # Com refresh automático
  token_monitor:
    enabled: true
    check_interval_minutes: 30
    auto_refresh: true
    fallback_to_console: true
```

**Características:**
- ✅ Refresh automático de tokens
- ✅ Monitor a cada 30 minutos
- ✅ Fallback para console se necessário
- ✅ Ideal para desenvolvimento

### 🛠️ **Desenvolvimento** (`application-dev.yaml`)
```yaml
gmail:
  auth_mode: token-only  # Com refresh automático
  token_monitor:
    enabled: true
    check_interval_minutes: 15  # Mais frequente
    auto_refresh: true
    fallback_to_console: true
```

**Características:**
- ✅ Refresh automático de tokens
- ✅ Monitor a cada 15 minutos (mais frequente)
- ✅ Fallback para console se necessário
- ✅ Logs detalhados para debug

### 🚀 **Produção** (`application-prod.yaml`)
```yaml
gmail:
  auth_mode: service-account  # Mais robusto
  token_monitor:
    enabled: true
    check_interval_minutes: 60
    auto_refresh: false  # Service account não precisa
    fallback_to_console: false
    alerts:
      enabled: true
      webhook_url: ${GMAIL_ALERT_WEBHOOK_URL}
      email_alert: ${GMAIL_ALERT_EMAIL}
```

**Características:**
- ✅ Service Account (mais robusto)
- ✅ Monitor a cada 60 minutos
- ✅ Alertas para problemas
- ✅ Sem dependência de tokens de usuário

## 🔄 Como Funciona o Refresh Automático

### 1. **Detecção de Token Expirado**
```python
# O sistema verifica automaticamente se o token está próximo do vencimento
if creds.expired and creds.refresh_token:
    creds.refresh(Request())  # Renova automaticamente
```

### 2. **Monitor Proativo**
```python
# Verifica tokens a cada X minutos (configurável por ambiente)
time_until_expiry = expiry_time - datetime.utcnow()
if time_until_expiry < timedelta(hours=1):
    # Renova antes de expirar
```

### 3. **Fallback Inteligente**
```python
# Se refresh falhar, tenta fluxo interativo
if not creds.valid and self.auth_mode == "console":
    flow = InstalledAppFlow.from_client_secrets_file(...)
    creds = flow.run_local_server(port=0)
```

## 🛠️ Configuração por Ambiente

### **Local**
```bash
./scripts/setup_environment.sh local
poetry run python run.py
```

### **Desenvolvimento**
```bash
./scripts/setup_environment.sh dev
poetry run python run.py
```

### **Produção**
```bash
./scripts/setup_environment.sh prod
poetry run python run.py
```

## 📊 Monitoramento

### **Logs de Token**
```bash
# Verificar status do token
python scripts/token_monitor.py

# Logs do sistema
tail -f /var/log/gmail-token-monitor.log
```

### **Health Check**
```bash
# Verificar status do consumer
curl http://localhost:8602/health/rabbitmq

# Verificar status geral
curl http://localhost:8602/health
```

## 🚨 Alertas e Troubleshooting

### **Problemas Comuns**

1. **Token Expirado**
   ```
   ERROR: Token has been expired or revoked
   ```
   **Solução:** O sistema renova automaticamente

2. **Service Account Inválido**
   ```
   ERROR: Service account credentials not found
   ```
   **Solução:** Verificar arquivo `service-account.json`

3. **Refresh Token Inválido**
   ```
   ERROR: invalid_grant: Token has been expired or revoked
   ```
   **Solução:** Re-autenticar via console

### **Alertas Automáticos**
- 📧 Email para administradores
- 🔔 Webhook para Slack/Discord
- 📊 Métricas para Prometheus

## 🔧 Configuração Avançada

### **Variáveis de Ambiente**
```bash
# Produção
export GMAIL_ALERT_WEBHOOK_URL="https://hooks.slack.com/..."
export GMAIL_ALERT_EMAIL="admin@company.com"
export APP_ENV=prod
```

### **Docker Compose**
```yaml
services:
  email-sender:
    environment:
      - APP_ENV=prod
      - GMAIL_ALERT_WEBHOOK_URL=${SLACK_WEBHOOK}
    volumes:
      - ./secure:/app/secure:ro
```

## 📈 Benefícios

### ✅ **Autonomia Total**
- Sistema roda indefinidamente sem intervenção manual
- Renovação automática de tokens
- Monitoramento proativo

### ✅ **Robustez**
- Service Account para produção
- Fallback inteligente
- Alertas automáticos

### ✅ **Flexibilidade**
- Configuração por ambiente
- Monitoramento configurável
- Logs detalhados

## 🎯 Resultado Final

O sistema agora é **100% autônomo** e não depende de intervenção manual para renovação de tokens! 🚀

- 🏠 **Local**: Refresh automático com fallback
- 🛠️ **Dev**: Monitoramento mais frequente
- 🚀 **Prod**: Service Account + alertas
