from ..bot import BasePlugin

class Shutdown(BasePlugin):
    hear_group = False

    def hear(self, message):
        if message.content == 'shutdown':
            self.bot.shutdown()

class Testing(BasePlugin):
    hear_regex = '^(\w+) .*'
    hear_group = False

    def hear(self, message, match=None):
        self.bot.send_message(message.reply_to(), 'I done heard that! ' +  match.group(1))
