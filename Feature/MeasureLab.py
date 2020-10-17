from Code_lab.projects import Project
import pandas as pd
import os
import shutil
from Code_lab.metrics.version_metrics import SourceMonitor, CK, Designite, Checkstyle, Halstead
import pathlib

# parameter  for checkstyle
MAX_AnonInnerLength = 50
MAX_BooleanExpression = 3
MAX_CyclomaticComplexity = 7
MAX_MethodLength = 60
MAX_ReturnCount = 3
MAX_ClassFanOutComplexity = 2


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
        self.measure_checkstyle(list_before_error, list_after_error)

        # metric lab
        self.clean_file_and_directory()
        # before
        self.write_file(file_before, str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/before")
        self.measure_lab_init()
        self.measure_lab(self.list_before)
        self.clean_file_and_directory()
        # after
        self.write_file(file_after, str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/after")
        self.measure_lab_init()
        self.measure_lab(self.list_after)
        self.clean_file_and_directory()

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
                    file.write('%s\n' % line)
        except Exception as e:
            pass

    @staticmethod
    def run_checkstyle(name_file, name_measure):
        os.system('java -jar ' + str(pathlib.Path().absolute()) + "\..\Checker\checkstyle-8.31-all.jar -c " + str(
            pathlib.Path().absolute()) + '\..\Checker\\' + name_measure + ".xml File/" + name_file + ".java -o File/" +
                  name_file + ".txt")

    def measure_checkstyle(self, list_before_error, list_after_error):
        """
          get all feature of checkstyle
        """
        # 1 - AnonInnerLength
        self.list_sum.append(self.sum_of_anonymous_inner_class(list_after_error, "[AnonInnerLength]", MAX_AnonInnerLength)
                             - self.sum_of_anonymous_inner_class(list_before_error, "[AnonInnerLength]", MAX_AnonInnerLength))

        # 2 - AvoidInlineConditionals
        self.list_sum.append(self.sum_of_line(list_after_error, "[AvoidInlineConditionals]") -
                             self.sum_of_line(list_before_error, "[AvoidInlineConditionals]"))

        # 3 - BooleanExpressionComplexity
        self.list_sum.append(self.sum_of_boolean_expression_complexity(list_after_error, "[BooleanExpressionComplexity]",
                                                              MAX_BooleanExpression)
                             - self.sum_of_boolean_expression_complexity(list_before_error, "[BooleanExpressionComplexity]",
                                                               MAX_BooleanExpression))

        # 4 - CovariantEquals
        self.list_sum.append(self.sum_of_line(list_after_error, "[CovariantEquals]")
                             - self.sum_of_line(list_before_error, "[CovariantEquals]"))

        # 5 - ClassTypeParameterName
        self.list_sum.append(self.sum_of_line(list_after_error, "[ClassTypeParameterName]") -
                             self.sum_of_line(list_before_error, "[ClassTypeParameterName]"))

        # 6 - CatchParameterName
        self.list_sum.append(self.sum_of_line(list_after_error, "[CatchParameterName]") -
                             self.sum_of_line(list_before_error, "[CatchParameterName]"))

        # 7 - EmptyBlock
        self.list_sum.append(self.sum_of_line(list_after_error, "[EmptyBlock]") -
                             self.sum_of_line(list_before_error, "[EmptyBlock]"))

        # 8 - EmptyStatement
        self.list_sum.append(self.sum_of_line(list_after_error, "[EmptyStatement]") -
                             self.sum_of_line(list_before_error, "[EmptyStatement]"))

        # 9 -EqualsHashCode
        self.list_sum.append(self.sum_of_line(list_after_error, "[EqualsHashCode]") -
                             self.sum_of_line(list_before_error, "[EqualsHashCode]"))

        # 10 -CyclomaticComplexity
        self.list_sum.append(self.sum_of_cyclomatic_complexity(list_after_error, "[CyclomaticComplexity]",
                                                      MAX_CyclomaticComplexity) -
                             self.sum_of_cyclomatic_complexity(list_before_error, "[CyclomaticComplexity]",
                                                               MAX_CyclomaticComplexity))

        # 11 - line length

        self.list_sum.append(self.sum_of_found(list_after_error, "[LineLength]") -
                             self.sum_of_found(list_before_error, "[LineLength]"))

        # 12 -MethodLength
        self.list_sum.append(self.sum_of_method_length(list_after_error, "[MethodLength]", MAX_MethodLength) -
                             self.sum_of_method_length(list_before_error, "[MethodLength]", MAX_MethodLength))

        # 13 - MissingSwitchDefault
        self.list_sum.append(self.sum_of_line(list_after_error, "[MissingSwitchDefault]") -
                             self.sum_of_line(list_before_error, "[MissingSwitchDefault]"))

        # 14 - ReturnCount
        self.list_sum.append(self.sum_of_return_count(list_after_error, "[ReturnCount]", MAX_ReturnCount)
                             - self.sum_of_return_count(list_before_error, "[ReturnCount]", MAX_ReturnCount))

        # 15 - ReturnCount
        self.list_sum.append(self.sum_of_line(list_after_error, "[StringLiteralEquality]") -
                             self.sum_of_line(list_before_error, "[StringLiteralEquality]"))

        # 16 - TodoComment
        self.list_sum.append(self.sum_of_line(list_after_error, "[TodoComment]") -
                             self.sum_of_line(list_before_error, "[TodoComment]"))

        # 17 - ClassFanOutComplexity
        self.list_sum.append(self.sum_of_class_fan_out_complexity(list_after_error, "[ClassFanOutComplexity]",
                                                         MAX_ClassFanOutComplexity)
                             - self.sum_of_class_fan_out_complexity(list_before_error, "[ClassFanOutComplexity]",
                                                          MAX_ClassFanOutComplexity))

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
    def measure_lab_init():
        try:
            number = 0
            d = Designite(Project("commons-lang", "Lang"), '', None)
            d.extract()
            number = 1
            cs = Checkstyle(Project("commons-lang", "Lang"), '', None)
            cs.extract()
            number = 2
            h = Halstead(Project("commons-lang", "Lang"), '', None)
            h.extract()
            number = 3
            c = CK(Project("commons-lang", "Lang"), '', None)
            c.extract()
            number = 4
            sm = SourceMonitor(Project("commons-lang", "Lang"), '', None)
            sm.extract()
            # TODO Wrong number of items passed 3, placement implies 1
        except Exception as e:
            print("measure_lab ", number)
            print(e)
            pass

    def measure_lab(self, list):
        # Designite Java
        list.append(self.get_metric_sum_column("designite_implementation", "Long Parameter List"))
        list.append(self.get_metric_sum_column("designite_implementation", "Complex Conditional"))
        list.append(self.get_metric_sum_column("designite_implementation", "Complex Method"))

        # checkstyle
        list.append(self.get_metric_sum_column("checkstyle", "Nested_if-else_depth"))
        list.append(self.get_metric_first_row("checkstyle", "NCSS_for_this_file"))
        list.append(self.get_metric_first_row("checkstyle", "File_length"))
        list.append(self.get_metric_sum_column("checkstyle", "NPath_Complexity"))
        list.append( self.get_metric_first_row("checkstyle", "Number_of_public_methods"))
        list.append(self.get_metric_first_row("checkstyle", "Total_number_of_methods"))

        # CK
        list.append(self.get_metric_sum_column("ck", "wmc"))
        list.append(self.get_metric_sum_column("ck", "loopQty"))
        list.append(self.get_metric_sum_column("ck", "comparisonsQty"))
        list.append(self.get_metric_sum_column("ck", "maxNestedBlocks"))
        list.append(self.get_metric_sum_column("ck", "lambdasQty"))
        list.append(self.get_metric_sum_column("ck", "cbo"))
        list.append(self.get_metric_sum_column("ck", "variables"))
        list.append(self.get_metric_sum_column("ck", "tryCatchQty"))
        list.append(self.get_metric_sum_column("ck", "parenthesizedExpsQty"))
        list.append(self.get_metric_sum_column("ck", "stringLiteralsQty"))
        list.append(self.get_metric_sum_column("ck", "numbersQty"))
        list.append(self.get_metric_sum_column("ck", "assignmentsQty"))
        list.append(self.get_metric_sum_column("ck", "mathOperationsQty"))
        list.append(self.get_metric_sum_column("ck", "uniqueWordsQty"))
        list.append(self.get_metric_sum_column("ck", "modifiers"))
        list.append(self.get_metric_sum_column("ck", "logStatementsQty"))
        # Halstead
        list.append(self.get_metric_sum_column("halstead", "getDifficulty"))
        list.append(self.get_metric_sum_column("halstead", "getVolume"))
        list.append(self.get_metric_sum_column("halstead", "getDistinctOperandsCnt"))
        list.append(self.get_metric_sum_column("halstead", "getDistinctOperatorsCnt"))
        list.append(self.get_metric_sum_column("halstead", "getEffort"))
        list.append(self.get_metric_sum_column("halstead", "getTotalOparandsCnt"))
        list.append(self.get_metric_sum_column("halstead", "getTotalOperatorsCnt"))
        list.append(self.get_metric_sum_column("halstead", "getVocabulary"))

    @staticmethod
    def get_metric_sum_column(name_tool, name_metric):
        try:
            df = pd.read_csv(
                str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/commons-lang/" + name_tool +
                ".csv", delimiter=";")
            sum_column = df[name_metric].sum()
            return sum_column
        except Exception as e:
            return 0

    @staticmethod
    def get_metric_first_row(name_tool, name_metric):
        try:
            df = pd.read_csv(
                str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/commons-lang/" + name_tool +
                ".csv", delimiter=";")
            first_row = df[name_metric].sum()
            return first_row
        except Exception as e:
            return 0

    @staticmethod
    def clean_file_and_directory():
        # remove file.java
        if os.path.exists(str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/before.java"):
            os.remove(str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/before.java")
        if os.path.exists(str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/after.java"):
            os.remove(str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/after.java")
        # remove directory of metric
        if os.path.exists(str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/commons-lang"):
            shutil.rmtree(str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/commons-lang")


