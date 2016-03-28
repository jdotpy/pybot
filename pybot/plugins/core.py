from ..bot import BasePlugin

class CoreBotCommands(BasePlugin):
    def process_message(self, message):
        print('core', message.content)
        if message.content == 'shutdown':
            print('....shutting down')
            self.bot.shutdown()
