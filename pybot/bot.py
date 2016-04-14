import time
import requests
import random
import sys
from .utils import import_obj
import re

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

    def reply_to(self):
        if self.is_group_message():
            return self.room
        else:
            return self.sender

class ChatEntity():
    def __eq__(self, other):
        if isinstance(other, ChatEntity):
            return self.get_id() == other.get_id()
        else:
            return False

    def __str__(self):
        return self.get_id()

class User(ChatEntity):
    def __init__(self, username, name, data=None):
        self.username = username
        self.name = name
        self.data = data or {}

    def get_id(self):
        return self.username

class Room(ChatEntity):
    def __init__(self, room_id, data=None):
        self.room_id = room_id
        self.data = data or {}

    def get_id(self):
        return self.room_id

class PyBot():
    DEFAULT_MEMORY = 'pybot.storage.memory.RAMStorage'

    def __init__(self, config):
        self.config = config
        self.memory = self._load_memory(config)
        self.backend = self._load_backend(config)
        self.plugins = self._load_plugins(config)
        self.bot_user = self.backend.bot_user
        self.session = self.new_web_session()

    def new_web_session(self, **config_override):
        web_config = self.config.get('web', {}).copy()
        web_config.update(config_override)
        session = requests.Session()

        #  Proxy
        http_proxy = web_config.get('http_proxy')
        https_proxy = web_config.get('https_proxy')
        proxies = {}
        if http_proxy or https_proxy:
            if http_proxy:
                proxies['http'] = http_proxy
            if https_proxy:
                proxies['https'] = https_proxy
        session.proxies = proxies

        # Certs
        session.verify = web_config.get('verify', True)
        session.keep_alive = web_config.get('keep_alive', True)
        return session

    def _load_memory(self, config):
        memory_settings = self.config.get('memory', {}).copy()
        memory_path = memory_settings.pop('path', self.DEFAULT_MEMORY)
        Memory = import_obj(memory_path)
        return Memory(self, **memory_settings)

    def _load_backend(self, config):
        backend_settings = self.config.get('backend', {}).copy()
        backend_path = backend_settings.pop('path')
        Backend = import_obj(backend_path)
        return Backend(self, **backend_settings)

    def _load_plugins(self, config):
        plugins = []
        for plugin_config in self.config.get('plugins', []):
            path = plugin_config.pop('path')
            if plugin_config == None:
                plugin_config = {}
            Plugin = import_obj(path)
            plugins.append(Plugin(self, plugin_config))
        return plugins

    def _emit_plugin_event(self, event_name, *args, **kwargs):
        for plugin in self.plugins:
            handler = getattr(plugin, event_name, None)
            if handler is not None:
                handler(*args, **kwargs)

    def run(self):
        self.backend.start()
        self._emit_plugin_event('on_startup')

    def _on_message(self, message):
        self._emit_plugin_event('on_message', message)
        # Hear events 

    def bot_user():
        return self.backend.bot_user

    ## Intended for plugin access
    def get_users(self, room=None):
        return self.backend.get_users(room=room)

    def shutdown(self):
        self.backend.shutdown()
        sys.exit(0)

    def send_message(self, recipient, content):
        self.backend.send_message(recipient, content)

    def web(self, *args, **kwargs):
        session = kwargs.pop('session', self.session)
        attempts = kwargs.pop('attempts', 3)

        response = None
        exception = None
        for i in range(attempts):
            print('Retrying')
            try:
                response = self.session.request(*args, **kwargs)
                if i == 0:
                    raise ValueError()
                print('Got a response')
                break
            except (
                requests.exceptions.TooManyRedirects,
                requests.exceptions.URLRequired,
            ) as e:
                # This are exceptions we dont want to execute a retry on
                print('Got a no-retry exception')
                exception = e
                break
            except Exception as e:
                print('Got a retry-able exception')
                exception = e
        if response:
            return response.status_code, response
        else:
            return None, e

