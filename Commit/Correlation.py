import csv
import pathlib
from statistics import mean

import pandas as pd
from numpy import std, cov
from scipy.stats import pearsonr, spearmanr
import seaborn as sns
import matplotlib.pyplot as plt

class Correlation:

    def __init__(self, path):
        with open('File/correlation.csv', 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(['col', 'covariance[col][col]', 'covariance[col][commit insert bug?]',
                            'covariance[commit insert bug?][col]', 'covariance[commit insert bug?][commit insert bug?]',  'pearsonr', 'spearmanr', 'mean', 'std'])
            data_frame = pd.read_csv(path)
            for col in data_frame:
                if col == 'commit' or col == 'file':
                    continue
                covariance = cov(data_frame[col], data_frame['commit insert bug?'])
                pearson, _ = pearsonr(data_frame[col], data_frame['commit insert bug?'])
                spearman, _ = spearmanr(data_frame[col], data_frame['commit insert bug?'])
                writer.writerow([col, covariance[0][0], covariance[0][1], covariance[1][0], covariance[1][1],
                                 pearson, spearman, mean(data_frame[col]), std(data_frame[col])])
                file.flush()

    @staticmethod
    def T_test():
        df_bug = pd.read_csv(str(pathlib.Path().absolute()) + '/File/bug_commit.csv')
        df_not_bug = pd.read_csv(str(pathlib.Path().absolute()) + '/File/not_bug_commit.csv')
        for col in df_bug:
            if col == 'commit' or col == 'file':
                continue
            sns.kdeplot(df_bug[col], shade=True, color ='red')
            sns.kdeplot(df_not_bug[col], shade=True)
            plt.title("T-Test")
            plt.show()


if __name__ == "__main__":
    # cor = Correlation(str(pathlib.Path().absolute()) + '/File/feature.csv')
    Correlation.T_test()