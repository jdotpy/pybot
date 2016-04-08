import random
import re

class BasePlugin():
    def __init__(self, bot, options):
        self.bot = bot
        self.options = options

    def percent_chance(self, percent):
        i = random.random() * 100
        if i < percent:
            return True
        else:
            return False

class HearMessagePlugin(BasePlugin):
    hear_group = True
    hear_pm = True
    hear_regexes = []
    hear_regex = None
    default_response = 'I hear you'

    def __init__(self, *args, **kwargs):
        super(HearMessagePlugin, self).__init__(*args, **kwargs)
        hear_option = self.options.get('hear', None)
        self.hear_pm = self.options.get('hear_pm', self.hear_pm)
        self.hear_group = self.options.get('hear_group', self.hear_group)
        if isinstance(hear_option, list):
            self.hear_regexes = [re.compile(r) for r in hear_option]
        elif isinstance(hear_option, str):
            self.hear_regex = re.compile(hear_option)

    def on_message(self, message):
        group = message.is_group_message()
        if group and not self.hear_group:
            return False
        elif not self.hear_pm:
            return False
        if self.hear_regex:
            hear_regexes = [self.hear_regex]
        else:
            hear_regexes = self.hear_regexes

        hear_args = [message]
        hear = False
        if hear_regexes:
            for regex in hear_regexes:
                match = re.match(regex, message.content)
                if match:
                    hear = True
                    hear_args.append(match)
                    break

        if not hear:
            return False

        results = self.hear(*hear_args)
        if isinstance(results, str):
            self.bot.send_message(message.reply_to(), results)
            
    def hear(self):
        return self.default_response

class SimpleResponder(HearMessagePlugin):
    def hear(self, message, match=None):
        if not self.percent_chance(self.options.get('chance', 100)):
            return False
        responses = self.options.get('say', self.default_response)
        if isinstance(responses, list):
            response = str(random.choice(responses))
        else:
            response = str(responses)
        return response

class Shutdown(BasePlugin):
    hear_group = False

    def hear(self, message):
        if message.content == 'shutdown':
            self.bot.shutdown()
