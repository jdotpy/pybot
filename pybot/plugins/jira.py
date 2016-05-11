from .core import HearMessagePlugin
import requests
import json
import re

class JiraClient(HearMessagePlugin):
    def __init__(self, *args, **kwargs):
        super(JiraClient, self).__init__(*args, **kwargs)
        self.base_url = self.options.get('url', None)
        self.default_project = self.options.get('default_project', None)
        self.default_issue_type = self.options.get('default_issue_type', "Story")

    def _execute(self, method, path, data=None):
        auth = (self.options.get('user', ''), self.options.get('password', ''))
        session = requests.Session()
        session.proxies = {}
        if method == 'GET':
            status_code, response = self.bot.web(method, self.base_url + path, params=data, verify=False, auth=auth, session=session)
        else:
            data = json.dumps(data)
            headers= {'Content-Type': 'application/json'}
            status_code, response = self.bot.web(method, self.base_url + path, data=data, verify=False, auth=auth, session=session, headers=headers)
        if not status_code:
            return None
        results = response.json()
        return results

    def _lookup(self, message, issue_id, verbose=False):
        results = self._execute('GET', '/rest/api/2/issue/' + issue_id, data={
            'expand': 'summary'
        })
        if results:
            self.bot.send_message(
                message.reply_to(), 
                self._issue_display(results, verbose=verbose)
            )

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

    def get_jira_user(self, user):
        return {"name": user.name}

class IssueMention(JiraClient):
    patterns = [
        r'#(\d{1,6})( -v)?',
        r'(\w{2,50}\-\d{1,6})( -v)?'
    ]
    hear_regexes = [
        r'.*' + pattern for pattern in patterns
    ]

    def _parse_ids(self, content):
        lookups = []
        for regex in self.patterns:
            for match in re.finditer(regex, content):
                verbose = ' -v' in match.groups()
                issue_id = match.group(1)
                if '-' not in issue_id:
                    if not self.default_project:
                        continue
                    issue_id = self.default_project + '-' + issue_id
                lookups.append((issue_id, verbose))
        return lookups


    def hear(self, message, match=None):
        lookups = self._parse_ids(message.content)
        for issue_id, verbose in lookups:
            self._lookup(message, issue_id, verbose=verbose)

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

class CreateTicket(JiraClient):
    hear_regexes = [
        r'assign me (.*)',
    ]

    def hear(self, message, match=None):
        summary = match.group(1)
        results = self._execute('POST', '/rest/api/2/issue', data={
            "fields": {
                'project': {"key": self.default_project},
                'issuetype': {"name": self.default_issue_type},
                'summary': summary,
                'assignee': self.get_jira_user(message.sender)
            }
        })
        self._lookup(message, results['key'])


