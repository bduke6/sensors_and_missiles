import pytest # type: ignore
import os
from src.config import Config

def test_load_config():
    config = Config('src/config.yaml')
    assert config.get('environment.max_time') == 50
    assert config.get('environment.log_directory') == './logs'
    assert config.get_bool('environment.display_plot') is False

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        Config('nonexistent.yaml')

def test_invalid_yaml():
    with open('invalid.yaml', 'w') as f:
        f.write("invalid: [unbalanced brackets")
    with pytest.raises(Exception):
        Config('invalid.yaml')
    os.remove('invalid.yaml')

def test_default_value():
    config = Config('src/config.yaml')
    assert config.get('nonexistent.key', 'default_value') == 'default_value'

def test_missing_key_raises_keyerror():
    config = Config('src/config.yaml')
    with pytest.raises(KeyError):
        config.get('nonexistent.key')
