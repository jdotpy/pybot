from .core  import HearMessagePlugin
import random

class GoogleCS(HearMessagePlugin):
    hear_regex = '^google (?P<cmd>search|image|animate)(?P<random> random)? (?P<query>.*)'

    def google_search(self, message, query, search_type):
        params = {
            'key': self.options.get('key', ''),
            'cx': self.options.get('cx', ''),
            'num': '10',
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
            return None
        if 'error' in results:
            self.bot.send_message(message.reply_to(), 'Googling error: ' + str(results['error']))
            return None
        return results['items']

    def hear(self, message, match=None):
        search_type = match.group('cmd')
        query = match.group('query')
        choose_random = match.group('random') is not None

        results = self.google_search(message, query, search_type)
        if results is None:
            return False

        if choose_random:
            selected = random.choice(results)
        else:
            selected = results[0]
        return selected['link']
