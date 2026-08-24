import json
import os
import pytest
from handler_registry import HandlerRegistry
from config import load_config, get_action

@pytest.fixture
def temp_registry(tmp_path):
    path = tmp_path / 'handler.json'
    path.touch()
    registry = HandlerRegistry(path=str(path))
    yield registry


def test_register_handler_success(temp_registry):
    mapping = temp_registry.register_handler('login', 'auth_handler', action='Organization')
    assert mapping == {
        'event': 'login',
        'handler': 'auth_handler',
        'action': 'Organization'
    }
    with open(temp_registry.path) as f:
        data = json.load(f)
    assert data['handlers']['auth_handler'] == mapping


def test_register_duplicate_handler_raises(temp_registry):
    temp_registry.register_handler('event1', 'my_handler')
    with pytest.raises(ValueError, match='already registered'):
        temp_registry.register_handler('event2', 'my_handler')


def test_invalid_handler_name_raises(temp_registry):
    with pytest.raises(ValueError, match='must be a non‑empty string'):
        temp_registry.register_handler('event', '')


def test_action_from_config(temp_registry, monkeypatch):
    monkeypatch.setattr('config.load_config', lambda: {'action': 'Cycle'})
    mapping = temp_registry.register_handler('cycle_event', 'cycle_handler')
    assert mapping['action'] == 'Cycle'
