import pytest
from app.config import Config

def test_config_loading():
    config = Config()
    assert config.database_url is not None
    assert config.redis_url is not None 