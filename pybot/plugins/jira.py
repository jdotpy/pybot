from .core import HearMessagePlugin
import requests

class JiraClient(HearMessagePlugin):
    def __init__(self, *args, **kwargs):
        super(JiraClient, self).__init__(*args, **kwargs)
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

    def _issue_link(self, issue):
        return self.base_url + '/browse/' + issue['key']

    def _issue_display(self, issue, verbose=False):
        summary = issue['fields']['summary']
        if issue['fields']['description']:
            details = '\n' + issue['fields']['description']
        else:
            details = ''
        status = issue['fields']['status']['name']
        issue_type = issue['fields']['issuetype']['name']
        try:
            assigned_to = issue['fields']['assignee']['displayName']
        except Exception as e:
            assigned_to = 'Nobody'
        creator = issue['fields']['creator']['displayName']
        created = issue['fields']['created'].replace('T', ' ')
        try:
            comments = issue['fields']['comment']['comments']
        except Exception as e:
            comments = []
        if comments:
            last_comment_date = comments[-1]['created'].replace('T', ' ')
        else:
            last_comment_date = 'No comments'
        if verbose:
            return '[{} {}] {}\nCreated by: {}\nAssigned to: {}\nLast Comment: {}\n{}{}'.format(
                status, issue_type, summary, 
                creator, assigned_to, 
                last_comment_date,
                self._issue_link(issue),
                details
            )
        else:
            return '[{} {}] {} @{}\n{}'.format(
                status, issue_type, summary, assigned_to, 
                self._issue_link(issue)
            )

class IssueMention(JiraClient):
    hear_regexes = [
        r'#(\d{1,6})( -v)?\b',
        r'\b(\w{2,50}\-\d{1,6})( -v)?\b'
    ]

    def hear(self, message, match=None):
        issue_id = match.group(1)
        verbose = ' -v' in match.groups()
        if '-' not in issue_id:
            if self.default_project:
                issue_id = self.default_project + '-' + issue_id
            else:
                return None
        results = self._execute('GET', '/rest/api/2/issue/' + issue_id, data={
            'expand': 'summary'
        })
        if results is None:
            return None
        return self._issue_display(results, verbose=verbose)

class JiraSearch(JiraClient):
    hear_regexes = [
        r'jira search (.*)',
    ]

    def hear(self, message, match=None):
        jql = match.group(1)
        results = self._execute('GET', '/rest/api/2/search', data={
            'jql': jql
        })
        if results is None:
            return None
        
        result_displays = []
        for issue in results['issues']:
            result_displays.append(self._issue_display(issue))

        return '\n\n'.join(result_displays)
