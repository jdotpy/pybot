import unittest

from .storage.memory import RAMStorage
from .storage import redis

class StorageTestCase(unittest.TestCase):
    storage_backends = {
        RAMStorage,
        redis.BaseRedisStorage,
        redis.RedisJSONStorage,
        redis.RedisPickleStorage,
    }

    test_key = 'my_key'
    test_invalid_key = 'not_my_key'
    test_string_value = 'foobar'
    test_complex_value = {'foo': 'bar'}
    test_default = 'not a none value'

    def test_backends(self):
        for Backend in self.storage_backends:
            storage = Backend({})

            self.assertEqual(storage.get(self.test_invalid_key), None)
            self.assertEqual(storage.get(self.test_invalid_key, default=self.test_default), self.test_default)

            storage.set(self.test_key, self.test_string_value)
            self.assertEqual(storage.get(self.test_key), self.test_string_value)

            if storage.complex_values:
                storage.set(self.test_key, self.test_complex_value)
                self.assertEqual(storage.get(self.test_key), self.test_complex_value)
