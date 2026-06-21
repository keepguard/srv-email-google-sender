
import os
import logging
from dataclasses import dataclass
from typing import Any, Dict
import yaml

logger = logging.getLogger(__name__)

def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def load_settings_dict() -> Dict[str, Any]:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "..", ".."))
    cfg_dir = os.path.join(root, "config")
    env = os.getenv("APP_ENV", "local").lower()

    def _load_yaml(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    base_cfg = _load_yaml(os.path.join(cfg_dir, "application.yaml"))
    env_file = f"application-{env}.yaml"
    env_cfg_path = os.path.join(cfg_dir, env_file)
    env_cfg = _load_yaml(env_cfg_path) if os.path.exists(env_cfg_path) else {}

    merged = _deep_merge(base_cfg, env_cfg)

    # allow env vars to override simple values
    def _override(target: Dict[str, Any], prefix=""):
        for k, v in list(target.items()):
            key = (prefix + k).upper().replace(".", "_")
            if isinstance(v, dict):
                _override(v, prefix=key + "_")
            else:
                if isinstance(v, bool):
                    env_v = os.getenv(key)
                    if env_v is not None:
                        target[k] = env_v.lower() in ("1", "true", "yes")
                else:
                    env_v = os.getenv(key)
                    if env_v is not None:
                        target[k] = env_v
    _override(merged)

    # Normalize important paths relative to project root when not absolute
    def _abspath(p: str) -> str:
        if not p:
            return p
        if not os.path.isabs(p):
            return os.path.abspath(os.path.join(root, p))
        return p

    gmail = merged.get("gmail", {})
    if "client_secrets_file" in gmail:
        gmail["client_secrets_file"] = _abspath(gmail.get("client_secrets_file"))
    if "token_file" in gmail:
        gmail["token_file"] = _abspath(gmail.get("token_file"))
    merged["gmail"] = gmail

    return merged

@dataclass
class ServerCfg:
    host: str = "0.0.0.0"
    port: int = 8601

@dataclass
class TokenMonitorCfg:
    enabled: bool = True
    check_interval_minutes: int = 30
    auto_refresh: bool = True
    fallback_to_console: bool = True
    alerts: dict = None
    
    def __post_init__(self):
        if self.alerts is None:
            self.alerts = {
                "enabled": False,
                "webhook_url": "",
                "email_alert": ""
            }

@dataclass
class TokenManagerCfg:
    enabled: bool = False
    base_url: str = "http://srv-token-manager:8700"
    timeout: int = 10
    retry_attempts: int = 3

@dataclass
class GmailCfg:
    sender_email: str
    client_secrets_file: str
    token_file: str
    scopes: list
    auth_mode: str = "token-only"  # or console
    token_monitor: TokenMonitorCfg = None
    token_manager: TokenManagerCfg = None
    
    def __post_init__(self):
        if self.token_monitor is None:
            self.token_monitor = TokenMonitorCfg()
        if self.token_manager is None:
            self.token_manager = TokenManagerCfg()


@dataclass
class RabbitMQCfg:
    host: str = "localhost"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"
    vhost: str = "/"
    queues: dict = None
    exchanges: dict = None
    routing_keys: dict = None
    retry: dict = None
    
    def __post_init__(self):
        if self.queues is None:
            self.queues = {
                "email_send": "srv.email.google.sender.message.send",
                "email_send_dlt": "srv.email.google.sender.message.send.dlt"
            }
        if self.exchanges is None:
            # Log fallback usage for monitoring
            logger.warning("Using fallback exchange configuration - this should not happen in production")
            logger.info("Fallback exchanges: srv-email-google-sender-exchange, srv-email-google-sender-exchange-dlt")
            self.exchanges = {
                "email_exchange": "srv-email-google-sender-exchange",
                "email_exchange_dlt": "srv-email-google-sender-exchange-dlt"
            }
        if self.routing_keys is None:
            self.routing_keys = {
                "email_send": "email.google.send",
                "email_failed": "email.failed"
            }
        if self.retry is None:
            self.retry = {
                "max_attempts": 3,
                "initial_delay_seconds": 5
            }

@dataclass
class Settings:
    app_name: str
    app_version: str
    server: ServerCfg
    gmail: GmailCfg
    rabbitmq: RabbitMQCfg

def load_settings() -> Settings:
    cfg = load_settings_dict()
    server = cfg.get("server", {})
    gmail = cfg.get("gmail", {})
    rabbitmq = cfg.get("rabbitmq", {})
    return Settings(
        app_name=cfg.get("app", {}).get("name", "srv-email-google-sender"),
        app_version=cfg.get("app", {}).get("version", "1.0.0"),
        server=ServerCfg(
            host=server.get("host", "0.0.0.0"),
            port=int(server.get("port", 8601)),
        ),
        gmail=GmailCfg(
            sender_email=gmail.get("sender_email", ""),
            client_secrets_file=gmail.get("client_secrets_file", ""),
            token_file=gmail.get("token_file", ""),
            scopes=gmail.get("scopes", ["https://www.googleapis.com/auth/gmail.send"]),
            auth_mode=gmail.get("auth_mode", "token-only"),
            token_monitor=TokenMonitorCfg(
                enabled=gmail.get("token_monitor", {}).get("enabled", True),
                check_interval_minutes=gmail.get("token_monitor", {}).get("check_interval_minutes", 30),
                auto_refresh=gmail.get("token_monitor", {}).get("auto_refresh", True),
                fallback_to_console=gmail.get("token_monitor", {}).get("fallback_to_console", True),
                alerts=gmail.get("token_monitor", {}).get("alerts", {})
            ),
            token_manager=TokenManagerCfg(
                enabled=gmail.get("token_manager", {}).get("enabled", False),
                base_url=gmail.get("token_manager", {}).get("base_url", "http://srv-token-manager:8700"),
                timeout=gmail.get("token_manager", {}).get("timeout", 10),
                retry_attempts=gmail.get("token_manager", {}).get("retry_attempts", 3)
            ),
        ),
        rabbitmq=RabbitMQCfg(
            host=rabbitmq.get("host", "localhost"),
            port=int(rabbitmq.get("port", 5672)),
            user=rabbitmq.get("user", "guest"),
            password=rabbitmq.get("password", "guest"),
            vhost=rabbitmq.get("vhost", "/"),
            queues=rabbitmq.get("queues", {}),
            exchanges=rabbitmq.get("exchanges", {}),
            retry=rabbitmq.get("retry", {}),
        ),
    )
