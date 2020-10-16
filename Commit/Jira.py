from jira import JIRA
import csv

NAME_PROJECT = "LANG"


class Jira:
    connect: JIRA

    def __init__(self, url_arg):
        self.URL = url_arg

    def connect(self):
        self.connect = JIRA(obj_jira.URL)

    @staticmethod
    def write_file(list_issues):
        f = open('File/jira.csv', 'a', newline='')
        try:
            writer = csv.writer(f)
            for issue in list_issues:
                writer = csv.writer(f)
                writer.writerow([issue.key])
        finally:
            f.close()

    def get_all_issues(self):
        list_all_issues = list()
        # Search all issues with Query
        block_size = 100
        block_num = 0
        index = 0
        while index < 247045:
            try:
                start_idx = block_num * block_size
                issues_in_project = self.connect.search_issues('project = LANG AND (type = Bug) AND (status = Closed '
                                                               'OR status = Done )',
                                                               start_idx, block_size)
                if len(issues_in_project) == 0:
                    # Retrieve issues until there are no more to come
                    break
                if issues_in_project is not None:
                    for issue in issues_in_project:
                        list_all_issues.append(issue)
                self.write_file(list_all_issues)
                list_all_issues = list()
                block_num += 1
                index += 1
            except:
                pass
        return list_all_issues


# Connect project in Jira
obj_jira = Jira('https://issues.apache.org/jira')
obj_jira.connect()
list_to_write = obj_jira.get_all_issues()
# obj_jira.write_file(list_to_write)
