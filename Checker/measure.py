import os

# from metrics.version_metrics import CK, SourceMonitor, Designite, Checkstyle, Bugged, BuggedMethods, Halstead
from Code_lab.projects import Project
import pandas as pd
import os
import shutil

from Code_lab.metrics.version_metrics import SourceMonitor, CK, Designite, Checkstyle, Halstead
import pathlib

MAX_AnonInnerLength = 50
MAX_BooleanExpression = 3
MAX_CyclomaticComplexity = 7
MAX_MethodLength = 60
MAX_ReturnCount = 3
MAX_ClassFanOutComplexity = 2


def main_measure(file_before, file_after):
    write_file(file_before, "File/before")
    write_file(file_after, "File/after")

    list_sum = list()

    # checkstyle
    run_checkstyle("before", "checkstyle")
    run_checkstyle("after", "checkstyle")
    list_before_error, list_after_error = get_list_error()
    measure_checkstyle(list_sum, list_before_error, list_after_error)

    # metric lab
    clean_file_and_directory()

    write_file(file_before, str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/before")
    measure_lab()

    # Designite Java
    Long_Parameter_List_before = get_metric_sum_column("designite_implementation", "Long Parameter List")
    Complex_Conditional_before = get_metric_sum_column("designite_implementation", "Complex Conditional")
    Complex_Method_before = get_metric_sum_column("designite_implementation", "Complex Method")

    # checkstyle
    nested_if_else_dept_before = get_metric_sum_column("checkstyle", "Nested_if-else_depth")
    NCSS_before = get_metric_first_row("checkstyle", "NCSS_for_this_file")
    File_length_before = get_metric_first_row("checkstyle", "File_length")
    NPath_Complexity_before = get_metric_sum_column("checkstyle", "NPath_Complexity")
    Number_of_public_methods_before = get_metric_first_row("checkstyle", "Number_of_public_methods")
    Total_number_of_methods_before = get_metric_first_row("checkstyle", "Total_number_of_methods")

    # CK
    wmc_before = get_metric_sum_column("ck", "wmc")
    loopQty_before = get_metric_sum_column("ck", "loopQty")
    comparisonsQty_before = get_metric_sum_column("ck", "comparisonsQty")
    maxNestedBlocks_before = get_metric_sum_column("ck", "maxNestedBlocks")
    lambdasQty_before = get_metric_sum_column("ck", "lambdasQty")
    cbo_before = get_metric_sum_column("ck", "cbo")
    variables_before = get_metric_sum_column("ck", "variables")
    tryCatchQty_before = get_metric_sum_column("ck", "tryCatchQty")
    parenthesizedExpsQty_before = get_metric_sum_column("ck", "parenthesizedExpsQty")
    stringLiteralsQty_before = get_metric_sum_column("ck", "stringLiteralsQty")
    numbersQty_before = get_metric_sum_column("ck", "numbersQty")
    assignmentsQty_before = get_metric_sum_column("ck", "assignmentsQty")
    mathOperationsQty_before = get_metric_sum_column("ck", "mathOperationsQty")
    uniqueWordsQty_before = get_metric_sum_column("ck", "uniqueWordsQty")
    modifiers_before = get_metric_sum_column("ck", "modifiers")
    logStatementsQty_before = get_metric_sum_column("ck", "logStatementsQty")
    # Halstead
    difficulty_before = get_metric_sum_column("halstead", "getDifficulty")
    volume_before = get_metric_sum_column("halstead", "getVolume")
    getDistinctOperandsCnt_before = get_metric_sum_column("halstead", "getDistinctOperandsCnt")
    getDistinctOperatorsCnt_before = get_metric_sum_column("halstead", "getDistinctOperatorsCnt")
    getEffort_before = get_metric_sum_column("halstead", "getEffort")
    getTotalOparandsCnt_before = get_metric_sum_column("halstead", "getTotalOparandsCnt")
    getTotalOperatorsCnt_before = get_metric_sum_column("halstead", "getTotalOperatorsCnt")
    getVocabulary_before = get_metric_sum_column("halstead", "getVocabulary")

    clean_file_and_directory()

    write_file(file_after, str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/after")
    measure_lab()

    # Designite Java
    Long_Parameter_List_after = get_metric_sum_column("designite_implementation", "Long Parameter List")
    Complex_Conditional_after = get_metric_sum_column("designite_implementation", "Complex Conditional")
    Complex_Method_after = get_metric_sum_column("designite_implementation", "Complex Method")

    # checkstyle
    nested_if_else_dept_after = get_metric_sum_column("checkstyle", "Nested_if-else_depth")
    NCSS_after = get_metric_first_row("checkstyle", "NCSS_for_this_file")
    File_length_after = get_metric_first_row("checkstyle", "File_length")
    NPath_Complexity_after = get_metric_sum_column("checkstyle", "NPath_Complexity")
    Number_of_public_methods_after = get_metric_first_row("checkstyle", "Number_of_public_methods")
    Total_number_of_methods_after = get_metric_first_row("checkstyle", "Total_number_of_methods")

    # CK
    wmc_after = get_metric_sum_column("ck", "wmc")
    loopQty_after = get_metric_sum_column("ck", "loopQty")
    comparisonsQty_after = get_metric_sum_column("ck", "comparisonsQty")
    maxNestedBlocks_after = get_metric_sum_column("ck", "maxNestedBlocks")
    lambdasQty_after = get_metric_sum_column("ck", "lambdasQty")
    cbo_after = get_metric_sum_column("ck", "cbo")
    variables_after = get_metric_sum_column("ck", "variables")
    tryCatchQty_after = get_metric_sum_column("ck", "tryCatchQty")
    parenthesizedExpsQty_after = get_metric_sum_column("ck", "parenthesizedExpsQty")
    stringLiteralsQty_after = get_metric_sum_column("ck", "stringLiteralsQty")
    numbersQty_after = get_metric_sum_column("ck", "numbersQty")
    assignmentsQty_after = get_metric_sum_column("ck", "assignmentsQty")
    mathOperationsQty_after = get_metric_sum_column("ck", "mathOperationsQty")
    uniqueWordsQty_after = get_metric_sum_column("ck", "uniqueWordsQty")
    modifiers_after = get_metric_sum_column("ck", "modifiers")
    logStatementsQty_after = get_metric_sum_column("ck", "logStatementsQty")

    # Halstead
    difficulty_after = get_metric_sum_column("halstead", "getDifficulty")
    volume_after = get_metric_sum_column("halstead", "getVolume")
    getDistinctOperandsCnt_after = get_metric_sum_column("halstead", "getDistinctOperandsCnt")
    getDistinctOperatorsCnt_after = get_metric_sum_column("halstead", "getDistinctOperatorsCnt")
    getEffort_after = get_metric_sum_column("halstead", "getEffort")
    getTotalOparandsCnt_after = get_metric_sum_column("halstead", "getTotalOparandsCnt")
    getTotalOperatorsCnt_after = get_metric_sum_column("halstead", "getTotalOperatorsCnt")
    getVocabulary_after = get_metric_sum_column("halstead", "getVocabulary")

    clean_file_and_directory()

    # save in list

    # Designite Java
    list_sum.append(Long_Parameter_List_after - Long_Parameter_List_before)
    list_sum.append(Complex_Conditional_after - Complex_Conditional_before)
    list_sum.append(Complex_Method_after - Complex_Method_before)

    # checkstyle
    list_sum.append(nested_if_else_dept_after - nested_if_else_dept_before)
    list_sum.append(NCSS_after - NCSS_before)
    list_sum.append(File_length_after - File_length_before)
    list_sum.append(NPath_Complexity_after - NPath_Complexity_before)
    list_sum.append(Number_of_public_methods_after - Number_of_public_methods_before)
    list_sum.append(Total_number_of_methods_after - Total_number_of_methods_before)
    # CK
    list_sum.append(wmc_after - wmc_before)
    list_sum.append(loopQty_after - loopQty_before)
    list_sum.append(comparisonsQty_after - comparisonsQty_before)
    list_sum.append(maxNestedBlocks_after - maxNestedBlocks_before)
    list_sum.append(lambdasQty_after - lambdasQty_before)
    list_sum.append(cbo_after - cbo_before)
    list_sum.append(variables_after - variables_before)
    list_sum.append(tryCatchQty_after - tryCatchQty_before)
    list_sum.append(parenthesizedExpsQty_after - parenthesizedExpsQty_before)
    list_sum.append(stringLiteralsQty_after - stringLiteralsQty_before)
    list_sum.append(numbersQty_after - numbersQty_before)
    list_sum.append(assignmentsQty_after - assignmentsQty_before)
    list_sum.append(mathOperationsQty_after - mathOperationsQty_before)
    list_sum.append(uniqueWordsQty_after - uniqueWordsQty_before)
    list_sum.append(modifiers_after - modifiers_before)
    list_sum.append(logStatementsQty_after - logStatementsQty_before)

    # Halstead
    list_sum.append(difficulty_after - difficulty_before)
    list_sum.append(volume_after - volume_before)
    list_sum.append(getDistinctOperandsCnt_after - getDistinctOperandsCnt_before)
    list_sum.append(getDistinctOperatorsCnt_after - getDistinctOperatorsCnt_before)
    list_sum.append(getEffort_after - getEffort_before)
    list_sum.append(getTotalOparandsCnt_after - getTotalOparandsCnt_before)
    list_sum.append(getTotalOperatorsCnt_after - getTotalOperatorsCnt_before)
    list_sum.append(getVocabulary_after - getVocabulary_before)

    return list_feature(list_sum)


def write_file(list_java_file, name_file):
    try:
        with open(name_file + '.java', 'w') as file:
            for line in list_java_file:
                file.write('%s\n' % line)
    except Exception as e:
        pass


def run_checkstyle(name_file, name_measure):
    os.system('java -jar ' + str(pathlib.Path().absolute()) + "\..\Checker\checkstyle-8.31-all.jar -c " + str(
        pathlib.Path().absolute()) + '\..\Checker\\' + name_measure + ".xml File/" + name_file + ".java -o File/" + name_file + ".txt")

def measure_checkstyle(list_sum, list_before_error, list_after_error):
    # 1 - AnonInnerLength
    sum_before = sum_of_anonymous_inner_class(list_before_error, "[AnonInnerLength]", MAX_AnonInnerLength)
    sum_after = sum_of_anonymous_inner_class(list_after_error, "[AnonInnerLength]", MAX_AnonInnerLength)
    list_sum.append(sum_after - sum_before)

    # 2 - AvoidInlineConditionals
    sum_before = sum_of_line(list_before_error, "[AvoidInlineConditionals]")
    sum_after = sum_of_line(list_after_error, "[AvoidInlineConditionals]")
    list_sum.append(sum_after - sum_before)

    # 3 - BooleanExpressionComplexity
    sum_before = sum_of_boolean_expression_complexity(list_before_error, "[BooleanExpressionComplexity]",
                                                      MAX_BooleanExpression)
    sum_after = sum_of_boolean_expression_complexity(list_after_error, "[BooleanExpressionComplexity]",
                                                     MAX_BooleanExpression)
    list_sum.append(sum_after - sum_before)

    # 4 - CovariantEquals
    sum_before = sum_of_line(list_before_error, "[CovariantEquals]")
    sum_after = sum_of_line(list_after_error, "[CovariantEquals]")
    list_sum.append(sum_after - sum_before)

    # 5 - ClassTypeParameterName
    sum_before = sum_of_line(list_before_error, "[ClassTypeParameterName]")
    sum_after = sum_of_line(list_after_error, "[ClassTypeParameterName]")
    list_sum.append(sum_after - sum_before)

    # 6 - CatchParameterName
    sum_before = sum_of_line(list_before_error, "[CatchParameterName]")
    sum_after = sum_of_line(list_after_error, "[CatchParameterName]")
    list_sum.append(sum_after - sum_before)

    # 7 - EmptyBlock
    sum_before = sum_of_line(list_before_error, "[EmptyBlock]")
    sum_after = sum_of_line(list_after_error, "[EmptyBlock]")
    list_sum.append(sum_after - sum_before)

    # 8 - EmptyStatement
    sum_before = sum_of_line(list_before_error, "[EmptyStatement]")
    sum_after = sum_of_line(list_after_error, "[EmptyStatement]")
    list_sum.append(sum_after - sum_before)

    # 9 -EqualsHashCode
    sum_before = sum_of_line(list_before_error, "[EqualsHashCode]")
    sum_after = sum_of_line(list_after_error, "[EqualsHashCode]")
    list_sum.append(sum_after - sum_before)

    # 10 -CyclomaticComplexity
    sum_before = sum_of_cyclomatic_complexity(list_before_error, "[CyclomaticComplexity]",
                                              MAX_CyclomaticComplexity)
    sum_after = sum_of_cyclomatic_complexity(list_after_error, "[CyclomaticComplexity]",
                                             MAX_CyclomaticComplexity)
    list_sum.append(sum_after - sum_before)

    # 11 - line length
    sum_before = sum_of_found(list_before_error, "[LineLength]")
    sum_after = sum_of_found(list_after_error, "[LineLength]")
    list_sum.append(sum_after - sum_before)

    # 12 -MethodLength
    sum_before = sum_of_method_length(list_before_error, "[MethodLength]", MAX_MethodLength)
    sum_after = sum_of_method_length(list_after_error, "[MethodLength]", MAX_MethodLength)
    list_sum.append(sum_after - sum_before)

    # 13 - MissingSwitchDefault
    sum_before = sum_of_line(list_before_error, "[MissingSwitchDefault]")
    sum_after = sum_of_line(list_after_error, "[MissingSwitchDefault]")
    list_sum.append(sum_after - sum_before)

    # 14 - ReturnCount
    sum_before = sum_of_return_count(list_before_error, "[ReturnCount]", MAX_ReturnCount)
    sum_after = sum_of_return_count(list_after_error, "[ReturnCount]", MAX_ReturnCount)
    list_sum.append(sum_after - sum_before)

    # 15 - ReturnCount
    sum_before = sum_of_line(list_before_error, "[StringLiteralEquality]")
    sum_after = sum_of_line(list_after_error, "[StringLiteralEquality]")
    list_sum.append(sum_after - sum_before)

    # 16 - TodoComment
    sum_before = sum_of_line(list_before_error, "[TodoComment]")
    sum_after = sum_of_line(list_after_error, "[TodoComment]")
    list_sum.append(sum_after - sum_before)

    # 17 - ClassFanOutComplexity
    sum_before = sum_of_class_fan_out_complexity(list_before_error, "[ClassFanOutComplexity]",
                                                 MAX_ClassFanOutComplexity)
    sum_after = sum_of_class_fan_out_complexity(list_after_error, "[ClassFanOutComplexity]",
                                                MAX_ClassFanOutComplexity)
    list_sum.append(sum_after - sum_before)


def get_list_error():
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
def sum_of_line(list_error_with_found, name_error):
    sum_line = 0
    for line in list_error_with_found:
        if line.find("Starting audit...") == -1 and line.find("Audit done.") == -1 and line.find(name_error) != -1:
            sum_line += 1
    return sum_line


# ------------------------------ DesigniteJava


def run_DesigniteJava():
    os.system('java -jar ' + str(pathlib.Path().absolute()) + '/../Checker/DesigniteJava.jar -i "File\DesigniteJava" -o '
                                                        '"File\DesigniteJava\DesigniteJava_error.txt"')


def read_error():
    line_error = list()
    with open("File/DesigniteJava/DesigniteJava_error.txt") as fp:
        lines = fp.readlines()
        for line in lines:
            line_error.append(line)
    return line_error


def long_parameter_list(line_error):
    # Long parameter list:
    for line in line_error:
        if line.find("Long parameter list") != -1:
            index_start = line.find("Long parameter list:")
            index_end = line.find("	Long statement")
            line = line[index_start + 20:index_end]
            return int(line)
    return 0


def complex_method(line_error):
    # Complex method:
    for line in line_error:
        if line.find("Complex method:") != -1:
            index_start = line.find("Complex method:")
            index_end = line.find("	Empty catch clause:")
            line = line[index_start + 15:index_end]
            return int(line)
    return 0


def complex_conditional(line_error):
    # Complex conditional:
    for line in line_error:
        if line.find("Complex conditional:") != -1:
            index_start = line.find("Complex conditional:")
            line = line[index_start + 20:]
            return int(line)
    return 0


def measure_lab():
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


def get_metric_sum_column(name_tool, name_metric):
    try:
        df = pd.read_csv(str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/commons-lang/" + name_tool +
                         ".csv", delimiter=";")
        sum_column = df[name_metric].sum()
        return sum_column
    except Exception as e:
        return 0


def get_metric_first_row(name_tool, name_metric):
    try:
        df = pd.read_csv(str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/commons-lang/" + name_tool +
                         ".csv", delimiter=";")
        first_row = df[name_metric].sum()
        return first_row
    except Exception as e:
        return 0


def clean_file_and_directory():
    # remove file.java
    if os.path.exists(str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/before.java"):
        os.remove(str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/before.java")
    if os.path.exists(str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/after.java"):
        os.remove(str(pathlib.Path().absolute()) + "/apache_repos/commons-lang/after.java")
    # remove directory of metric
    if os.path.exists(str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/commons-lang"):
        shutil.rmtree(str(pathlib.Path().absolute()) + "/../Code_lab/repository_data/metrics/commons-lang")


def list_feature(list_sum):
    list_commit = list()
    for feature in list_sum:
        list_commit.append(feature)
    return list_commit
