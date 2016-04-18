from .core import SimpleResponder

class ChuckNorris(SimpleResponder):
    hear_regex = r'tell me about (\w+) (\w+)'
    base_url = 'http://api.icndb.com/jokes/random'

    def hear(self, message, match=None):
        first_name, last_name = match.groups()
        params = {
            'firstName': first_name,
            'lastName': last_name,
            'exclude': '[' + ','.join(self.options.get('exclude', [])) + ']'
        }
        result_code, response = self.bot.web('GET', self.base_url, params=params)
        if result_code:
            return response.json()['value']['joke']
        else:
            return 'Chuck norris error: ' + str(response)
