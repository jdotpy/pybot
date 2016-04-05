class RAMStorage():
    complex_values = True

    def __init__(self, config):
        self.config = config
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)
