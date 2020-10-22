import csv
import difflib
from collections import Counter


class MeasureDiff:
    def measure_diff(self, change_line):
        """
        create feature that compare text of file before commit and file after
        :param change_line:
        :return: list_feature
        """
        list_feature = []
        if change_line is None:
            return None
        self.character_change(change_line)
        number_add, number_remove, number_change_block = self.row_add_remove_block(change_line)
        list_feature.append(number_add)
        list_feature.append(number_remove)
        list_feature.append(number_add-number_remove)
        list_feature.append(number_change_block)
        character = self.character_change(change_line)
        list_feature.append(character)
        return list_feature

    @staticmethod
    def row_add_remove_block(change_line):
        """
        return number row add, number row remove and number block change
        block define  - Distinguished by a line that was not added or removed in commit
        :param change_line:
        :return: three feature
        """
        diff = difflib.Differ().compare(change_line[0], change_line[1])
        number_add = 0
        number_remove = 0
        block = True
        number_change_block = 0
        for i in diff:
            if i.startswith("+"):
                i = i[1:]
                i = i.lstrip()
                if not i.startswith("*") and not i.startswith("/**") and not i.startswith("//"):
                    number_add += 1
                if block:
                    number_change_block += 1
                    block = False
            elif i.startswith("-"):
                i = i[1:]
                i = i.lstrip()
                if not i.startswith("*") and not i.startswith("/**") and not i.startswith("//"):
                    number_remove += 1
                if block:
                    number_change_block += 1
                    block = False
            elif not i.startswith("?"):
                block = True
        return number_add, number_remove, number_change_block

    @staticmethod
    def character_change(change_line):
        """
        return the number of character that Different between two file
        remove character: " ", ""
        :param change_line:
        :return: one feature
        """

        list_before = change_line[0]
        chars_before = []
        for line in list_before:
            for c in line:
                chars_before.append(c)

        list_after = change_line[1]
        chars_after = []
        for line in list_after:
            for c in line:
                chars_after.append(c)
        dic_after = Counter(chars_after)
        dic_before = Counter(chars_before)
        if '' in dic_after:
            dic_after.pop('')
        if '' in dic_before:
            dic_before.pop('')
        if ' ' in dic_after:
            dic_after.pop(' ')
        if ' ' in dic_before:
            dic_before.pop(' ')
        list_character = [abs(dic_after[x] - dic_before[x]) for x in dic_after if x in dic_before]
        keys1 = dic_before.keys()
        keys2 = dic_after.keys()
        difference = keys1 - keys2
        value = 0
        for i in difference:
            value += dic_before[i]
        return value + sum(list_character)

    @staticmethod
    def find_feature(list_feature, file_change, commit):
        with open('File/feature_of_commit_solve_issue.csv', 'a', newline='', encoding="utf-8") as file:
            writer = csv.writer(file, delimiter='')
            try:
                file.write(str(commit))
                file.write(',')
                file.write(str(file_change))
                file.write(',')
                for feature in list_feature:
                    file.write(str(feature))
                    file.write(',')
                file.write('\n')
                file.flush()
            except Exception as e:
                # raise e
                pass
