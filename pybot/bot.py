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
        return []

    def run(self):
        self.backend.connect()
        self.backend.process(block=False)
        time.sleep(10)
        sys.exit(0)
        
    def on_message(self, message):
        print('...on message :)', str(message))

    def send_message(self, recipient, content):
        self.backend.send_message(recipient, content)
