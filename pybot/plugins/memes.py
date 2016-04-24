from .core import SimpleResponder

import re

class ImgFlipMemeGen(SimpleResponder):
    hear_regexes = [
        'memegen (.*)',
    ]
    base_url = 'https://api.imgflip.com/caption_image'

    meme_types = [
        {
          'regex': '(.*) (Y U NO .*)',
          'template': 61527
        },
        {
          'regex': "(I DON'?T ALWAYS .*) (BUT WHEN I DO .*)",
          'template': 61532
        },
        {
          'regex': '(.*) ?(SUCCESS|NAILED IT.*)',
          'template': 61544
        },
        {
          'regex': '(.*) (ALL the .*)',
          'template': 61533
        },
        {
          'regex': '(.*) (TOO DAMN .*)',
          'template': 61580
        },
        #{
        #  'regex': '(GOOD NEWS EVERYONE[,.!]?) (.*)',
        #  'template': 
        #},
        {
          'regex': '(NOT SURE IF .*) (OR .*)',
          'template': 61520
        },
        {
          'regex': '(YO DAWG) (.*)',
          'template': 101716
        },
        #{
        #  'regex': '(ALL YOUR .*) (ARE BELONG TO US)',
        #  'template': 61579
        #},
        #{
        #  'regex': '(.*) (You\'?re gonna have a bad time)',
        #  'template': 61579
        #},
        {
          'regex': '(one does not simply) (.*)',
          'template': 61579
        },
        {
          'regex': '(AM I THE ONLY ONE AROUND HERE) (.*)',
          'template': 259680
        },
        {
          'regex': '(PREPARE|BRACE YOURSELF|YOURSELVES) (.*)',
          'template': 61546
        },
        {
          'regex': '(WHAT IF I TOLD YOU) (.*)',
          'template': 100947
        },
        {
          'regex': '(.*),? (.* EVERYWHERE)',
          'template': 100947
        },
    ]
    def _query(self, template_id, line_one, line_two=''):
        params = {
            'username': self.options.get('username'),
            'password': self.options.get('password'),
            'template_id': str(template_id),
            'text0': line_one,
            'text1':line_two
        }
        status_code, response = self.bot.web('GET', self.base_url, params=params, verify=False)
        if not status_code:
            return 'Error:' + str(response)

        results = response.json()
        if not results['success']:
            return 'Error: ' + str(results)
        else:
            return results['data']['url']

    def hear(self, message, match=None):
        text = match.group(1)
        for mt in self.meme_types:
            mt_match = re.match(mt['regex'], text, re.I)
            if mt_match:
                return self._query(mt['template'], *mt_match.groups())
                break
