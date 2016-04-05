import redis
import json
import pickle

class BaseRedisStorage():
    complex_values = False
    def __init__(self, config):
        self.redis = redis.Redis(
            host=config.get('storage.host', 'localhost'),
            port=config.get('storage.port', 6379),
            password=config.get('storage.password'),
        )

    def set(self, key, value):
        self.redis.set(key, self._value_prep(value))

    def get(self, key, default=None):
        value = self.redis.get(key)
        if value is None:
            return default
        return self._value_restore(value)

    def _value_prep(self, value):
        return value.encode('utf-8')

    def _value_restore(self, value):
        return value.decode('utf-8')

class RedisJSONStorage(BaseRedisStorage):
    complex_values = True
    def _value_prep(self, value):
        return json.dumps(value).encode('utf-8')

    def _value_restore(self, value):
        return json.loads(value.decode('utf-8'))

class RedisPickleStorage(RedisJSONStorage):
    complex_values = True
    def _value_prep(self, value):
        return pickle.dumps(value)

    def _value_restore(self, value):
        return pickle.loads(value)
