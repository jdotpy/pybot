from .xmpp import XMPPBackend
from ..bot import Message, User

class HipchatBackend(XMPPBackend):
    MUC_MAXHISTORY = 1 # Apparently this is as close to 0 as hipchat will let me get

    def _parse_roster_query(self, result):
        users = []
        raw_user_items = [ri for ri in result['roster']]
        for item in raw_user_items:
            user_data = dict(item.xml.attrib)
            users.append(User(
                username=user_data['jid'],
                name=user_data['name'],
            ))
        return users
