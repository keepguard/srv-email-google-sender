# 🌍 Configurações por Ambiente - Email Google Sender

## 📋 Resumo das Configurações Implementadas

### 🏠 **LOCAL** (`application-local.yaml`)
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
- ✅ **Token com refresh automático**
- ✅ **Monitor a cada 30 minutos**
- ✅ **Fallback para console se necessário**
- ✅ **Ideal para desenvolvimento local**

### 🛠️ **DESENVOLVIMENTO** (`application-dev.yaml`)
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
- ✅ **Token com refresh automático**
- ✅ **Monitor a cada 15 minutos** (mais frequente para debug)
- ✅ **Fallback para console se necessário**
- ✅ **Logs detalhados para desenvolvimento**

### 🚀 **PRODUÇÃO** (`application-prod.yaml`)
```yaml
gmail:
  auth_mode: service-account  # Mais robusto para produção
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
- ✅ **Service Account** (mais robusto e seguro)
- ✅ **Monitor a cada 60 minutos**
- ✅ **Alertas automáticos** para problemas
- ✅ **Sem dependência de tokens de usuário**

## 🔧 Como Usar

### **1. Configurar Ambiente**
```bash
# Local
./scripts/setup_environment.sh local

# Desenvolvimento  
./scripts/setup_environment.sh dev

# Produção
./scripts/setup_environment.sh prod
```

### **2. Iniciar Aplicação**
```bash
# Com configuração automática por ambiente
poetry run python run.py
```

### **3. Verificar Configuração**
```bash
# Testar configuração atual
poetry run python -c "from app.config.loader import load_settings; s = load_settings(); print(f'Auth: {s.gmail.auth_mode}, Monitor: {s.gmail.token_monitor.enabled}, Interval: {s.gmail.token_monitor.check_interval_minutes}min')"
```

## 📊 Comparação de Ambientes

| Ambiente | Auth Mode | Monitor | Intervalo | Auto-Refresh | Fallback | Alertas |
|----------|-----------|---------|-----------|--------------|----------|---------|
| **Local** | token-only | ✅ | 30min | ✅ | ✅ | ❌ |
| **Dev** | token-only | ✅ | 15min | ✅ | ✅ | ❌ |
| **Prod** | service-account | ✅ | 60min | ❌ | ❌ | ✅ |

## 🎯 Benefícios Implementados

### ✅ **Autonomia Total**
- **Sistema roda indefinidamente** sem intervenção manual
- **Renovação automática** de tokens em local/dev
- **Service Account** em produção (mais robusto)

### ✅ **Configuração Inteligente**
- **Local**: Refresh automático com fallback
- **Dev**: Monitoramento mais frequente para debug
- **Prod**: Service Account + alertas automáticos

### ✅ **Monitoramento Proativo**
- **Verificação automática** de tokens
- **Renovação antes do vencimento**
- **Logs detalhados** para troubleshooting
- **Alertas** para problemas em produção

## 🚀 Resultado Final

O sistema agora é **100% autônomo** em todos os ambientes:

- 🏠 **Local**: Ideal para desenvolvimento com refresh automático
- 🛠️ **Dev**: Monitoramento intensivo para debug
- 🚀 **Prod**: Service Account robusto com alertas

**Não há mais dependência de intervenção manual para renovação de tokens!** 🎉
