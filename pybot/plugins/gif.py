from .google import GoogleCS 
from .core  import SimpleResponder

import re
import random

class GoogleRandomGif(GoogleCS):
    hear_regex = r'\b(\w{1,200})\.gif\b'

    def giphy_check(self, link):
        if '.giphy.com' in link and link.endswith('_s.gif'):
            new_link = link[:-6] + '.gif'
            return new_link
        return link

    def hear(self, message, match=None):
        query = match.group(1).replace('_', ' ')
        results = self.google_search(message, query, 'animate')
        if results is None:
            return False
        if self.options.get('best_quality', False):
            results.sort(key=lambda x: x['image']['byteSize'])
            selected = results[-1]
        else:
            selected = random.choice(results)
        self.bot.send_message(message.reply_to(), selected['link'])

class ImageBank(SimpleResponder):
    hear_regexes = [
        r'^save (?P<url>.{1,1000}) as (?P<name>\w{0,200})\.img$',
        r'\b(?P<name>\w{0,200})\.img\b'
    ]
    memory_prefix = 'img-bank:'

    def hear(self, message, match=None):
        name = match.group('name')
        try:
            url = match.group('url')
        except Exception as e:
            url = None

        if url:
            # This is a SET command
            images = self.bot.memory.get(self.memory_prefix + name, [])
            images.append(url)
            self.bot.memory.set(self.memory_prefix + name, images)
            return 'Saved. {}.img now has {} images.'.format(name, len(images))
        else:
            images = self.bot.memory.get(self.memory_prefix + name, [])
            if len(images) == 0:
                not_found = self.options.get('not_found')
                if not_found:
                    return not_found
                else:
                    return False
            url = random.choice(images)
            return url
