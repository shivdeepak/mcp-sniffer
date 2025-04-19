from mcp_sniffer.config import AppConfig


def test_config():
    config = AppConfig()
    assert config.LISTEN_PORT == 3002
    assert config.UPSTREAM_PORT == 3001


def test_config_from_file():
    config = AppConfig(LISTEN_PORT=8002, UPSTREAM_PORT=8001)
    assert config.LISTEN_PORT == 8002
    assert config.UPSTREAM_PORT == 8001
