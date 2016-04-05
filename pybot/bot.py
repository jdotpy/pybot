import time
import requests
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

class BasePlugin():
    hear_pm = True
    hear_group = True
    hear_regex = None

    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings

    def on_message(self, message):
        pass

class PyBot():
    def __init__(self, config):
        self.config = config
        self.memory = self._load_memory(config)
        self.backend = self._load_backend(config)
        self.plugins = self._load_plugins(config)
        self.bot_user = self.backend.bot_user
        self.web = self.new_web_session()

    def new_web_session(self):
        session = requests.Session()

        #  Proxy
        http_proxy = self.config.get('web.http_proxy')
        https_proxy = self.config.get('web.https_proxy')
        proxies = {}
        if http_proxy or https_proxy:
            if http_proxy:
                proxies['http'] = http_proxy
            if https_proxy:
                proxies['https'] = https_proxy
        session.proxies = proxies

        # Certs
        session.verify = self.config.get('web.verify', True)
        return session

    def _load_memory(self, config):
        memory_settings = self.config.get('memory', {}).copy()
        memory_path = memory_settings.pop('path')
        Memory = import_obj(memory_path)
        return Memory(self, **memory_settings)

    def _load_backend(self, config):
        backend_settings = self.config.get('backend', {}).copy()
        backend_path = backend_settings.pop('path')
        Backend = import_obj(backend_path)
        return Backend(self, **backend_settings)

    def _load_plugins(self, config):
        plugins = []
        for plugin_path, plugin_settings in self.config.get('plugins', {}).items():
            if plugin_settings == None:
                plugin_settings = {}
            Plugin = import_obj(plugin_path)
            plugins.append(Plugin(self, plugin_settings))
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
        # Hear events 
        group = message.is_group_message()
        if group:
            hear_attribute = 'hear_group'
        else:
            hear_attribute = 'hear_pm'
        for plugin in self.plugins:
            if not getattr(plugin, hear_attribute):
                print('Skipping plugin', plugin, 'hear attribute:', hear_attribute)
                continue
            if plugin.hear_regex is not None:
                match = re.match(plugin.hear_regex, message.content)
                if match is not None:
                    plugin.hear(message, match)
                else:
                    print('skipping plugin', plugin, 'regex doesnt match')
                    continue
            else:
                plugin.hear(message)

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
