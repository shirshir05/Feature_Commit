import copy
import json
import pathlib
import sqlite3
import pandas as pd

DIC = {}


class MeasureTokens:

    def __init__(self):
        """"
            Init the connection of DB
        """
        DB_PATH = r"C:\Users\shir0\Commits-Issues-DB\CommitIssueDB.db"
        # Get DB connection
        self.db_connection = sqlite3.connect(DB_PATH)
        print("connection established to token")
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
        dic_before = self.find_tokens(commit, file_change, "OLD")
        dic_after = self.find_tokens(commit, file_change, "NEW")
        if dic_before is None and dic_after is None:
            return None
        if dic_before is None:
            dic_before = copy.copy(DIC)
        elif dic_after is None:
            dic_after = copy.copy(DIC)
        feature = {x: dic_after[x] - dic_before[x] for x in dic_before if x in dic_after}
        list_ans = []
        for i in feature.keys():
            list_ans.append(feature[i])
        return list_ans

    def find_tokens(self, commit, file_change, new_or_old):
        """"
            help function that return dictionary of measure
            parameter:
                commit(commit)
                file change - file that change
            return:
                return dictionary of measure
        """
        try:
            query_method_data = "SELECT * FROM MethodData WHERE NewPath =='" + str(
                file_change) + "'AND CommitID = '" + \
                                str(commit) + "' AND "  "OldNew == '" + new_or_old + "' AND Changed=1"

            sql_query = pd.read_sql_query(query_method_data, self.db_connection)
            if sql_query.empty:
                return None
            df = pd.DataFrame(sql_query, columns=['Tokens'])
            dic = copy.copy(DIC)
            for index, line in df.iterrows():
                if line.values == "" : continue
                line = str(line.values)
                line = line[2:-2]
                dict_json = json.loads(line)
                for key in dict_json:
                    if key in dic:
                        dic[key] += dict_json[key]
            return dic
        except Exception as e:
            print(e)
            pass
            return None

    @staticmethod
    def init_dic():
        with open(str(pathlib.Path().absolute()) + '/../Feature/dic_tokens', 'r') as f:
            for token in f:
                DIC[token.replace("\n", "")] = 0

    def close_connection(self):
        self.db_connection.close()

if __name__ == '__main__':
    test = MeasureTokens()
    test.init_dic()
    print(test.get_feature('cf4138d7bc1a892295ccd58ea8b42f7c8737239a','src/main/java/org/apache/commons/lang3/time/DurationFormatUtils.java'))
    print(DIC)