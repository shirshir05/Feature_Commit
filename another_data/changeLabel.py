import csv
import pathlib

import pandas as pd
import numpy as np


class changeLabel:

    def __init__(self):

        # save if commit insert bug fro change label
        self.dic_commit_blame = {}
        # save commit fix, commit and file to equal if our data
        self.dic_commit_blame_issue = {}
        self.other_data = pd.read_csv(str(pathlib.Path().absolute()) + '/jit_sn_commons-math.csv', delimiter=',')
        self.our_data = pd.read_csv(str(pathlib.Path().absolute()) + '/../Commit/File/feature.csv', delimiter='!')
        self.our_commit_blame = pd.read_csv(str(pathlib.Path().absolute()) + '/../Commit/File/commit_blame.csv',
                                            delimiter=',')

    def read_commit_blame(self):
        """
            Save self.dic_commit_blame
        """
        for (column_name, columnData) in self.other_data.iteritems():
            if column_name.find("adhoc") != -1 or column_name.find("MATH") != -1:
                df = self.other_data[self.other_data[column_name] == 1]
                index_start = column_name.find("__")
                index_end = column_name.rfind("__")
                issue = column_name[0:index_start]
                commit_fix = column_name[index_start + 2:index_end]
                for row in df.iterrows():
                    file = row[1]["file"]
                    if file.endswith(".java") and not file.endswith("Test.java"):
                        self.dic_commit_blame[(row[1]["commit"], file)] = (issue, commit_fix)
                        self.dic_commit_blame_issue[(row[1]["commit"], file, commit_fix)] = issue

    def write_fix_and_blame(self):
        with open(str(pathlib.Path().absolute()) + '/commit_blame_data_exist.csv', 'w', newline='',
                  encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(['issue', 'commit fix', 'commit blame', 'file', 'match'])
            for key in self.dic_commit_blame_issue.keys():
                commit_blame = key[0]
                file = key[1]
                commit_fix = key[2]
                if ((self.our_commit_blame['blame commit'] == commit_blame) &
                    (self.our_commit_blame['commit fix'] == str(commit_fix)) &
                    (self.our_commit_blame['file'] == str(file))).any():
                    writer.writerow([self.dic_commit_blame_issue[key], commit_fix, commit_blame, file, 1])
                else:
                    writer.writerow([self.dic_commit_blame_issue[key], commit_fix, commit_blame, file, 0])

    def change_label(self):
        """"
            change label ("commit insert bug?) according data exist
        """
        self.our_data['commit insert bug?'] = self.our_data['commit insert bug?'].fillna(0)
        for ind in self.our_data.index:
            if (self.our_data['commit'][ind], self.our_data['file'][ind]) in self.dic_commit_blame:
                self.our_data['commit insert bug?'][ind] = 1
        self.our_data.to_csv(str(pathlib.Path().absolute()) + '/../Commit/File/feature_change_label.csv', index=False)

    def change_feature(self):
        """"
            change label ("commit insert bug?) according data exist
        """
        index_col = self.our_data.columns.values[2:]
        for i in index_col:
            self.other_data[i] = np.full(self.other_data['commit'].shape[0], -1)
        for ind in self.our_data.index:
            commit_search = self.our_data['commit'][ind]
            file_search = self.our_data['file'][ind]
            if ((commit_search == self.other_data['commit']) & (
                    file_search == self.other_data['file'])).any():
                index_commit = np.where((self.other_data['commit'] == commit_search).values == True)
                index_file = np.where((self.other_data['file'] == file_search).values == True)
                index_other_data = np.intersect1d(index_commit, index_file)
                for i in index_col:
                    self.other_data.at[(index_other_data, i)] = (self.our_data.loc[ind][i])
        self.other_data.to_csv(str(pathlib.Path().absolute()) + '/../Commit/File/change_feature.csv', index=False)


if __name__ == '__main__':
    obj = changeLabel()
    obj.change_feature()
    # obj.read_commit_blame()
    # obj.write_fix_and_blame()
    # obj.change_label()
