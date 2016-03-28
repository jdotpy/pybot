from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

from ..bot import Message, User
import time

class XMPPBackend(ClientXMPP):
    MUC_MAXHISTORY = "0"

    def __init__(self, bot, user=None, password=None, server=None, nickname=None, muc=False, rooms=None):
        self.bot = bot
        jid = user + '@' + server
        self.nick = nickname
        self.use_muc = muc
        self.rooms = rooms or []

        ClientXMPP.__init__(self, jid, password)

        if self.use_muc:
            self.register_plugin('xep_0045')
            self.muc = self['xep_0045']

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.startup_timestamp = time.time()
        self.send_presence()
        self.get_roster()

        for room in self.rooms:
            self.muc.joinMUC(room, self.nick, maxhistory=self.MUC_MAXHISTORY)

    def message(self, msg):
        ts = msg.xml.get('ts', None)
        if ts and float(ts) < self.startup_timestamp:
            pass
            print('Ignoring old message: ', msg['body'])
        elif msg['type'] in ('chat', 'normal'):
            msg_from = msg['from'].bare
            msg_to = msg['to'].bare
            content = msg['body']
            self.bot.on_message(Message(
                msg_from, 
                msg_to, 
                content, 
                original=msg
            ))
        elif msg['type'] == 'groupchat':
            msg_from = msg['mucnick']
            msg_to = msg['to'].bare
            content = msg['body']
            self.bot.on_message(Message(
                msg_from, 
                msg_to, 
                content, 
                room=msg_to,
                original=msg
            ))
        else:
            print('...ignoring unknown message type:', msg['type'])

    def _parse_roster_query(self, result):
        users = []
        raw_user_items = result['roster']['items']
        for username, user_data in raw_user_items.items():
            users.append(User(
                username=username,
                name=user_data.get('name', ''),
                data=user_data
            ))
        return users

    ## Begin PyBot backend support
    def start(self):
        self.connect()
        self.process(block=False)
        for room in self.rooms:
            self.send_message(room, 'wazzzzzuuuuup boyz????')

    def get_users(self, room=None):
        if room is None:
            roster = self.get_roster()
        else:
            roster = self.muc.rooms[room].get_roster()
        users = self._parse_roster_query(roster)
        return users

    def shutdown(self):
        pass

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
