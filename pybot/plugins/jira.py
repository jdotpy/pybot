from .core import HearMessagePlugin
import requests

class JiraHelpers(HearMessagePlugin):
    hear_regexes = [
        r'#(\d{1,6})\b',
        r'\b(\w{2,50}\-\d{1,6})\b'
    ]

    def __init__(self, *args, **kwargs):
        super(JiraHelpers, self).__init__(*args, **kwargs)
        self.base_url = self.options.get('url', None)
        self.default_project = self.options.get('default_project', None)

    def _execute(self, method, path, data=None):
        auth = (self.options.get('user', ''), self.options.get('password', ''))
        session = requests.Session()
        session.proxies = {}
        if method == 'GET':
            status_code, response = self.bot.web(method, self.base_url + path, params=data, verify=False, auth=auth, session=session)
        else:
            status_code, response = self.bot.web(method, self.base_url + path, data=params, verify=False, auth=auth, session=session)
        if not status_code:
            return None
        results = response.json()
        return results

    def hear(self, message, match=None):
        issue_id = match.group(1)
        if '-' not in issue_id:
            if self.default_project:
                issue_id = self.default_project + '-' + issue_id
            else:
                return None
        results = self._execute('GET', '/rest/api/latest/issue/' + issue_id, data={
            'expand': 'summary'
        })
        if results is None:
            print('didnt find a ticket')
            return None
        ticket_url = self.base_url + '/browse/' + issue_id
        return '{}\n{}'.format(ticket_url, results['fields']['summary'])
