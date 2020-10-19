import csv
import os
import pathlib
import sqlite3
import pandas as pd
import numpy as np


class MeasureToken:

    def __init__(self):
        """"
            Init the connection of DB
        """
        DB_PATH = r"C:\Users\shir0\Commits-Issues-DB\CommitIssueDB.db"
        # Get DB connection
        self.db_connection = sqlite3.connect(DB_PATH)
        print("connection established")
        if os.path.exists(str(pathlib.Path().absolute()) +"/File/before_token.csv"):
            os.remove(str(pathlib.Path().absolute()) + "/File/before_token.csv")
        if os.path.exists(str(pathlib.Path().absolute()) + "/File/after_token.csv"):
            os.remove(str(pathlib.Path().absolute()) + "/File/after_token.csv")
        with open(str(pathlib.Path().absolute()) + '/File/after_token.csv', 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Member', 'FieldDeclaration', 'VariableDeclaration', 'LocalVariableDeclaration',
                             'VariableDeclarator', 'Literal', 'This', 'MemberReference'])
        with open(str(pathlib.Path().absolute()) + '/File/before_token.csv', 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Member', 'FieldDeclaration', 'VariableDeclaration', 'LocalVariableDeclaration',
                             'VariableDeclarator', 'Literal', 'This', 'MemberReference'])

    def get_feature(self, commit, file_change):
        """"
            Main function that return list of feature
            parameter:
                parent(commit)
                commit(commit)
                file change - file that change
            return:
                return list of feature
        """
        dic_before = self.find_meaning(commit, file_change, "OLD")
        if dic_before is None:
            return None
        self.write_value_without_sub(dic_before, "before_token", commit, file_change)
        dic_after = self.find_meaning(commit, file_change, "NEW")
        if dic_after is None:
            return None
        self.write_value_without_sub(dic_after, "after_token", commit, file_change)
        feature = {x: dic_after[x] - dic_before[x] for x in dic_before if x in dic_after}
        list_ans = [feature["'Member'"], feature["'FieldDeclaration'"], feature["'VariableDeclaration'"],
                    feature["'LocalVariableDeclaration'"], feature["'VariableDeclarator'"], feature["'Literal'"],
                    feature["'This'"], feature["'MemberReference'"]]
        return list_ans

    def find_meaning(self, commit, file_change, new_or_old):
        """"
            help function that return dictionary of measure
            parameter:
                commit(commit)
                file change - file that change
            return:
                return dictionary of measure
        """
        try:
            query_method_data = "SELECT * FROM MethodData WHERE NewPath =='" + str(file_change) + "'AND CommitID = '" +\
                                str(commit) + "' AND "  "OldNew == '" + new_or_old + "' "

            sql_query = pd.read_sql_query(query_method_data, self.db_connection)
            if sql_query.empty:
                return None
            df = pd.DataFrame(sql_query, columns=['Meaning'])

            dic = {"'Member'": 0, "'FieldDeclaration'": 0, "'VariableDeclaration'": 0, "'LocalVariableDeclaration'": 0,
                   "'VariableDeclarator'": 0, "'Literal'": 0, "'This'": 0, "'MemberReference'": 0}
            for index, line in df.iterrows():
                # remove{'BlockStatement': 1, 'LocalVariableDeclaration': 1}
                line = str(line.values)
                line = line[3:len(line) - 3]
                split_line = line.split(", ")
                for meaning in split_line:
                    get_number = meaning.split(": ")
                    if get_number[0] in dic.keys():
                        dic[get_number[0]] += int(get_number[1])
            return dic
        except Exception as e:
            print(e)
            pass
            return None

    @staticmethod
    def write_value_without_sub(dic, name_file, commit, file_change):
        with open('File/' + name_file + '.csv', 'a', newline='', encoding="utf-8") as file:
            file.write("\n")
            file.write("%s,%s," % (commit, file_change))
            for key in dic.keys():
                file.write(",%s" % (dic[key]))

    def close_connection(self):
        self.db_connection.close()


if __name__ == '__main__':
    measure_token = MeasureToken()
    measure_token.get_feature('0b748abd186ea0d9e10b4a5b43ec4f410ebbc64f', 'src/main/java/org/apache/commons/lang3/Conversion.java')
