import javalang
from javalang.tree import ClassDeclaration
import operator
import os


class Filter:

    def __init__(self):
        self.before_contents = ['']
        self.after_contents = ['']
        self.line_before_file = []
        self.line_after_file = []


    @staticmethod
    def find_java_file(list_of_file):
        """
       :return:
            list of file.java without Test.java
        """
        list_file = list()
        for file in list_of_file:
            if file.endswith(".java") and not file.endswith("Test.java"):
                list_file.append(file)
        return list_file

    # function from javadiff - https://github.com/amir9979/javadiff
    def get_relevant_lines(self, diff, first_commit=None, second_commit=None):
        self.before_contents = self.get_before_content_from_diff(diff, first_commit)
        self.after_contents = self.get_after_content_from_diff(diff, second_commit)
        self.before_contents = list(map(lambda x: x.decode("utf-8", errors='ignore'), self.before_contents))
        self.after_contents = list(map(lambda x: x.decode("utf-8", errors='ignore'), self.after_contents))
        self.line_before_file = self.find_use_line(self.before_contents)
        self.line_after_file = self.find_use_line(self.after_contents)
        return self.line_before_file, self.line_after_file

    def find_use_line(self, contents):
        """""
        This method return list of line that contain code of mathod
        :parameter:
            contents - source file
        """""
        tokens = list(javalang.tokenizer.tokenize("".join(contents)))
        parser = javalang.parser.Parser(tokens)
        parsed_data = parser.parse()
        list_ans = self.get_methods_by_javalang(tokens, parsed_data)
        if list_ans:
            return [item for sublist in list_ans for item in sublist]
        return None

    # @staticmethod
    # def get_methods_by_javalang(tokens, parsed_data):
    #     def get_method_end_position(method, seperators):
    #         method_seperators = seperators[list(map(id, sorted(seperators + [method],
    #                                                            key=lambda x: (
    #                                                                x.position.line, x.position.column)))).index(
    #             id(method)):]
    #         assert method_seperators[0].value == "{"
    #         counter = 1
    #         for seperator in method_seperators[1:]:
    #             if seperator.value == "{":
    #                 counter += 1
    #             elif seperator.value == "}":
    #                 counter -= 1
    #             if counter == 0:
    #                 return seperator.position
    #
    #     list_ans = list()
    #     used_lines = set(map(lambda t: t.position.line - 1, tokens))
    #     seperators = list(filter(lambda token: isinstance(token, javalang.tokenizer.Separator) and token.value in "{}",
    #                              tokens))
    #     classes_full = list(parsed_data.filter(javalang.tree.ClassDeclaration))  # tuple (position,class itself)
    #     for full_class in classes_full:
    #         class_path = full_class[0]
    #         class_declaration = full_class[1]
    #         if len(class_path) > 2:  # has parent class
    #             index = class_path.find('.')
    #             if index != -1:
    #                 class_name = class_path[0:index]
    #             class_name = class_name + "." + class_declaration.name
    #         else:
    #             class_name = class_declaration.name
    #         methods = list(map(operator.itemgetter(1), class_declaration.filter(javalang.tree.MethodDeclaration)))
    #         constructors = list(
    #             map(operator.itemgetter(1), class_declaration.filter(javalang.tree.ConstructorDeclaration)))
    #         for method in methods + constructors:
    #             if not method.body:
    #                 # skip abstract methods
    #                 continue
    #             method_start_position = method.position
    #             method_end_position = get_method_end_position(method, seperators)
    #             method_used_lines = list(
    #                 filter(lambda line: method_start_position.line - 1 <= line <= method_end_position.line, used_lines))
    #             list_ans.append(method_used_lines)
    #     return list_ans

    def get_methods_by_javalang(self, tokens, parsed_data, analyze_source_lines=True):
        def get_method_end_position(method, seperators):
            method_seperators = seperators[list(map(id, sorted(seperators + [method],
                                                          key=lambda x: (x.position.line, x.position.column)))).index(
                id(method)):]
            assert method_seperators[0].value == "{"
            counter = 1
            for seperator in method_seperators[1:]:
                if seperator.value == "{":
                    counter += 1
                elif seperator.value == "}":
                    counter -= 1
                if counter == 0:
                    return seperator.position

        used_lines = set(map(lambda t: t.position.line-1, tokens))
        seperators = list(filter(lambda token: isinstance(token, javalang.tokenizer.Separator) and token.value in "{}",
                            tokens))
        list_ans = list()
        for class_declaration in map(operator.itemgetter(1), parsed_data.filter(javalang.tree.ClassDeclaration)):
            methods = list(map(operator.itemgetter(1), class_declaration.filter(javalang.tree.MethodDeclaration)))
            constructors = list(map(operator.itemgetter(1), class_declaration.filter(javalang.tree.ConstructorDeclaration)))
            for method in methods + constructors:
                if not method.body:
                    # skip abstract methods
                    continue
                method_start_position = method.position
                method_end_position = get_method_end_position(method, seperators)
                method_used_lines = list(
                        filter(lambda line: method_start_position.line - 1 <= line <= method_end_position.line, used_lines))
                list_ans.append(method_used_lines)
            return list_ans

    @staticmethod
    def get_before_content_from_diff(diff, first_commit):
        """
        This function return the content of file before commit (parent)
        """
        before_contents = ['']
        if diff.new_file:
            assert diff.a_blob is None
        else:
            try:
                before_contents = diff.a_blob.data_stream.stream.readlines()
            except:
                if first_commit:
                    before_contents = first_commit.repo.git.show(
                        "{0}:{1}".format(first_commit.hexsha, diff.a_path)).split('\n')
        return before_contents

    @staticmethod
    def get_after_content_from_diff(diff, second_commit):
        """
            This function return the content of file after commit
        """
        after_contents = ['']
        if diff.deleted_file:
            assert diff.b_blob is None
        else:
            try:
                after_contents = diff.b_blob.data_stream.stream.readlines()
            except:
                if second_commit:
                    after_contents = second_commit.repo.git.show(
                        "{0}:{1}".format(second_commit.hexsha, diff.b_path)).split('\n')
        return after_contents

    @staticmethod
    def filter_file_line(relevant_line, source_file):
        if relevant_line is None:
            return
        update_source_file = []
        for line_number in range(0, len(source_file)):
            if line_number in relevant_line:
                update_source_file.append(source_file[line_number])
        return update_source_file

