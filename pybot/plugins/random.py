from .core import SimpleResponder
import random
import re

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
        '^roll ?(\d{0,2}d\d{1,100}[+-/*]?\d* ?)*$',
    ]
    coins = ['Heads', 'Tails']
    die_regex = r'(?P<count>\d{0,2})d((?P<sides>\d{1,100})(?P<operator>[-+/*])?(?P<modifier>\d*)?)'

    def _parse_die(self, text):
        match = re.match(self.die_regex, text)
        count = match.group('count')
        if not count:
            count = 1
        else:
            count = int(count)
        operator = match.group('operator')
        if not operator:
            operator = None
        modifier = match.group('modifier')
        if not modifier:
            modifier = '0'
        return count, int(match.group('sides')), operator, int(modifier)

    def hear(self, message, match=None):
        # Parse the dice
        dice = match.group(0)[4:].split(' ')
        dice = list(filter(lambda x: bool(x), dice))
        if len(dice) == 0:
            dice.append('d6')

        # Roll 
        rolls = []
        total = 0
        for die in dice:
            die_sum = 0
            count, sides, operator, modifier = self._parse_die(die)
            for i in range(count):
                die_roll = random.randint(1, int(sides))
                die_sum += die_roll
                rolls.append(die_roll)
            if operator:
                if operator == '+':
                    die_sum += modifier
                elif operator == '-':
                    die_sum -= modifier
                elif operator == '/':
                    die_sum = int(die_sum / modifier)
                elif operator == '*':
                    die_sum = die_sum * modifier
            total += die_sum

        # Format
        if len(rolls) == 1:
            return str(total)
        else:
            return '{} ({})'.format(
                str(total),
                ', '.join([str(r) for r in rolls])       
            )
