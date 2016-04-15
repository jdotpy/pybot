from .core import HearMessagePlugin
import requests

class IssueMention(HearMessagePlugin):
    hear_regexes = [
        r'#(\d{1,6})( -v)?\b',
        r'\b(\w{2,50}\-\d{1,6})( -v)?\b'
    ]

    def __init__(self, *args, **kwargs):
        super(IssueMention, self).__init__(*args, **kwargs)
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
        verbose = ' -v' in match.groups()
        if '-' not in issue_id:
            if self.default_project:
                issue_id = self.default_project + '-' + issue_id
            else:
                return None
        results = self._execute('GET', '/rest/api/latest/issue/' + issue_id, data={
            'expand': 'summary'
        })
        if results is None:
            return None
        ticket_url = self.base_url + '/browse/' + issue_id
        summary = results['fields']['summary']
        if results['fields']['description']:
            details = '\n' + results['fields']['description']
        else:
            details = ''
        status = results['fields']['status']['name']
        issue_type = results['fields']['issuetype']['name']
        assigned_to = results['fields']['assignee']['displayName']
        creator = results['fields']['creator']['displayName']
        created = results['fields']['created'].replace('T', ' ')
        comments = results['fields']['comment']['comments']
        if comments:
            last_comment_date = comments[-1]['created'].replace('T', ' ')
        else:
            last_comment_date = 'No comments'
        if verbose:
            return '[{} {}] {}\nCreated by: {}\nAssigned to: {}\nLast Comment: {}\n{}{}'.format(
                status, issue_type, summary, 
                creator, assigned_to, 
                last_comment_date,
                ticket_url,
                details
            )
        else:
            return '[{} {}] {} @{}\n{}'.format(status, issue_type, summary, assigned_to, ticket_url)
