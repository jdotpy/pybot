from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

from ..bot import Message, User, Room
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

        all_users = self.get_users()
        self.users_by_username = {user.username: user for user in all_users}
        self.users_by_name = {user.name: user for user in all_users}

        for room in self.rooms:
            self.muc.joinMUC(room, self.nick, maxhistory=self.MUC_MAXHISTORY)

    def message(self, msg):
        # Determine if this was a event sent to us at connect time
        # grace is subtracted from startup_timestampin order to 
        # help prevent us from missing anything, and in case
        # time gets out of sync
        grace = 1
        ts = msg.xml.get('ts', None)
        if ts and float(ts) < (self.startup_timestamp - grace):
            print('Ignoring old message: ', msg['body'])
            return None

        # Parse event
        original = msg
        room = None
        if msg['type'] in ('chat', 'normal'):
            msg_from = self.users_by_username.get(msg['from'].bare, None)
            msg_to = self.users_by_username.get(msg['to'].bare, None)
            content = msg['body']
        elif msg['type'] == 'groupchat':
            msg_from = self.users_by_name.get(msg['mucnick'], None)
            msg_to = Room(msg['to'].bare)
            content = msg['body']
            room = msg_to
        else:
            print('...ignoring unknown message type:', msg['type'])
            return None

        ## We don't process events that we send ourselves that could
        # get into some infinite loopiness
        if msg_from == self.nick:
            print('...ignoring message sent by me:', msg['type'])
            return None

        self.bot._on_message(Message(
            msg_from, 
            msg_to, 
            content, 
            room=msg_to,
            original=msg
        ))

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

        # Raw connection test
        if self.muc:
            for i in range(5): # Wait a maximum of 5 seconds to connect to all rooms
                all_connected = True
                time.sleep(1)
                for room in self.rooms:
                    if room not in self.muc.rooms:
                        all_connected = False
                        break
                if all_connected:
                    break
        for room in self.rooms:
            self.send_message(room, '/me is now fully operational')

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
        if not isinstance(recipient, str):
            recipient = recipient.get_id() # Supports both rooms and users
        if recipient in self['xep_0045'].rooms:
            mtype='groupchat'
        else:
            mtype='chat'
        super(XMPPBackend, self).send_message(
            mto=recipient,
            mbody=content,
            mtype=mtype
        )
