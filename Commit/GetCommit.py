import difflib
import os
import pathlib
import threading

from git import Repo
import csv
import copy
import pandas as pd
from pandas.tests.io.excel.test_xlsxwriter import xlsxwriter

from Commit.Filter import Filter
from Feature.MeasureMeaningToken import MeasureMeaningToken
from Feature.Refactoring import Refactoring
from Feature.MeasureDiff import MeasureDiff
from Feature.MeasureMeaning import MeasureMeaning
from Feature.MeasureLab import MeasureLab
from Feature.MeasureTokens import MeasureTokens

LOCATION_PROJECT = "C:/Users/shir0/camel"

# This dictionary contain
# dict_commit_filter[(str(commit),str(file)) ]=[[lines_before, lines_after], [number_lines_before, number_lines_after]]
dict_commit_filter = {}


# -------------------------------------------Start feature of commit
def find_feature_all_commit(list_of_commit, list_commit_bug):
    with open('File/feature.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter='!')
        measure_diff = MeasureDiff()
        measure_meaning_token = MeasureMeaningToken()
        measure_refactoring = Refactoring()

        list_all = ["commit", "file"] + feature_header_parent("meaning_header") + feature_header("diff_header") + \
                   feature_header_parent("token_header") + feature_header("refactoring_header")
        list_all += ["commit insert bug?"]
        writer.writerow(list_all)
        file.flush()
        # find all commit
        for commit in list_of_commit:
            all_file_of_commit = commit.stats.files
            list_file_that_change = Filter.find_java_file(all_file_of_commit)
            # find java file
            for file_change in list_file_that_change:
                # parent of commit
                for parent in commit.parents:
                    diffs = parent.diff(commit)
                    for diff in diffs:
                        if diff.new_file or diff.deleted_file:
                            continue
                        if diff.b_path == file_change:
                            try:
                                if not (str(commit), str(file_change)) in dict_commit_filter.keys():
                                    # filter the source file
                                    filter_obj = Filter()
                                    number_lines_before, number_lines_after = filter_obj.get_relevant_lines(diff,
                                                                                                            parent,
                                                                                                            commit)
                                    before_contents = list(map(lambda x: x.decode("utf-8", errors='ignore'),
                                                               diff.a_blob.data_stream.stream.readlines()))
                                    lines_before = Filter.filter_file_line(number_lines_before, before_contents)
                                    after_contents = list(map(lambda x: x.decode("utf-8", errors='ignore'),
                                                              diff.b_blob.data_stream.stream.readlines()))
                                    lines_after = Filter.filter_file_line(number_lines_after, after_contents)
                                    # no relevant change in commit
                                    if len(list(difflib.context_diff(lines_before,
                                                                     lines_after))) == 0:
                                        continue
                                    dict_commit_filter[(str(commit), str(file_change))] = [[lines_before, lines_after],
                                                                                           [number_lines_before,
                                                                                            number_lines_after]]

                                list_feature_tokens, list_feature_meaning = feature_meaning_token(measure_meaning_token, commit, file_change)
                                list_feature_diff = feature_diff(measure_diff, commit, file_change)
                                list_refactoring = feature_refactoring(measure_refactoring, commit, file_change)
                                list_feature = list_feature_meaning + list_feature_diff + list_feature_tokens +\
                                               list_refactoring

                                file.write(str(commit))
                                file.write('!')
                                file.write(file_change)
                                file.write('!')
                                for feature in list_feature:
                                    file.write(str(feature))
                                    file.write('!')
                                ans = 0
                                df = list_commit_bug.loc[list_commit_bug["blame commit"] == str(commit)]
                                df = df.loc[df["file"] == str(file_change)]
                                if df.size > 0:
                                    ans = 1
                                if ans == 0:
                                    file.write("0")
                                else:
                                    file.write("1")
                                file.write('\n')
                                file.flush()
                            except Exception as e:
                                print("find_feature_all_commit - error - ", e)
                                print("commit ", commit)
                                import traceback
                                traceback.print_exc()
                                print("file ", file_change)
                                pass
        measure_meaning_token.close_connection()


def feature_header_parent(name_header):
    my_file = open(str(pathlib.Path().absolute()) + "/File/Header/" + name_header + ".txt", "r")
    lines_delta = []
    lines_parent = []
    lines_current = []
    for line in my_file:
        line = line.replace("\n", "")
        lines_parent.append('parent_' + str(line))
        lines_current.append('current_' + str(line))
        lines_delta.append('delta_' + str(line))
    return lines_parent + lines_current + lines_delta


def feature_header(name_header):
    my_file = open(str(pathlib.Path().absolute()) + "/File/Header/" + name_header + ".txt", "r")
    lines = my_file.read()
    lines = lines.split("\n")
    return lines


def feature_diff(measure_diff, commit, file_change):
    list_feature_diff = measure_diff.measure_diff(dict_commit_filter[(str(commit), str(file_change))][0])
    if list_feature_diff is None:
        raise Exception("None list_feature_diff")
    return list_feature_diff


def feature_refactoring(measure_refactoring, commit, file_change):
    list_refactoring = measure_refactoring.feature_refactoring(commit, file_change)
    if list_refactoring is None:
        raise Exception("None list_refactoring")
    return list_refactoring


def feature_meaning_token(measure_meaning_tokens, commit, file_change):
    list_feature_tokens = measure_meaning_tokens.get_feature(commit, file_change)
    if list_feature_tokens is None:
        raise Exception("None list_feature meaning tokens")
    return list_feature_tokens





def feature_lab(measure_lab, before_contents, after_contents, diff):
    if not after_contents:
        before_contents = list(map(lambda x: x.decode("utf-8", errors='ignore'),
                                       diff.a_blob.data_stream.stream.readlines()))
        after_contents = list(map(lambda x: x.decode("utf-8", errors='ignore'),
                                  diff.b_blob.data_stream.stream.readlines()))
    list_feature_lab = measure_lab.main_measure(before_contents, after_contents)
    if list_feature_lab is None:
        raise Exception("None list_feature_lab")
    return list_feature_lab


# -------------------------------------------END feature of commit


# main_function: 4
def operation_on_commit(list_commit_sol_issue, issue):
    """
    Strategy to find commit blame
    1. for commit in list of commit that fix bug
        1.1. find list of file change
        1.2 for file in file change
            1.2.1 find parents of commit in file
            1.2.2 for parent in parents
                1.2.2.1 find diff between parent and commit
                1.2.2.1.2 for all diff in diffs
                    1.2.2.1.2.1 filter_obj the source file (find only relevant line)
                    1.2.2.1.2.2 find blame commits
                    1.2.2.1.2.2 write blame commit to file commit_blame
    return:
        list contain tuple of (file_commit_change, commit_with_file)
    """
    list_commit_insert_bug = list()
    for commit in list_commit_sol_issue:
        all_file_of_commit = commit.stats.files
        list_file_that_change = Filter.find_java_file(all_file_of_commit)
        for file_change in list_file_that_change:
            for parent in commit.parents:
                diffs = parent.diff(commit)
                for diff in diffs:
                    filter_obj = Filter()
                    if diff.new_file or diff.deleted_file:
                        continue
                    # b_blob for rename file
                    if diff.b_path == file_change:
                        try:
                            number_lines_before, number_lines_after = filter_obj.get_relevant_lines(diff, parent,
                                                                                                    commit)
                            before_contents = list(map(lambda x: x.decode("utf-8", errors='ignore'),
                                                       diff.a_blob.data_stream.stream.readlines()))
                            lines_before = Filter.filter_file_line(number_lines_before, before_contents)

                            after_contents = list(map(lambda x: x.decode("utf-8", errors='ignore'),
                                                      diff.b_blob.data_stream.stream.readlines()))
                            lines_after = Filter.filter_file_line(number_lines_after, after_contents)
                            dict_commit_filter[(str(commit), str(file_change))] = [[lines_before, lines_after],
                                                                                   [number_lines_before,
                                                                                    number_lines_after]]
                            # no relevant change in commit
                            if len(list(difflib.context_diff(lines_before, lines_after))) == 0:
                                continue
                            diff_content = list(difflib.Differ().compare(lines_before, lines_after))

                            lines_guilty = find_blame_commits(diff_content)
                            # send diff.a_path (name of file before change)
                            list_commit_bug = write_file_commit_blame(parent, diff.a_path, lines_guilty, commit, issue,
                                                                      diff_content)
                            list_commit_insert_bug = list_commit_insert_bug + list_commit_bug
                        except Exception as e:
                            print("operation_on_commit function - error - ", e)
                            # raise e
                            pass


def commit_suspect_file(commit_suspect, file_change):
    for file_check in commit_suspect.stats.files.keys():
        index_suspect = file_check.rfind("/")
        index_file_change = file_change.rfind("/")
        if file_check[index_suspect:] == file_change[index_file_change:]:
            return file_check


def find_blame_commits(list_diff):
    """
        Get list diff between parent and commit
        This function find the number of line need blame.
        :parameter:
            list_diff(list) : list of string that contain row -
                1. start with + -> add
                2. start with - -> remove
                3. start with ? -> ignore
                4. otherwise no change
         Strategy to find commit blame:
         1. if line add we blame the line above line add (whiteout line that start with *, { , }, /*)
         2. if line remove we blame tha line remove (whiteout line that start with *, { , }, /*)
    """
    list_line_blame = list()
    list_line_number = list()
    list_diff = list(list_diff)
    # counter the number of line
    counter_line_number = 0
    for i in range(len(list_diff)):
        # line that change or remove
        if list_diff[i].startswith('-'):
            blame_remove_line(list_diff[i], counter_line_number, list_line_blame, list_line_number)
        # line that add to code
        elif list_diff[i].startswith('+'):
            blame_add_line(list_diff, counter_line_number, list_line_blame, list_line_number, i)
        # we count line of tha alo file (before commit)
        if not list_diff[i].startswith('+') and not list_diff[i].startswith('?'):
            counter_line_number += 1
    return list(map(lambda j, y: (j, y), list_line_blame, list_line_number))


# operation_on_commit: 3
def write_file_commit_blame(parent, file_change, lines_guilty, commit, issue, diff):
    """
    :parameter:
        parent(commit) -
        commit(commit) -
        file_change(str)
        lines_guilty(list of sublist) - [[line blame , line_number]]
        issue
        diff
    This function find the relevant commit we need blame according to line_number and write file of commit.
    """
    # blame return tuple commit and line that commit write
    # shir = diff.get_changed_methods('C:/Users/TMP467/Desktop/shir - studies/commons-lang', commit, parent)
    list_insert_bug = []
    with open('File/commit_blame.csv', 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        try:
            # counter the number of row in list (start 0)
            counter_all_line = -1
            counter_relevant_line = -1
            number_lines_before, number_lines_after = dict_commit_filter[(str(commit), str(file_change))][1]
            for commit_suspect, list_of_line in obj_git.connect.blame(parent, file_change):
                for i in range(0, len(list_of_line)):
                    counter_all_line += 1
                    if counter_all_line in number_lines_before:
                        counter_relevant_line += 1
                    for line, line_number in lines_guilty:
                        if line_number == counter_relevant_line:
                            if file_change in commit_suspect.stats.files.keys():
                                writer.writerow(
                                    [issue, commit, file_change, line,
                                     commit_suspect, counter_all_line,
                                     counter_relevant_line])
                            else:
                                writer.writerow(
                                    [issue, commit, commit_suspect_file(commit_suspect, file_change), line, commit_suspect, counter_all_line,
                                     counter_relevant_line])
                            list_insert_bug.append(commit_suspect)
        except Exception as e:
            print("write_file_commit_blame function - error - ", e)
            # raise e
            pass
    return list_insert_bug


# This function blame line that start with -
# diff_between_commit: 1
def blame_remove_line(line, current_line_number, list_line_blame, list_line_number):
    """
    parameter:
        line(str) - line remove starst with  -
        current_line_number(int) = number of line remove
        list_line_blame(list) - list line blame
        list_line_number(list) - list line number for save number line
    if line remove we blame tha line remove (ignore line that start with *, { , }, /*)
    """
    line_parser = copy.copy(line)
    # remove - and space from start of line
    line_parser = (line_parser.replace('- ', '', 1)).lstrip()
    # if the line is comment ignore
    if not line_parser.startswith("*") and not line_parser.startswith("}") and not line_parser.startswith(
            "/**") and line_parser != "" and not line_parser.startswith("//") and line_parser != " ":
        # blame the line that change or remove
        list_line_blame.append("line remove " + line_parser)
        list_line_number.append(current_line_number)


# diff_between_commit: 2
def blame_add_line(list_diff, counter_line_number, list_line_blame, list_line_number, i):
    """
    parameter:
        line(str) - line add starst with  +
        current_line_number(int) = number of line add
        list_line_blame(list) - list line blame
        list_line_number(list) - list line number for save number line
    if line add we blame the line above line add (whiteout line that start with *, { , }, /*, +)
    """
    if i == 0:
        return
    list_line_blame.append("line add " + list_diff[i])
    i = i - 1
    line_blame = list_diff[i].lstrip()
    index = 0
    flag = False
    while i >= 0 and flag is False:
        if line_blame.startswith('-'):
            line_blame = (list_diff[index].replace('- ', '', 1)).lstrip()
        elif line_blame.startswith('+') or line_blame.startswith('?'):
            i -= 1
            line_blame = list_diff[i].lstrip()
            continue
        # line that not blame - for example {, //, }
        if (line_blame.startswith("*") or line_blame.startswith("}") or line_blame.startswith(
                "/*") or line_blame == "" or line_blame.startswith("//")):
            index += 1
            i -= 1
            line_blame = list_diff[i].lstrip()
        else:
            flag = True
    if i >= 0:
        list_line_number.append(counter_line_number - 1 - index)


# This function read issue from csv file
# return list with all number issue
# main_function: 1
def read_issue_from_file():
    """
    read all issue that write in jira.csv
    :return:
        list issue
    """
    with open('File/Jira/jira3.csv') as csv_file:
        list_issue = list()
        read_csv = csv.reader(csv_file, delimiter=',')
        for row in read_csv:
            list_issue.append(row)
    return list_issue


# The issue read from csv in format ['LANG-123']
# return string in LANG-123 format
# main_function: 3
def parser_issue(issue):
    """
    remove []
    example
    ['LANG-1608']
    replace
    LANG-1608
    """
    issue = str(issue).replace(']', '')
    issue = str(issue).replace("'", '')
    return str(issue).replace('[', '')


def describe_data_frame(path):
    """
      Print describe_data_frame of feature
    """
    data_frame = pd.read_csv(path, delimiter='!')
    df_not_bug = data_frame[data_frame['commit insert bug?'] == 0]
    df_bug = data_frame[data_frame['commit insert bug?'] == 1]

    pd.options.display.width = 0
    print("describe data frame")
    df_not_bug.describe().to_csv(str(pathlib.Path().absolute()) + "/../Commit/File/Describe/df_not_bug_description.csv")
    df_bug.describe().to_csv(str(pathlib.Path().absolute()) + "/../Commit/File/Describe/df_bug_description.csv")
    data_frame.describe().to_csv(str(pathlib.Path().absolute()) + "/../Commit/File/Describe/all_description.csv")


def merge_feature(path, path_merge, name_column, new_path):
    data_frame = pd.read_csv(path)
    list_check = []
    f = open(path_merge, "r")
    while (True):
        line = f.readline()
        if not line:
            break
        list_check.append(line.strip())
    f.close()
    for index, line in data_frame.iterrows():
        count = 0
        for x in list_check:
            if line[x] != 0:
                count += 1
        if count >= 1:
            data_frame.loc[index, name_column] = count
        else:
            data_frame.loc[index, name_column] = 0
    data_frame.to_csv(new_path, index=False)


class GetCommit:
    # connect: Repo

    def __init__(self, url, feature_only=False):
        """
        This function init tha GetCommit class.
        connect to project in github
        init file
        :parameter:
            url(string) - fot project in github
        """
        if feature_only is True:
            self.run_only_feature(url)
            return
        self.URL = url
        self.connect = Repo(self.URL)
        assert not self.connect.bare
        self.list_of_commit = self.get_all_commit()
        if os.path.exists("File/commit_blame.csv"):
            os.remove("File/commit_blame.csv")

    def run_only_feature(self, url):
        self.URL = url
        self.connect = Repo(self.URL)
        assert not self.connect.bare
        self.list_of_commit = self.get_all_commit()

    @classmethod
    def get_commit_by_id(self, url, commit_id):
        self.URL = url
        self.connect = Repo(self.URL)
        assert not self.connect.bare
        return self.connect.commit(commit_id)

    def main_function(self):
        """
        This function classification all commit insert bug by blame the last row that edit.
        The main function that call all help function.
        :return:
            all_commit_insert_bug(list)
        """
        # for all issue in jira
        with open('File/commit_blame.csv', 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            # need space
            writer.writerow([])
            writer.writerow(['issue', 'commit fix', 'file', 'line change', 'blame commit', 'line number',
                             'number relevant line number'])
        # get list all issue that start with LANG-XXXX
        list_of_issue = read_issue_from_file()
        # get list of commit
        for issue in list_of_issue:
            issue = parser_issue(issue)
            list_commit_sol_issue = list()
            # find all commit solve this issue
            for commit_check in self.list_of_commit:
                if issue in commit_check.summary:
                    # quick fix for short issues
                    if commit_check.summary.index(issue) + len(issue) < len(commit_check.summary) and commit_check.summary[commit_check.summary.index(issue) + len(issue)].isnumeric():
                        continue
                    list_commit_sol_issue.append(commit_check)
                elif issue in commit_check.message:
                    if commit_check.message.index(issue) + len(issue) < len(commit_check.message) and \
                            commit_check.message[commit_check.message.index(issue) + len(issue)].isnumeric():
                        continue
                    list_commit_sol_issue.append(commit_check)
            # operation_on_commit find all commit that insert bug of this issue
            if list_commit_sol_issue:
                operation_on_commit(list_commit_sol_issue, issue)

    # main_function: 2
    def get_all_commit(self):
        """
        Get all commit from url of repository
        :return:
            list_all_commit(list)
        """
        list_all_commit = list()
        commits = list(self.connect.iter_commits('master'))
        for commit in commits[0:10]:
            list_all_commit.append(commit)
        return list_all_commit

    def read_commit_blame(self):
        self.dataset = pd.read_csv('File/commit_blame.csv', delimiter=',', skiprows=1)
        self.dataset = self.dataset[['blame commit', 'file']]


# TODO list for new programmer:
# 1. TODO change variable LOCATION_PROJECT to path of project in your computer
# 2. TODO add directory name "Code_lab" from this URL https://github.com/amir9979/repository_mining.git
# 3. TODO change line DB_PATH = r"C:\Users\shir0\Commits-Issues-DB\CommitIssueDB.db" (you need create DB in this name
#  TODO according to https://github.com/amir9979/Commits-Issues-DB.git


if __name__ == '__main__':
    # todo commit blame and feature
    # obj_git = GetCommit(LOCATION_PROJECT)
    # # # get all commit insert bug
    # obj_git.main_function()
    # obj_git.read_commit_blame()
    # feature
    # find_feature_all_commit(obj_git.list_of_commit, obj_git.dataset)

    # todo run_only_feature
    obj_git = GetCommit(LOCATION_PROJECT, True)
    obj_git.read_commit_blame()
    find_feature_all_commit(obj_git.list_of_commit, obj_git.dataset)

    # todo run one commit in feature
    # obj_git = GetCommit(LOCATION_PROJECT, True)
    # obj_git.read_commit_blame()
    # commit_check = GetCommit.get_commit_by_id(LOCATION_PROJECT, '0207f15a49e4a1c74920d2d1cfc2a8ee6c67969c')
    # find_feature_all_commit([commit_check], obj_git.dataset)

    # todo describe_data_frame difference bug ot not bug
    # describe_data_frame(str(pathlib.Path().absolute()) + '/File/feature.csv')
    # describe_data_frame(str(pathlib.Path().absolute()) + '/File/feature_change_label.csv')


    # todo get all unique meaning
    # try:
    #     DB_PATH = r"C:\Users\shir0\Commits-Issues-DB\CommitIssueDB.db"
    #     # Get DB connection
    #     db_connection = sqlite3.connect(DB_PATH)
    #     query_method_data = "select Meaning from MethodData"
    #     sql_query = pd.read_sql_query(query_method_data, db_connection)
    #     df = pd.DataFrame(sql_query, columns=['Meaning'])
    #     list_tokens = []
    #     with open('../Feature/dic_meaning.txt', 'w') as f:
    #         for index, line in df.iterrows():
    #             if line.values == "": continue
    #             json_line = json.loads(str(line.values).replace("\\\'", '"')[3:-3])
    #             for i in json_line.keys():
    #                 if i not in list_tokens:
    #                     list_tokens.append(i)
    #                     f.write("%s " % i)
    #                     f.write("\n")
    #                     f.flush()
    # except Exception as e:
    #     print(e)
    #     pass
