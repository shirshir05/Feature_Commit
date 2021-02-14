from Code_lab.projects import Project
import pandas as pd
import os
import shutil
from Code_lab.metrics.version_metrics import SourceMonitor, CK, Designite, Checkstyle, Halstead
import pathlib
from git import Repo as Re

# region parameter  for checkstyle
from Code_lab.repo import Repo

MAX_AnonInnerLength = 50
MAX_BooleanExpression = 3
MAX_CyclomaticComplexity = 7
MAX_MethodLength = 60
MAX_ReturnCount = 3
MAX_ClassFanOutComplexity = 2

list_checkstyle_sum_of_line = ["[AvoidInlineConditionals]", "[CovariantEquals]", "[ClassTypeParameterName]",
                               "[CatchParameterName]", "[EmptyBlock]", "[EmptyStatement]", "[EqualsHashCode]",
                               "[LineLength]", "[MissingSwitchDefault]", "[StringLiteralEquality]", "[TodoComment]"]
# endregion

# region parameter for designite
parameter_designite = ["Long Parameter List", "Complex Conditional", "Complex Method"]
string_designite = "designite_implementation"
# endregion

# region parameter for ck
string_ck = "ck"
parameter_ck = ["wmc", "loopQty", "comparisonsQty", "maxNestedBlocks", "lambdasQty", "cbo", "variables",
                "tryCatchQty", "parenthesizedExpsQty", "stringLiteralsQty", "numbersQty", "assignmentsQty",
                "mathOperationsQty", "uniqueWordsQty", "modifiers", "logStatementsQty"]
# endregion

# region parameter for halstead
string_halstead = "halstead"
parameter_halstead = ["getDifficulty", "getVolume", "getDistinctOperandsCnt", "getDistinctOperatorsCnt", "getEffort",
                      "getTotalOparandsCnt", "getTotalOperatorsCnt", "getVocabulary"]

# endregion

NAME_PROJECT = "camel"


class MeasureLab:
    def __init__(self):
        self.list_before = []
        self.list_after = []
        self.list_sum = list()

    def main_measure(self, file_before, file_after):
        self.list_before = []
        self.list_after = []
        self.list_sum = list()
        self.write_file(file_before, "File/before")
        self.write_file(file_after, "File/after")

        # checkstyle
        self.run_checkstyle("before", "checkstyle")
        self.run_checkstyle("after", "checkstyle")
        list_before_error, list_after_error = self.get_list_error()
        before, after = self.measure_checkstyle(list_before_error, list_after_error)
        self.list_before += before
        self.list_after += after

        # metric lab
        self.clean_file_and_directory()
        # before
        self.write_file(file_before, str(pathlib.Path().absolute()) + "/apache_repos/" + NAME_PROJECT + "/before")
        project = Project(NAME_PROJECT, NAME_PROJECT.upper())
        # version for Code_lab/repository_data/metric
        version_before = 'shir3'
        self.measure_lab_init(project, version_before)
        self.measure_lab(self.list_before, version_before)
        self.clean_file_and_directory()
        # after
        self.write_file(file_after, str(pathlib.Path().absolute()) + "/apache_repos/" + NAME_PROJECT + "/after")
        version_after = 'shir4'
        self.measure_lab_init(project, version_after)
        self.measure_lab(self.list_after, version_after)
        self.clean_file_and_directory()

        self.list_sum += self.list_before
        self.list_sum += self.list_after
        self.list_sum += [x - y for x, y in zip(self.list_after, self.list_before)]

        return self.list_sum

    @staticmethod
    def write_file(list_java_file, name_file):
        """
        write file.java
        :param
            name_file(str)
            list_java_file - list file to write
        """
        try:
            with open(name_file + '.java', 'w') as file:
                for line in list_java_file:
                    file.write('%s' % line)
        except Exception as e:
            pass

    @staticmethod
    def run_checkstyle(name_file, name_measure):
        os.system('java -jar ' + str(pathlib.Path().absolute()) + "\..\Feature\checkstyle-8.31-all.jar -c " + str(
            pathlib.Path().absolute()) + '\..\Feature\\' + name_measure + ".xml File/" + name_file + ".java -o File/" +
                  name_file + ".txt")

    def measure_checkstyle(self, list_before_error, list_after_error):
        def checkstyle_call_function(list_after, list_before, name, function, param, before_add, after_add):
            before_arg = function(list_before, name, param)
            after_arg = function(list_after, name, param)
            before_add.append(before_arg)
            after_add.append(after_arg)

        """
          get all feature of checkstyle
        """

        before_list = []
        after_list = []
        for i in list_checkstyle_sum_of_line:
            before = self.sum_of_line(list_before_error, i)
            after = self.sum_of_line(list_after_error, i)
            before_list.append(before)
            after_list.append(after)

        checkstyle_call_function(list_after_error, list_before_error, "[AnonInnerLength]",
                                 self.sum_of_anonymous_inner_class, MAX_AnonInnerLength, before_list, after_list)

        # 3 - BooleanExpressionComplexity
        checkstyle_call_function(list_after_error, list_before_error, "[BooleanExpressionComplexity]",
                                 self.sum_of_boolean_expression_complexity, MAX_BooleanExpression, before_list,
                                 after_list)

        # 10 -CyclomaticComplexity
        checkstyle_call_function(list_after_error, list_before_error, "[CyclomaticComplexity]",
                                 self.sum_of_cyclomatic_complexity, MAX_CyclomaticComplexity, before_list, after_list)

        # 12 -MethodLength

        checkstyle_call_function(list_after_error, list_before_error, "[MethodLength]",
                                 self.sum_of_method_length, MAX_MethodLength, before_list, after_list)

        # 14 - ReturnCount
        checkstyle_call_function(list_after_error, list_before_error, "[ReturnCount]",
                                 self.sum_of_return_count, MAX_ReturnCount, before_list, after_list)

        # 17 - ClassFanOutComplexity

        checkstyle_call_function(list_after_error, list_before_error, "[ClassFanOutComplexity]",
                                 self.sum_of_class_fan_out_complexity, MAX_ClassFanOutComplexity, before_list,
                                 after_list)

        return before_list, after_list

    @staticmethod
    def get_list_error():
        """
          get all error from checkstyle
        """
        list_before_error = list()
        list_after_error = list()
        with open("File/before.txt") as fp:
            lines = fp.readlines()
            for line in lines:
                list_before_error.append(line)
        with open("File/after.txt") as fp:
            lines = fp.readlines()
            for line in lines:
                list_after_error.append(line)
        return list_before_error, list_after_error

    # sum line that contain word "found" and the number after found
    @staticmethod
    def sum_of_found(list_error_with_found, name_error):
        sum_length_line = 0
        for line in list_error_with_found:
            number_start = line.find("(found")
            if number_start != -1 and line.find(name_error) != -1:
                index_start = number_start
                line = line[index_start + 7:]
                index_end = line.find(")")
                line = line[:index_end]
                sum_length_line += int(line)
        return sum_length_line

    # sum line that contain words "Boolean expression complexity is" and the number after found
    @staticmethod
    def sum_of_boolean_expression_complexity(list_error_with_found, name_error, average):
        sum_boolean_expression = 0
        for line in list_error_with_found:
            index_start = line.find("Boolean expression complexity is")
            if index_start != -1 and line.find(name_error) != -1:
                line = line[index_start + 33:]
                index_end = line.find(" (")
                line = line[:index_end]
                sum_boolean_expression += int(line)
        return sum_boolean_expression

    # sum line that contain words "Cyclomatic Complexity is" and the number after found
    @staticmethod
    def sum_of_cyclomatic_complexity(list_error_with_found, name_error, average):
        sum_cyclomatic_complexity = 0
        for line in list_error_with_found:
            index_start = line.find("Cyclomatic Complexity is")
            if index_start != -1 and line.find(name_error) != -1:
                line = line[index_start + 25:]
                index_end = line.find(" (")
                line = line[:index_end]
                sum_cyclomatic_complexity += int(line)
        return sum_cyclomatic_complexity

    # sum line that contain words "Cyclomatic Complexity is" and the number after found
    @staticmethod
    def sum_of_return_count(list_error_with_found, name_error, average):
        sum_return_count = 0
        for line in list_error_with_found:
            index_start = line.find("Return count is")
            if index_start != -1 and line.find(name_error) != -1:
                line = line[index_start + 16:]
                index_end = line.find(" (")
                line = line[:index_end]
                sum_return_count += int(line)
        return sum_return_count

    # sum line that contain words "Cyclomatic Complexity is" and the number after found
    @staticmethod
    def sum_of_class_fan_out_complexity(list_error_with_found, name_error, average):
        sum_complexity = 0
        for line in list_error_with_found:
            index_start = line.find("Class Fan-Out Complexity is")
            if index_start != -1 and line.find(name_error) != -1:
                line = line[index_start + 28:]
                index_end = line.find(" (max")
                line = line[:index_end]
                sum_complexity += int(line)
        return sum_complexity

    # sum line that contain words "Method length is" and the number after found
    @staticmethod
    def sum_of_method_length(list_error_with_found, name_error, average):
        sum_length_line = 0
        for line in list_error_with_found:
            index_start = line.find("Method length is")
            if index_start != -1 and line.find(name_error) != -1:
                line = line[index_start + 17:]
                index_end = line.find("lines")
                line = line[:index_end]
                sum_length_line += int(line)
        return sum_length_line

    # sum line that contain words "Anonymous inner class length is" and the number after found
    @staticmethod
    def sum_of_anonymous_inner_class(list_error_with_found, name_error, average):
        sum_anonymous_inner_class = 0
        for line in list_error_with_found:
            index_start = line.find("Anonymous inner class length is")
            if index_start != -1 and line.find(name_error) != -1:
                line = line[index_start + 32:]
                index_end = line.find(" lines (")
                line = line[:index_end]
                sum_anonymous_inner_class += int(line)
        return sum_anonymous_inner_class

    # sum line that contain error
    @staticmethod
    def sum_of_line(list_error_with_found, name_error):
        sum_line = 0
        for line in list_error_with_found:
            if line.find("Starting audit...") == -1 and line.find("Audit done.") == -1 and line.find(name_error) != -1:
                sum_line += 1
        return sum_line

    @staticmethod
    def measure_lab_init(project, version):
        try:
            number = 0
            cs = Checkstyle(project, version, None)
            cs.extract()
            number = 1
            c = CK(project, version, None)
            c.extract()
            number = 2
            h = Halstead(project, version, None)
            h.extract()
            number = 3

            d = Designite(project, version, None)
            d.extract()
            number = 4
            # sm = SourceMonitor(Project("commons-math", "MATH"), '3', None)
            # sm.extract()
        except Exception as e:
            print("measure_lab ", number)
            print(e)
            pass

    def measure_lab(self, list, version):
        # Designite Java
        for i in parameter_designite:
            list.append(self.get_metric_sum_column(string_designite, i, version))

        # checkstyle
        string_checkstyle = "checkstyle"
        list.append(self.get_metric_sum_column(string_checkstyle, "Nested_if-else_depth", version))
        list.append(self.get_metric_first_row(string_checkstyle, "NCSS_for_this_file", version))
        list.append(self.get_metric_first_row(string_checkstyle, "File_length", version))
        list.append(self.get_metric_sum_column(string_checkstyle, "NPath_Complexity", version))
        list.append(self.get_metric_first_row(string_checkstyle, "Number_of_public_methods", version))
        list.append(self.get_metric_first_row(string_checkstyle, "Total_number_of_methods", version))

        # CK
        for i in parameter_ck:
            list.append(self.get_metric_sum_column(string_ck, i, version))

        # Halstead
        for i in parameter_halstead:
            list.append(self.get_metric_sum_column(string_halstead, i, version))

    @staticmethod
    def get_metric_sum_column(name_tool, name_metric, version):
        try:
            df = pd.read_csv(
                str(
                    pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/" + NAME_PROJECT + "/" + version + "/" + name_tool +
                ".csv", delimiter=";")
            sum_column = df[name_metric].sum()
            return sum_column
        except Exception as e:
            return 0

    @staticmethod
    def get_metric_first_row(name_tool, name_metric, version):
        try:
            df = pd.read_csv(
                str(
                    pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/" + NAME_PROJECT + "/" + version + "/" + name_tool +
                ".csv", delimiter=";")
            first_row = df[name_metric].sum()
            return first_row
        except Exception as e:
            return 0

    @staticmethod
    def clean_file_and_directory():
        # remove file.java
        if os.path.exists(str(pathlib.Path().absolute()) + "/apache_repos/" + NAME_PROJECT + "/before.java"):
            os.remove(str(pathlib.Path().absolute()) + "/apache_repos/" + NAME_PROJECT + "/before.java")
        if os.path.exists(str(pathlib.Path().absolute()) + "/apache_repos/" + NAME_PROJECT + "/after.java"):
            os.remove(str(pathlib.Path().absolute()) + "/apache_repos/" + NAME_PROJECT + "/after.java")
        # remove directory of metric
        if os.path.exists(str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/" + NAME_PROJECT):
            shutil.rmtree(str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/" + NAME_PROJECT)
