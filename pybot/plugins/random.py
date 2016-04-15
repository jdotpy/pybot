from .core import SimpleResponder
import random

class CoinFlip(SimpleResponder):
    hear_regex = '^coin flip$'
    coins = ['Heads', 'Tails']

    def hear(self, message, match=None):
        return random.choice(self.coins)

class RandomNumber(SimpleResponder):
    hear_regex = '^random number (\d+),? ?(\d+)?$'
    coins = ['Heads', 'Tails']

    def hear(self, message, match=None):
        numbers = match.groups()
        if len(numbers) == 2:
            start, end = int(numbers[0]), int(numbers[1])
        else:
            start = 0
            end = numbers[0]
        return str(random.randint(start, end))

class PickRandom(SimpleResponder):
    hear_regex = '^(choose|pick) random (.+)$'

    def hear(self, message, match=None):
        params = match.group(2)
        options = list(filter(lambda x: bool(x), params.split(',')))
        return random.choice(options)
