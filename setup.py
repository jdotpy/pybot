#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pybot',
    version='0.1',
    description='Easily extendable chatbot with swappable backends/plugins and xmpp integration',
    author='KJ',
    author_email='<redacted>',
    url='<TBD>',
    packages=[
        'pybot',
        'pybot.backends',
        'pybot.plugins',
        'pybot.storage',
    ],
    install_requires=[
        'sleekxmpp',
        'requests',
        'pyyaml',
        'quickconfig'
    ],
)
