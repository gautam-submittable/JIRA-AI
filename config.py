import json, os

CONFIG_PATH = 'config.json'

_DEFAULTS = {
    'action': 'Organization'
}

def load_config():
    """Load configuration from config.json, falling back to defaults."""
    if not os.path.exists(CONFIG_PATH):
        return _DEFAULTS.copy()
    with open(CONFIG_PATH, 'r') as f:
        data = json.load(f)
    cfg = _DEFAULTS.copy()
    cfg.update(data)
    return cfg

def get_action():
    """Return the configured action (e.g., 'Organization' or 'Cycle')."""
    return load_config().get('action', _DEFAULTS['action'])
