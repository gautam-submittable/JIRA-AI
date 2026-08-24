from handler_registry import HandlerRegistry
from config import get_action

def main(event, handler_name):
    """Register a handler for the given event.

    This function can be called from tests or a real command line interface.
    """
    registry = HandlerRegistry()
    action = get_action()
    mapping = registry.register_handler(event, handler_name, action=action)
    return mapping

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Usage: python register_handler.py <event> <handler_name>')
        sys.exit(1)
    ev, hdl = sys.argv[1], sys.argv[2]
    try:
        result = main(ev, hdl)
        print('Registered:', result)
    except ValueError as e:
        print('Error:', e)
        sys.exit(1)
