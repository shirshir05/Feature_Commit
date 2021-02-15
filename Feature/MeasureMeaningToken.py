import copy
import json
import pathlib
import sqlite3
import pandas as pd

DIC_TOKEN = {}
DIC_Meaning = {}


class MeasureMeaningToken:

    def __init__(self):
        """"
                  Init the connection of DB
              """
        DB_PATH = r"C:\Users\shir0\Commits-Issues-DB\CommitIssueDB.db"
        # Get DB connection
        self.db_connection = sqlite3.connect(DB_PATH)
        print("connection established to DB")
        self.init_dic()

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
        dic_before_token, dic_before_meaning = self.find_meaning_token(commit, file_change, "OLD")
        dic_after_token, dic_after_meaning = self.find_meaning_token(commit, file_change, "NEW")
        if dic_before_token is None and dic_before_meaning is None and dic_after_token is None and dic_after_meaning is None :
            return None
        if dic_before_token is None:
            dic_before_token = copy.copy(DIC_TOKEN)
        if dic_before_meaning is None:
            dic_before_meaning = copy.copy(DIC_Meaning)
        if dic_after_token is None:
            dic_after_token = copy.copy(DIC_TOKEN)
        if dic_after_meaning is None:
            dic_after_meaning = copy.copy(DIC_Meaning)

        return self.sub_dic(dic_before_token, dic_after_token), self.sub_dic(dic_before_meaning, dic_after_meaning)

    def find_meaning_token(self, commit, file_change, new_or_old):
        """"
            help function that return dictionary of measure
            parameter:
                commit(commit)
                file change - file that change
            return:
                return dictionary of measure
        """
        try:
            query_method_data = f"SELECT Meaning, Tokens  FROM MethodData WHERE NewPath ='{str(file_change)}' AND CommitID = '{str(commit)}'  AND OldNew == '{new_or_old}'"
            sql_query = pd.read_sql_query(query_method_data, self.db_connection)
            if sql_query.empty:
                return None, None
            df = pd.DataFrame(sql_query, columns=['Meaning', 'Tokens'])
            dic_token = copy.copy(DIC_TOKEN)
            dic_meaning = copy.copy(DIC_Meaning)

            for index, line in df.iterrows():
                if line[0] == [None] or line[0] is None: line[0] = '{{}}'
                if line[1] == [None] or line[1] is None: line[1] = '{{}}'
                # remove{'BlockStatement': 1, 'LocalVariableDeclaration': 1}
                # json_line_meaning = json.loads(str(line[0]).replace("\\\'", '"').replace('\\\\"', '')[3:-3])
                json_line_meaning = json.loads(str(line[0]).replace("\'", '"')[1:-1])

                for key in json_line_meaning.keys():
                    if key in dic_meaning.keys():
                        dic_meaning[key] += json_line_meaning[key]
                json_line_token = json.loads(str(line[1]).replace("\'", '"')[1:-1])
                # json_line_token = json.loads(str(line[1]).replace("\\\'", '"').replace('\\\\"', '')[3:-3])
                for key in json_line_token.keys():
                    if key in dic_token.keys():
                        dic_token[key] += json_line_token[key]
            return dic_token, dic_meaning
        except Exception as e:
            print(e)
            pass
            return None, None

    def sub_dic(self, before, after):
        list_ans = self.dic_to_list(before)
        list_ans += self.dic_to_list(after)
        feature_delta = {x: after[x] - before[x] for x in before if x in after}
        list_ans += self.dic_to_list(feature_delta)
        return list_ans

    @staticmethod
    def dic_to_list(feature):
        list_ans = []
        for i in feature.keys():
            list_ans.append(feature[i])
        return list_ans

    def close_connection(self):
        self.db_connection.close()

    @staticmethod
    def init_dic():
        with open(str(pathlib.Path().absolute()) + '/../Feature/dic_meaning.txt', 'r') as f:
            # with open(str(pathlib.Path().absolute()) + '/dic_meaning.txt', 'r') as f:
            for token in f:
                DIC_Meaning[token.replace(" \n", "")] = 0
        with open(str(pathlib.Path().absolute()) + '/../Feature/dic_tokens', 'r') as f:
            for token in f:
                DIC_TOKEN[token.replace("\n", "")] = 0
