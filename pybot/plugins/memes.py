from .core import SimpleResponder

import re

class MemeGen(SimpleResponder):
    hear_regexes = [
        'memegen (.*)',
    ]
    base_url = 'http://version1.api.memegenerator.net/Instance_Create'

    meme_types = [
        {
          'regex': 'Y U NO (.*)',
          'generatorID': 2,
          'imageID': 166088
        },
        {
          'regex': "I DON'?T ALWAYS (.*) BUT WHEN I DO (.*)",
          'generatorID': 74,
          'imageID': 2485
        },
        {
          'regex': 'O\s?RLY\?? ?(.*)/i',
          'generatorID': 920,
          'imageID': 117049
        },
        {
          'regex': '(.*) (SUCCESS|NAILED IT.*)',
          'generatorID': 121,
          'imageID': 1031
        },
        {
          'regex': '(.*) (ALL the .*)',
          'generatorID': 6013,
          'imageID': 1121885
        },
        {
          'regex': '(.*) (TOO DAMN .*)',
          'generatorID': 998,
          'imageID': 203665
        },
        {
          'regex': '(GOOD NEWS EVERYONE[,.!]?) (.*)',
          'generatorID': 1591,
          'imageID': 112464
        },
        {
          'regex': '(NOT SURE IF .*) (OR .*)',
          'generatorID': 305,
          'imageID': 84688
        },
        {
          'regex': '(YO DAWG .*) (SO .*)',
          'generatorID': 79,
          'imageID': 108785
        },
        {
          'regex': '(ALL YOUR .*) (ARE BELONG TO US)',
          'generatorID': 349058,
          'imageID': 2079825
        },
        {
          'regex': '(.*) (FUCK YOU)',
          'generatorID': 1189472,
          'imageID': 5044147
        },
        {
          'regex': '(.*) (You\'?re gonna have a bad time)',
          'generatorID': 825296,
          'imageID': 3786537
        },
        {
          'regex': '(one does not simply) (.*)',
          'generatorID': 274947,
          'imageID': 1865027
        },
        {
          'regex': '(it looks like you\'re|it looks like you) (.*)',
          'generatorID': 20469,
          'imageID': 1159769
        },
        {
          'regex': '(AM I THE ONLY ONE AROUND HERE) (.*)',
          'generatorID': 953639,
          'imageID': 4240352
        },
        {
          'regex': '(.*) (NOT IMPRESSED.*)',
          'generatorID': 1420809,
          'imageID': 5883168
        },
        {
          'regex': '(PREPARE YOURSELF) (.*)',
          'generatorID': 414926,
          'imageID': 2295701
        },
        {
          'regex': '(WHAT IF I TOLD YOU) (.*)',
          'generatorID': 1118843,
          'imageID': 4796874
        },
        {
          'regex': '(.*) (BETTER DRINK MY OWN PISS)',
          'generatorID': 92,
          'imageID': 89714
        },
    ]
    def _query(self, gen_id, image_id, line_one, line_two=''):
        params = {
            'username': self.options.get('username'),
            'password': self.options.get('password'),
            'imageID': str(image_id),
            'generatorID': str(gen_id),
            'languageCode': 'en',
            'text0': 'foo',
            'text1':'bar' 
        }
        response = self.bot.web.get(self.base_url, params=params)
        results = response.json()

        if results['errorMessage']:
            return results['errorMessage']
        else:
            return results['instanceImageUrl']

    def hear(self, message, match=None):
        text = match.group(1)
        for mt in self.meme_types:
            mt_match = re.match(mt['regex'], text, re.I)
            if mt_match:
                return self._query(mt['generatorID'], mt['imageID'], *mt_match.groups())
                break
