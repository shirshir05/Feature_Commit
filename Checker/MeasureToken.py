import sqlite3
import pandas as pd


class MeasureToken:

    def __init__(self):
        """"
            Init the connection of DB
        """
        DB_PATH = r"C:\Users\shir0\Commits-Issues-DB\CommitIssueDB.db"
        # Get DB connection
        self.db_connection = sqlite3.connect(DB_PATH)
        print("connection established")

    def get_feature(self, parent, commit, file_change):
        """"
            Main function that return list of feature
            parameter:
                parent(commit)
                commit(commit)
                file change - file that change
            return:
                return list of feature
        """
        dic_before = self.find_meaning(parent, file_change)
        dic_after = self.find_meaning(commit, file_change)
        feature = {x: dic_before[x] - dic_after[x] for x in dic_before if x in dic_after}
        list_ans = [feature['Member'], feature['FieldDeclaration'], feature['VariableDeclaration'],
                    feature['LocalVariableDeclaration'], feature['VariableDeclarator'], feature['Literal'],
                    feature['This'], feature['MemberReference']]
        return list_ans

    def find_meaning(self, commit, file_change):
        """"
            help function that return dictionary of measure
            parameter:
                commit(commit)
                file change - file that change
            return:
                return dictionary of measure
        """
        query_method_data = "SELECT Meaning FROM MethodData WHERE CommitID=" + commit + "AND NewPath=" + file_change
        sql_query = pd.read_sql_query(query_method_data, self.db_connection)
        df = pd.DataFrame(sql_query, columns=['Meaning'])
        list_meaning = df['Meaning'].tolist()
        dic = {"'Member'": 0, "'FieldDeclaration'": 0, "'VariableDeclaration'": 0, "'LocalVariableDeclaration'": 0,
               "'VariableDeclarator'": 0, "'Literal'": 0, "'This'": 0, "'MemberReference'": 0}
        for line in list_meaning:
            # remove{'BlockStatement': 1, 'LocalVariableDeclaration': 1}
            line = line[1:len(line) - 1]
            split_line = line.split(", ")
            for meaning in split_line:
                if meaning.find(meaning):
                    get_number = meaning.split(" ")
                    dic[get_number[0]] += int(get_number[1])
        return dic
