from ..bot import BasePlugin
import random

class GoogleCS(BasePlugin):
    hear_regex = '^google (?P<cmd>search|image|animate)(?P<random> random)? (?P<query>.*)'

    def hear(self, message, match=None):
        search_type = match.group('cmd')
        query = match.group('query')
        choose_random = match.group('random') is not None

        params = {
            'key': self.settings.get('key', ''),
            'cx': self.settings.get('cx', ''),
            'fields': 'items(title,link)',
            'num': '8',
            'q': query,
        }

        if search_type in ('image', 'animate'):
            params['searchType'] = "image"
        if search_type == 'animate':
            params['fileType'] = 'gif'

        try:
            response = self.bot.web.get('https://www.googleapis.com/customsearch/v1', params=params)
            results = response.json()
        except Exception as e:
            self.bot.send_message(message.reply_to(), 'Googling error: ' + str(e))
            return False

        if 'error' in results:
            self.bot.send_message(message.reply_to(), 'Googling error: ' + str(results['error']))
            return False

        if choose_random:
            selected = random.choice(results['items'])
        else:
            selected = results['items'][0]

        self.bot.send_message(message.reply_to(), selected['link'])
