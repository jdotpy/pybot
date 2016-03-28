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
                self.room, 
                self.sender, 
                self.content
            )
        else:
            return '[{} -> {}] {}'.format(
                self.sender, 
                self.recipient, 
                self.content
            )

    def is_group_message():
        return self.room is not None

class User():
    def __init__(self, username, name, data=None):
        self.username = username
        self.name = name
        self.data = data or {}

class Room():
    def __init__(self, room_id, name, data=None):
        self.room_id = room_id
        self.name = name
        self.data = data

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

    def run(self):
        self.backend.start()
        time.sleep(5)
        users = self.get_users()
        print('We got users!', users)

    def get_users(self, room=None):
        return self.backend.get_users(room=room)

    def shutdown(self):
        self.backend.shutdown()
        sys.exit(0)
        
    def on_message(self, message):
        print('...on message :)', str(message))
        for plugin in self.plugins:
            plugin.process_message(message)    

    def send_message(self, recipient, content):
        self.backend.send_message(recipient, content)
