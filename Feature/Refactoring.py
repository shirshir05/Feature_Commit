import json
import pathlib

from bokeh.core.json_encoder import pd
from numpy import loadtxt


class Refactoring:

    def __init__(self):
        self.dic = {}
        self.data_json = {}
        index = 0
        while index < 41:
            with open(str(pathlib.Path().absolute()) + "/../Commit/File/Refactoring/camel/out(" + str(index) + ").json") as json_file:
            # with open(str(pathlib.Path().absolute()) + "/File/Refactoring/camel/out(" + str(index) + ").json") as json_file:

                self.data_json.update(json.load(json_file))
                index += 1
        self.dict_ans = self.init_type()

    def find_type(self):
        # dic = ("commit", "file_a", "file_b") : [type, leftSideLocations, rightSideLocations]
        with open(str(pathlib.Path().absolute()) + '/File/Refactoring/refactoring.json') as json_file:
            data_json = json.load(json_file)
            for commit in data_json.keys():
                if commit["refactorings"]:
                    for type_refactorings in commit["refactorings"]:
                        file = type_refactorings["rightSideLocations"][0]["filePath"]
                        if file.endswith(".java") and not file.endswith("Test.java"):
                            new_tuple = (commit["sha1"], type_refactorings["leftSideLocations"][0]["filePath"],
                                         type_refactorings["rightSideLocations"][0]["filePath"])
                            self.dic[new_tuple] = [type_refactorings["type"], type_refactorings["leftSideLocations"],
                                                   type_refactorings["rightSideLocations"]]

    def sum_type(self):
        dict_type = {}
        for value in self.dic.values():
            value_in_dic = dict_type.get(value[0], 0)
            dict_type[value[0]] = value_in_dic + 1
        with open(str(pathlib.Path().absolute()) + '/File/Refactoring/refactoring_type.csv', 'w') as f:
            f.write("type,count\n")
            for key in dict_type.keys():
                f.write("%s,%s\n" % (key, dict_type[key]))

    def feature_refactoring(self, commit_check, file_check):
        for commit in self.data_json.keys():
            for list_commit in self.data_json[commit]:
                if list_commit["refactorings"]:
                    if list_commit["sha1"] == str(commit_check):
                        for type in list_commit["refactorings"]:
                            for file in type['leftSideLocations']:
                                if file['filePath'] == file_check:
                                    if type['refactor_type'] in self.dict_ans.keys():
                                        self.dict_ans[type['refactor_type']] += 1
                                    else:
                                        print(type['refactor_type'])
                            for file in type['rightSideLocations']:
                                if file['filePath'] == file_check:
                                    if type['refactor_type'] in self.dict_ans.keys():
                                        self.dict_ans[type['refactor_type']] += 1
                                    else:
                                        print(type['refactor_type'])
        return list(self.dict_ans.values())

    @staticmethod
    def init_type():
        # list_type = pd.read_csv(str(pathlib.Path().absolute()) + '/File/Refactoring/refactoring_type.csv')
        list_type = pd.read_csv(str(pathlib.Path().absolute()) + "/../Commit/File/Refactoring/refactoring_type.csv")
        list_type = list_type['type']
        dict_type = list_type.to_dict()
        dict = dict_type.fromkeys(list_type, 0)
        return dict


if __name__ == '__main__':
    r = Refactoring()
    r.feature_refactoring("f5e6bbbaaf878f11050bcdfa9639a5a7fc0551e1", "camel-core/src/main/java/org/apache/camel/api/management/mbean/ManagedBacklogDebuggerMBean.java")
