from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

from ..bot import Message

class XMPPBackend(ClientXMPP):
    MUC_MAXHISTORY = 0

    def __init__(self, bot, user=None, password=None, server=None, nickname=None, muc=False, rooms=None):
        self.bot = bot
        jid = user + '@' + server
        self.nick = nickname
        self.muc = muc
        self.rooms = rooms or []

        ClientXMPP.__init__(self, jid, password)

        if self.muc:
            self.register_plugin('xep_0045')

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        for room in self.rooms:
            self['xep_0045'].joinMUC(room, self.nick, maxhistory=self.MUC_MAXHISTORY)
            self.send_message(room, 'wazzzzzuuuuup boyz????')

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg_from = msg['nick']
            msg_to = self.nick
            content = str(msg)
            self.bot.on_message(Message(
                msg_from, 
                msg_to, 
                content, 
                original=msg
            ))
        elif msg['type'] == 'groupchat':
            content = str(msg)
            msg_from = msg['mucnick']
            msg_to = str(msg['to']).split('/')[0]
            self.bot.on_message(Message(
                msg_from, 
                msg_to, 
                content, 
                room=msg_to,
                original=msg
            ))
        else:
            print('...ignoring unknown message type:', msg['type'])

    ## Begin PyBot backend support
    def start(self):
        self.connect()
        self.process(block=False)

    def send_message(self, recipient, content):
        if recipient in self['xep_0045'].rooms:
            mtype='groupchat'
        else:
            mtype='chat'
        super(XMPPBackend, self).send_message(
            mto=recipient,
            mbody=content,
            mtype=mtype
        )
