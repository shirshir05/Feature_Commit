import difflib
import os

import pathlib

from git import Repo
import csv

import pandas as pd

from Commit.Filter import Filter
from Feature.MeasureDiff import MeasureDiff
from Feature.MeasureToken import MeasureToken
from Feature.MeasureLab import MeasureLab

NAME_PROJECT = "LANG-"
# FEATURE_LIST = ['commit', 'file', 'AnonInnerLength', 'AvoidInlineConditionals', 'BooleanExpressionComplexity',
#                 'CovariantEquals', 'ClassTypeParameterName', 'CatchParameterName', 'EmptyBlock',
#                 'EmptyStatement', 'EqualsHashCode', 'CyclomaticComplexity', 'LineLength', 'MethodLength',
#                 'MissingSwitchDefault', 'ReturnCount', 'StringLiteralEquality', 'TodoComment',
#                 'ClassFanOutComplexity', 'Long parameter list', 'Complex method', 'Complex conditional',
#                 'nested_if_else_dept', 'NCSS', 'File_length', 'NPath_Complexity', 'Number_of_public_methods',
#                 'Total_number_of_methods', 'wmc', 'loopQty',
#                 'comparisonsQty', 'maxNestedBlocks', 'lambdasQty', 'cbo', 'variables', 'tryCatchQty',
#                 'parenthesizedExpsQty', 'stringLiteralsQty', 'numbersQty', 'assignmentsQty', 'mathOperationsQty',
#                 'uniqueWordsQty', 'modifiers', 'logStatementsQty',
#                 'difficulty', 'volume', 'getDistinctOperandsCnt', 'getDistinctOperatorsCnt', 'getEffort',
#                 'getTotalOparandsCnt', 'getTotalOperatorsCnt', 'getVocabulary',
#                 'commit insert bug?']


FEATURE_LIST = ['commit', 'file', "Member", "FieldDeclaration", "VariableDeclaration", "LocalVariableDeclaration",
                "VariableDeclarator", "Literal",
                "This", "MemberReference", 'row add', 'row remove', "row add-row remove", "change block",
                "character change", 'commit insert bug?']

# This dictionary contain
# dict_commit_filter[str(commit)] = [[lines_before, lines_after], [number_lines_before, number_lines_after]]
dict_commit_filter = {}


# -------------------------------------------Start feature of commit
def find_feature_all_commit(list_of_commit, list_commit_bug):
    with open('File/feature_of_commit_solve_issue.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=',')
        measure_diff = MeasureDiff()
        measure_token = MeasureToken()
        measure_lab = MeasureLab()
        writer.writerow(FEATURE_LIST)
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
                        if diff.a_path == file_change:
                            try:
                                if not str(commit) in dict_commit_filter.keys():
                                    # filter the source file
                                    filter_obj = Filter()
                                    number_lines_before, number_lines_after = filter_obj.get_relevant_lines(diff,
                                                                                                            parent,
                                                                                                            commit)
                                    lines_before = Filter.filter_file_line(number_lines_before,
                                                                           diff.a_blob.data_stream.read().decode(
                                                                               'utf-8').splitlines())
                                    lines_after = Filter.filter_file_line(number_lines_after,
                                                                          diff.b_blob.data_stream.read().decode(
                                                                              'utf-8').splitlines())
                                    dict_commit_filter[str(commit)] = [[lines_before, lines_after],
                                                                       [number_lines_before, number_lines_after]]
                                # list_feature += measure_lab.main_measure(dict_commit_filter[str(commit)][0][0],
                                # dict_commit_filter[str(commit)][0][1]) list_feature += measure_lab.main_measure(
                                # diff.a_blob.data_stream.read().decode('utf-8').splitlines() ,
                                # diff.b_blob.data_stream.read().decode('utf-8').splitlines()) list_feature +=
                                # measure_token.measure_diff(commit, file_change)
                                list_feature = measure_token.get_feature(commit, file_change)
                                if list_feature is None:
                                    continue
                                list_feature += measure_diff.measure_diff(dict_commit_filter[str(commit)][0])
                                file.write(str(commit))
                                file.write(',')
                                file.write(file_change)
                                file.write(',')
                                for feature in list_feature:
                                    file.write(str(feature))
                                    file.write(',')
                                ans = 0
                                for commit_bug, file_bug in list_commit_bug:
                                    if str(commit) == str(commit_bug) and file_change == file_bug:
                                        ans = 1
                                if ans == 0:
                                    file.write("0")
                                else:
                                    file.write("1")
                                file.write('\n')
                                file.flush()
                            except Exception as e:
                                print("find_feature_all_commit - error - ", e)
                                # raise e
                                pass
        measure_token.close_connection()


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
    list_file_commit_change = list()
    list_commit_with_file = list()
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
                    if diff.a_path == file_change:
                        try:
                            number_lines_before, number_lines_after = filter_obj.get_relevant_lines(diff, parent,
                                                                                                    commit)
                            lines_before = Filter.filter_file_line(number_lines_before,
                                                                   diff.a_blob.data_stream.read().decode(
                                                                       'utf-8').splitlines())
                            lines_after = Filter.filter_file_line(number_lines_after,
                                                                  diff.b_blob.data_stream.read().decode(
                                                                      'utf-8').splitlines())
                            dict_commit_filter[str(commit)] = [[lines_before, lines_after],
                                                               [number_lines_before, number_lines_after]]
                            diff = difflib.Differ().compare(lines_before, lines_after)

                            lines_guilty = find_blame_commits(diff)
                            list_commit_bug = write_file_commit_blame(parent, file_change, lines_guilty, commit, issue,
                                                                      diff)
                            list_commit_insert_bug = list_commit_insert_bug + list_commit_bug
                            for commit_bug in list_commit_bug:
                                list_commit_with_file.append(file_change)
                                list_file_commit_change.append(commit_bug)
                        except Exception as e:
                            print("operation_on_commit function - error - ", e)
                            # raise e
                            pass
    return list(map(lambda j, y: (j, y), list_file_commit_change, list_commit_with_file))


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
            number_lines_before, number_lines_after = dict_commit_filter[str(commit)][1]
            for commit_suspect, list_of_line in obj_git.connect.blame(parent, file_change):
                for i in range(0, len(list_of_line)):
                    counter_all_line += 1
                    if counter_all_line in number_lines_before:
                        counter_relevant_line += 1
                    for line, line_number in lines_guilty:
                        if line_number == counter_relevant_line:
                            writer.writerow(
                                [issue, commit, file_change, line, commit_suspect, counter_all_line,
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
    # remove - and space from start of line
    line_parser = (line.replace('- ', '', 1)).lstrip()
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
    if line add we blame the line above line add (whiteout line that start with *, { , }, /*)
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
    with open('File/jira.csv') as csv_file:
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
    data_frame = pd.read_csv(path)
    pd.options.display.width = 0
    print("describe data frame in ptah ", path)
    print(data_frame.describe())


class GetCommit:
    connect: Repo

    def __init__(self, url):
        """
        This function init tha GetCommit class.
        connect to project in github
        init file
        :parameter:
            url(string) - fot project in github
        """
        self.URL = url
        self.connect = Repo(self.URL)
        assert not self.connect.bare
        self.list_of_commit = self.get_all_commit()
        if os.path.exists("File/commit_blame.csv"):
            os.remove("File/commit_blame.csv")

    def main_function(self):
        """
        This function classification all commit insert bug by blame the last row that edit.
        The main function that call all help function.
        :return:
            all_commit_insert_bug(list)
        """
        # for all issue in jira
        all_commit_insert_bug = list()
        with open('File/commit_blame.csv', 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(['issue', 'ID commit', 'file', 'line change', 'previous commit', 'line number',
                             'number relevant line number'])
        # get list all issue that start with LANG-XXXX
        list_of_issue = read_issue_from_file()
        # get list of commit
        for issue in list_of_issue:
            issue = parser_issue(issue)
            list_commit_sol_issue = list()
            # find all commit solve this issue
            for commit_check in self.list_of_commit:
                if str(issue + ' ') in commit_check.summary or str(issue + ')') in commit_check.summary or str(
                        issue + ']') in commit_check.summary or str(issue + ':') in commit_check.summary:
                    list_commit_sol_issue.append(commit_check)

                    # operation_on_commit find all commit that insert bug of this issue
            all_commit_insert_bug = all_commit_insert_bug + operation_on_commit(list_commit_sol_issue, issue)
        return all_commit_insert_bug

    # main_function: 2
    def get_all_commit(self):
        """
        Get all commit from url of repository
        :return:
            list_all_commit(list)
        """
        list_all_commit = list()
        commits = list(self.connect.iter_commits('master'))
        for commit in commits[:1000]:
            list_all_commit.append(commit)
        return list_all_commit


# TODO list for new programmer:
# 1. TODO change path in line obj_git = Git('C:/Users/shir0/commons-lang') to path og commons-lang
# 2. TODO add directory name "Code_lab" from this URL https://github.com/amir9979/repository_mining.git
# 2. TODO change line DB_PATH = r"C:\Users\shir0\Commits-Issues-DB\CommitIssueDB.db" (you need create DB in this name
# TODO according to https://github.com/amir9979/Commits-Issues-DB.git


if __name__ == '__main__':
    obj_git = GetCommit('C:/Users/shir0/commons-lang')
    # get all commit insert bug
    list_of_commit_insert_bug = obj_git.main_function()
    # feature
    find_feature_all_commit(obj_git.list_of_commit, list_of_commit_insert_bug)

    describe_data_frame(str(pathlib.Path().absolute()) + '/File/feature_of_commit_solve_issue.csv')
    describe_data_frame(str(pathlib.Path().absolute()) + '/File/before_token.csv')
    describe_data_frame(str(pathlib.Path().absolute()) + '/File/after_token.csv')
