import pytest
from wordpress_post_mcp.config import load_config
from wordpress_post_mcp.errors import ConfigurationError


def test_load_config_returns_config_when_all_envvars_set(monkeypatch):
    monkeypatch.setenv("WP_URL", "https://example.com")
    monkeypatch.setenv("WP_USERNAME", "user")
    monkeypatch.setenv("WP_APP_PASSWORD", "pass")

    config = load_config()

    assert config.url == "https://example.com"
    assert config.username == "user"
    assert config.app_password == "pass"


@pytest.mark.parametrize("missing_var", ["WP_URL", "WP_USERNAME", "WP_APP_PASSWORD"])
def test_load_config_raises_when_envvar_missing(monkeypatch, missing_var):
    monkeypatch.setenv("WP_URL", "https://example.com")
    monkeypatch.setenv("WP_USERNAME", "user")
    monkeypatch.setenv("WP_APP_PASSWORD", "pass")
    monkeypatch.delenv(missing_var)

    with pytest.raises(ConfigurationError):
        load_config()


def test_load_config_normalizes_trailing_slash(monkeypatch):
    monkeypatch.setenv("WP_URL", "https://example.com/")
    monkeypatch.setenv("WP_USERNAME", "user")
    monkeypatch.setenv("WP_APP_PASSWORD", "pass")

    config = load_config()

    assert config.url == "https://example.com"
