"""
Testes unitários para o módulo de carregamento de configurações.
"""
import os
import pytest
import yaml
from unittest.mock import patch, mock_open, MagicMock
from app.config.loader import _deep_merge, load_settings_dict, Settings


class TestDeepMerge:
    """Testes para a função _deep_merge."""

    def test_deep_merge_simple_dicts(self):
        """Testa merge de dicionários simples."""
        a = {"key1": "value1", "key2": "value2"}
        b = {"key2": "new_value2", "key3": "value3"}
        
        result = _deep_merge(a, b)
        
        expected = {"key1": "value1", "key2": "new_value2", "key3": "value3"}
        assert result == expected

    def test_deep_merge_nested_dicts(self):
        """Testa merge de dicionários aninhados."""
        a = {"level1": {"level2": {"key1": "value1", "key2": "value2"}}}
        b = {"level1": {"level2": {"key2": "new_value2", "key3": "value3"}}}
        
        result = _deep_merge(a, b)
        
        expected = {"level1": {"level2": {"key1": "value1", "key2": "new_value2", "key3": "value3"}}}
        assert result == expected

    def test_deep_merge_empty_dicts(self):
        """Teste merge com dicionários vazios."""
        a = {}
        b = {"key1": "value1"}
        
        result = _deep_merge(a, b)
        
        assert result == {"key1": "value1"}

    def test_deep_merge_none_values(self):
        """Teste merge com valores None."""
        a = {"key1": "value1"}
        b = {"key1": None}
        
        result = _deep_merge(a, b)
        
        assert result == {"key1": None}

    def test_deep_merge_preserves_original(self):
        """Testa se o dicionário original é preservado."""
        a = {"key1": "value1", "key2": "value2"}
        b = {"key3": "value3"}
        
        result = _deep_merge(a, b)
        
        # O dicionário original deve permanecer inalterado
        assert a == {"key1": "value1", "key2": "value2"}
        assert result == {"key1": "value1", "key2": "value2", "key3": "value3"}


class TestLoadSettingsDict:
    """Testes para a função load_settings_dict."""

    @patch("app.config.loader.os.path.exists")
    @patch("app.config.loader.os.path.dirname")
    @patch("app.config.loader.os.path.abspath")
    @patch("app.config.loader.os.path.join")
    @patch("app.config.loader.os.getenv")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_settings_dict_with_env_file(
        self, mock_file, mock_getenv, mock_join, mock_abspath, mock_dirname, mock_exists
    ):
        """Testa carregamento de configurações com arquivo de ambiente."""
        # Setup mocks
        mock_getenv.side_effect = lambda key, default=None: "test" if key == "APP_ENV" else None
        mock_exists.return_value = True
        mock_abspath.side_effect = lambda path: f"/absolute/{path}"
        mock_dirname.return_value = "/absolute/path"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        # Mock YAML content
        base_config = {"app": {"name": "srv-email-google-sender"}, "debug": False}
        env_config = {"debug": True, "app": {"version": "1.0.0"}}
        
        def mock_yaml_load(content):
            if "application.yaml" in str(mock_file.call_args):
                return base_config
            else:
                return env_config
        
        with patch("yaml.safe_load", side_effect=mock_yaml_load):
            result = load_settings_dict()
        
        expected = {
            "app": {"name": "srv-email-google-sender", "version": "1.0.0"},
            "debug": True
        }
        assert result == expected

    @patch("app.config.loader.os.path.exists")
    @patch("app.config.loader.os.path.dirname")
    @patch("app.config.loader.os.path.abspath")
    @patch("app.config.loader.os.path.join")
    @patch("app.config.loader.os.getenv")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_settings_dict_without_env_file(
        self, mock_file, mock_getenv, mock_join, mock_abspath, mock_dirname, mock_exists
    ):
        """Testa carregamento de configurações sem arquivo de ambiente."""
        # Setup mocks
        mock_getenv.side_effect = lambda key, default=None: "test" if key == "APP_ENV" else None
        mock_exists.side_effect = lambda path: "application.yaml" in path
        mock_abspath.side_effect = lambda path: f"/absolute/{path}"
        mock_dirname.return_value = "/absolute/path"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        # Mock YAML content
        base_config = {"app": {"name": "srv-email-google-sender"}, "debug": False}
        
        with patch("yaml.safe_load", return_value=base_config):
            result = load_settings_dict()
        
        assert result == base_config

    @patch("app.config.loader.os.path.exists")
    @patch("app.config.loader.os.path.dirname")
    @patch("app.config.loader.os.path.abspath")
    @patch("app.config.loader.os.path.join")
    @patch("app.config.loader.os.getenv")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_settings_dict_with_env_variables(
        self, mock_file, mock_getenv, mock_join, mock_abspath, mock_dirname, mock_exists
    ):
        """Testa carregamento de configurações com variáveis de ambiente."""
        # Setup mocks
        def mock_getenv_side_effect(key, default=None):
            env_vars = {
                "APP_ENV": "test",
                "DEBUG": "true",
                "APP_NAME": "test-app",
                "RABBITMQ_HOST": "rabbitmq.example.com"
            }
            return env_vars.get(key)
        
        mock_getenv.side_effect = mock_getenv_side_effect
        mock_exists.return_value = True
        mock_abspath.side_effect = lambda path: f"/absolute/{path}"
        mock_dirname.return_value = "/absolute/path"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        # Mock YAML content
        base_config = {
            "app": {"name": "srv-email-google-sender"},
            "debug": False,
            "rabbitmq": {"host": "localhost"}
        }
        
        with patch("yaml.safe_load", return_value=base_config):
            result = load_settings_dict()
        
        expected = {
            "app": {"name": "test-app"},
            "debug": True,
            "rabbitmq": {"host": "rabbitmq.example.com"}
        }
        assert result == expected

    @patch("app.config.loader.os.path.exists")
    @patch("app.config.loader.os.path.dirname")
    @patch("app.config.loader.os.path.abspath")
    @patch("app.config.loader.os.path.join")
    @patch("app.config.loader.os.getenv")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_settings_dict_with_boolean_env_variables(
        self, mock_file, mock_getenv, mock_join, mock_abspath, mock_dirname, mock_exists
    ):
        """Testa carregamento de configurações com variáveis booleanas de ambiente."""
        # Setup mocks
        def mock_getenv_side_effect(key, default=None):
            env_vars = {
                "APP_ENV": "test",
                "DEBUG": "true",
                "ENABLE_FEATURE": "1",
                "DISABLE_FEATURE": "false"
            }
            return env_vars.get(key)
        
        mock_getenv.side_effect = mock_getenv_side_effect
        mock_exists.return_value = True
        mock_abspath.side_effect = lambda path: f"/absolute/{path}"
        mock_dirname.return_value = "/absolute/path"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        # Mock YAML content
        base_config = {
            "debug": False,
            "features": {
                "enable_feature": False,
                "disable_feature": True
            }
        }
        
        with patch("yaml.safe_load", return_value=base_config):
            result = load_settings_dict()
        
        expected = {
            "debug": True,
            "features": {
                "enable_feature": True,
                "disable_feature": False
            }
        }
        assert result == expected

    @patch("app.config.loader.os.path.exists")
    @patch("app.config.loader.os.path.dirname")
    @patch("app.config.loader.os.path.abspath")
    @patch("app.config.loader.os.path.join")
    @patch("app.config.loader.os.getenv")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_settings_dict_with_empty_yaml(
        self, mock_file, mock_getenv, mock_join, mock_abspath, mock_dirname, mock_exists
    ):
        """Testa carregamento de configurações com YAML vazio."""
        # Setup mocks
        mock_getenv.side_effect = lambda key, default=None: "test" if key == "APP_ENV" else None
        mock_exists.return_value = True
        mock_abspath.side_effect = lambda path: f"/absolute/{path}"
        mock_dirname.return_value = "/absolute/path"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        with patch("yaml.safe_load", return_value=None):
            result = load_settings_dict()
        
        assert result == {}

    @patch("app.config.loader.os.path.exists")
    @patch("app.config.loader.os.path.dirname")
    @patch("app.config.loader.os.path.abspath")
    @patch("app.config.loader.os.path.join")
    @patch("app.config.loader.os.getenv")
    def test_load_settings_dict_file_not_found(
        self, mock_getenv, mock_join, mock_abspath, mock_dirname, mock_exists
    ):
        """Testa carregamento de configurações quando arquivo não é encontrado."""
        # Setup mocks
        mock_getenv.side_effect = lambda key, default=None: "test" if key == "APP_ENV" else None
        mock_exists.return_value = False
        mock_abspath.side_effect = lambda path: f"/absolute/{path}"
        mock_dirname.return_value = "/absolute/path"
        mock_join.side_effect = lambda *args: "/".join(args)
        
        with pytest.raises(FileNotFoundError):
            load_settings_dict()


class TestSettings:
    """Testes para a classe Settings."""

    def test_settings_creation(self):
        """Testa criação de instância Settings."""
        settings = Settings(
            app_name="test-app",
            version="1.0.0",
            environment="test",
            debug=True,
            rabbitmq={"host": "localhost"},
            gmail={"service_account_file": "test.json"}
        )
        
        assert settings.app_name == "test-app"
        assert settings.version == "1.0.0"
        assert settings.environment == "test"
        assert settings.debug is True
        assert settings.rabbitmq == {"host": "localhost"}
        assert settings.gmail == {"service_account_file": "test.json"}

    def test_settings_default_values(self):
        """Testa valores padrão da classe Settings."""
        settings = Settings(
            app_name="test-app",
            version="1.0.0",
            environment="test",
            debug=True,
            rabbitmq={"host": "localhost"},
            gmail={"service_account_file": "test.json"}
        )
        
        # Verifica se os valores padrão estão corretos
        assert settings.app_name == "test-app"
        assert settings.version == "1.0.0"
        assert settings.environment == "test"
        assert settings.debug is True

    @patch("app.config.loader.load_settings_dict")
    def test_settings_from_config(self, mock_load_settings):
        """Testa criação de Settings a partir de configuração."""
        mock_config = {
            "app_name": "test-app",
            "version": "1.0.0",
            "environment": "test",
            "debug": True,
            "rabbitmq": {"host": "localhost"},
            "gmail": {"service_account_file": "test.json"}
        }
        mock_load_settings.return_value = mock_config
        
        settings = Settings.from_config()
        
        assert settings.app_name == "test-app"
        assert settings.version == "1.0.0"
        assert settings.environment == "test"
        assert settings.debug is True
        assert settings.rabbitmq == {"host": "localhost"}
        assert settings.gmail == {"service_account_file": "test.json"}

    def test_settings_validation(self):
        """Testa validação de Settings."""
        # Teste com configuração válida
        settings = Settings(
            app_name="test-app",
            version="1.0.0",
            environment="test",
            debug=True,
            rabbitmq={"host": "localhost"},
            gmail={"service_account_file": "test.json"}
        )
        
        # Não deve lançar exceção
        assert settings is not None

    def test_settings_rabbitmq_config(self):
        """Testa configuração RabbitMQ específica."""
        rabbitmq_config = {
            "host": "rabbitmq.example.com",
            "port": 5672,
            "user": "guest",
            "password": "guest",
            "vhost": "/",
            "queues": {
                "email_send": "email.queue",
                "email_send_dlt": "email.dlt.queue"
            },
            "exchanges": {
                "email_exchange": "email.exchange",
                "email_exchange_dlt": "email.dlt.exchange"
            },
            "routing_keys": {
                "email_send": "email.send",
                "email_failed": "email.failed"
            },
            "retry": {
                "max_attempts": 3,
                "initial_delay_seconds": 5
            }
        }
        
        settings = Settings(
            app_name="test-app",
            version="1.0.0",
            environment="test",
            debug=True,
            rabbitmq=rabbitmq_config,
            gmail={"service_account_file": "test.json"}
        )
        
        assert settings.rabbitmq == rabbitmq_config
        assert settings.rabbitmq["host"] == "rabbitmq.example.com"
        assert settings.rabbitmq["port"] == 5672
        assert settings.rabbitmq["queues"]["email_send"] == "email.queue"

    def test_settings_gmail_config(self):
        """Testa configuração Gmail específica."""
        gmail_config = {
            "service_account_file": "service-account.json",
            "scopes": ["https://www.googleapis.com/auth/gmail.send"],
            "subject_prefix": "[APP]"
        }
        
        settings = Settings(
            app_name="test-app",
            version="1.0.0",
            environment="test",
            debug=True,
            rabbitmq={"host": "localhost"},
            gmail=gmail_config
        )
        
        assert settings.gmail == gmail_config
        assert settings.gmail["service_account_file"] == "service-account.json"
        assert settings.gmail["scopes"] == ["https://www.googleapis.com/auth/gmail.send"]
        assert settings.gmail["subject_prefix"] == "[APP]"
