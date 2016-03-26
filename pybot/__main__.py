from quickconfig import Configuration
from .bot import PyBot
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
    config = Configuration('config.yaml', Configuration.Arg('--config'))
    bot = PyBot(config)
    bot.run()
