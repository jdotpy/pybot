import time
import sys
from .utils import import_obj

class Message():
    def __init__(self, sender, recipient, content, room=None, original=None):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.room = room
        self.original = original

    def __str__(self):
        if self.room:
            return '[{}::{}] {}'.format(
                str(self.room),
                str(self.sender), 
                self.content
            )
        else:
            return '[{} -> {}] {}'.format(
                str(self.sender),
                str(self.recipient),
                self.content
            )

    def is_group_message(self):
        return self.room is not None

class User():
    def __init__(self, username, name, data=None):
        self.username = username
        self.name = name
        self.data = data or {}

    def get_id(self):
        return self.username

    def __str__(self):
        return self.username

class Room():
    def __init__(self, room_id, data=None):
        self.room_id = room_id
        self.data = data or {}

    def get_id(self):
        return self.room_id

    def __str__(self):
        return self.room_id

class BasePlugin():
    def __init__(self, bot):
        self.bot = bot

    def process_message(self, message):
        pass

class PyBot():
    def __init__(self, config):
        self.config = config
        self.backend = self._load_backend(config)
        self.plugins = self._load_plugins(config)

    def _load_backend(self, config):
        backend_settings = self.config.get('backend', {}).copy()
        backend_path = backend_settings.pop('path')
        Backend = import_obj(backend_path)
        return Backend(self, **backend_settings)

    def _load_plugins(self, config):
        plugins = []
        for plugin_path in self.config.get('plugins', []):
            Plugin= import_obj(plugin_path)
            plugins.append(Plugin(self))
        return plugins

    def _emit_plugin_event(self, event_name, *args, **kwargs):
        for plugin in self.plugins:
            handler = getattr(plugin, event_name)
            handler(*args, **kwargs)

    def run(self):
        self.backend.start()
        self._emit_plugin_event('on_startup')

    def _on_message(self, message):
        print('...on message :)', str(message))
        self._emit_plugin_event('on_message', message)

    ## Intended for plugin access
    def get_users(self, room=None):
        return self.backend.get_users(room=room)

    def shutdown(self):
        self.backend.shutdown()
        sys.exit(0)

    def send_message(self, recipient, content):
        self.backend.send_message(recipient, content)
