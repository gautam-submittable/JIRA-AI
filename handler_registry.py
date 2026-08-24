import json, os

class HandlerRegistry:
    def __init__(self, path='handler.json'):
        self.path = path
        self._data = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return {}
        with open(self.path, 'r') as f:
            return json.load(f)

    def _save(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=2)

    def register_handler(self, event, handler_name, action=None):
        """Register a handler for an event.

        Args:
            event (str): The event name.
            handler_name (str): Unique identifier of the handler.
            action (str, optional): The action type (e.g., 'Organization' or 'Cycle').
                If not provided, it will be read from the global config.

        Returns:
            dict: The newly added mapping.

        Raises:
            ValueError: If the handler_name is already registered.
        """
        if not handler_name:
            raise ValueError('handler_name must be a non‑empty string')
        if action is None:
            from config import get_action
            action = get_action()
        registry = self._data
        if handler_name in registry.get('handlers', {}):
            raise ValueError(f'Handler {handler_name!r} is already registered')
        mapping = {
            'event': event,
            'handler': handler_name,
            'action': action
        }
        registry.setdefault('handlers', {})[handler_name] = mapping
        self._save(registry)
        return mapping

    def get_registry(self):
        return self._data
