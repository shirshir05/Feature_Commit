import copy
import csv
import json
import os
import pathlib
import sqlite3
import pandas as pd


DIC = {}


class MeasureMeaning:

    def __init__(self):
        """"
            Init the connection of DB
        """
        DB_PATH = r"C:\Users\shir0\Commits-Issues-DB\CommitIssueDB.db"
        # Get DB connection
        self.db_connection = sqlite3.connect(DB_PATH)
        print("connection established")
        self.init_dic()

        if os.path.exists(str(pathlib.Path().absolute()) +"/File/before_token.csv"):
            os.remove(str(pathlib.Path().absolute()) + "/File/before_token.csv")
        if os.path.exists(str(pathlib.Path().absolute()) + "/File/after_token.csv"):
            os.remove(str(pathlib.Path().absolute()) + "/File/after_token.csv")
        if os.path.exists(str(pathlib.Path().absolute()) + "/File/NOT_in_DB.csv"):
            os.remove(str(pathlib.Path().absolute()) + "/File/NOT_in_DB.csv")

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
        dic_after = self.find_meaning(commit, file_change, "NEW")
        if dic_before is None and dic_after is None:
            # self.write_NOT_in_DB(0, 0, str(commit), file_change)
            return None
        # self.write_value_without_sub(dic_before, "before_token", commit, file_change)
        # self.write_value_without_sub(dic_after, "after_token", commit, file_change)
        if dic_before is None:
            # self.write_NOT_in_DB(0, 1, str(commit), file_change)
            dic_before = copy.copy(DIC)
        elif dic_after is None:
            # self.write_NOT_in_DB(1, 0, str(commit), file_change)
            dic_after = copy.copy(DIC)

        list_ans = self.dic_to_list(dic_before)
        list_ans += self.dic_to_list(dic_after)
        feature_delta = {x: dic_after[x] - dic_before[x] for x in dic_before if x in dic_after}
        list_ans += self.dic_to_list(feature_delta)
        return list_ans

    @staticmethod
    def dic_to_list(feature):
        list_ans = []
        for i in feature.keys():
            list_ans.append(feature[i])
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
            query_method_data = f"SELECT * FROM MethodData WHERE NewPath ==' {str(file_change)} ' AND CommitID = ' {str(commit)} ' AND OldNew == ' {new_or_old}'"

            sql_query = pd.read_sql_query(query_method_data, self.db_connection)
            if sql_query.empty:
                return None
            df = pd.DataFrame(sql_query, columns=['Meaning'])
            dic = copy.copy(DIC)
            for index, line in df.iterrows():
                if line.values == [None] or line.values is None: continue
                # remove{'BlockStatement': 1, 'LocalVariableDeclaration': 1}
                json_line = json.loads(str(line.values).replace("\\\'", '"')[3:-3])
                for meaning in json_line.keys():
                    if meaning in dic.keys():
                        dic[meaning] += json_line[meaning]
            return dic
        except Exception as e:
            print(e)
            pass
            return None

    @staticmethod
    def write_value_without_sub(dic, name_file, commit, file_change):
        if dic is None:
            return
        with open('File/' + name_file + '.csv', 'a', newline='', encoding="utf-8") as file:
            file.write("\n")
            file.write("%s,%s," % (commit, file_change))
            for key in dic.keys():
                file.write(",%s" % (dic[key]))

    def close_connection(self):
        self.db_connection.close()

    @staticmethod
    def write_NOT_in_DB(dic_before, dic_after, commit, file_change):
        with open('File/NOT_in_DB.csv', 'a', newline='', encoding="utf-8") as file:
            file.write("\n")
            file.write("%s,%s, %d,%d" % (commit, file_change,  dic_before, dic_after))

    @staticmethod
    def init_dic():
        # with open(str(pathlib.Path().absolute()) + '/../Feature/dic_meaning.txt', 'r') as f:
        with open(str(pathlib.Path().absolute()) + '/dic_meaning.txt', 'r') as f:
            for token in f:
                DIC[token.replace(" \n", "")] = 0


if __name__ == '__main__':
    measure_token = MeasureMeaning()
    measure_token.init_dic()
    # print(DIC)
    print(measure_token.get_feature('b9c19ecf28b2daf2dc1ff3bff72faaf5700e00ac',
                                    'core/camel-support/src/main/java/org/apache/camel/support/DefaultStartupStepRecorder.java' ))
