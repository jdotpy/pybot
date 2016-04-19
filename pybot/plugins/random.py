from .core import SimpleResponder
import random

class CoinFlip(SimpleResponder):
    hear_regexes = [
        '^coin flip$',
        '^flip coin$'
    ]
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
        if ',' in params:
            options = params.split(',')
        else:
            options = params.split(' ')
        options = list(filter(lambda x: bool(x), options))
        return random.choice(options)

class DiceRoll(SimpleResponder):
    hear_regexes = [
        '^roll (d\d+ ?)*$',
    ]
    coins = ['Heads', 'Tails']

    def hear(self, message, match=None):
        dice = match.group(0)[4:].split(' ')
        dice = list(filter(lambda x: bool(x), dice))
        if len(dice) == 0:
            dice.append('d6')
        rolls = []
        for die in dice:
            result = random.randint(1, int(die[1:]))
            rolls.append(str(result))
        return ' '.join(rolls)
