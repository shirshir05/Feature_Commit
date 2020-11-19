from jira import JIRA
import csv

NAME_PROJECT = "LANG"


class Jira:
    connect: JIRA

    def __init__(self, url_arg):
        self.URL = url_arg

    def connect(self):
        self.connect = JIRA(self.URL)




def get_jira_issues(project_name, url=r"http://issues.apache.org/jira", bunch=100):
    jira_conn = JIRA(url)
    all_issues=[]
    extracted_issues = 0
    while True:
        issues = jira_conn.search_issues("project={0} AND (type = Bug) AND (status = Closed OR status = Done OR status = Resolved)".format(project_name), maxResults=bunch, startAt=extracted_issues)
        all_issues.extend(issues)
        extracted_issues=extracted_issues+bunch
        if len(issues) < bunch:
            break
    with open('File/Jira/jira3.csv', 'w') as f:
        f.writelines(list(map(lambda issue: issue.key.strip()+'\n', all_issues)))


all_i = get_jira_issues('MATH')
# Connect project in Jira
# obj_jira = Jira('https://issues.apache.org/jira')
# obj_jira.connect()
