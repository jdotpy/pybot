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
        '^roll (\d{0,2}d\d{1,100}[+-]?\d* ?)*$',
    ]
    coins = ['Heads', 'Tails']

    def hear(self, message, match=None):
        # Parse the dice
        dice = match.group(0)[4:].split(' ')
        dice = list(filter(lambda x: bool(x), dice))
        if len(dice) == 0:
            dice.append('d6')

        # Roll 
        rolls = []
        modifiers = []
        for die in dice:
            modifier = 0
            count, size = die.split('d')
            if '+' in size:
                size, modifier = size.split('+')
            elif '-' in size:
                size, modifier = size.split('-')
                modifier = '-' + modifier 
            if modifier:
                modifiers.append(int(modifier))
            if not count:
                count = 1
            for i in range(int(count)):
                rolls.append(random.randint(1, int(size)))

        # Format
        if len(rolls) == 1:
            return str(rolls[0] + sum(modifiers))
        else:
            return '{} ({})'.format(
                str(sum(rolls) + sum(modifiers)),
                ', '.join([str(r) for r in rolls])       
            )
