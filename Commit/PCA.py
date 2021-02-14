import pathlib
import pandas as pd
from networkx.drawing.tests.test_pylab import plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np


class PCA_check:

    def __init__(self, path=str(pathlib.Path().absolute()) + '/File/feature.csv'):
        self.data_frame = pd.read_csv(path, delimiter="!")
        del self.data_frame['commit']
        del self.data_frame['file']
        self.y = self.data_frame['commit insert bug?']
        del self.data_frame['commit insert bug?']
        scaler = StandardScaler()
        scaler.fit(self.data_frame)
        X_scaled = scaler.transform(self.data_frame)
        # todo change n_components
        self.pca = PCA(n_components=95)
        self.pca.fit(X_scaled)
        self.x_pca = self.pca.transform(X_scaled)
        self.df_pca = pd.DataFrame(self.x_pca)
        self.df_pca['commit insert bug?'] = self.y
        self.df_pca.to_csv(str(pathlib.Path().absolute()) + '/File/PCA.csv')
        print(self.pca.explained_variance_ratio_)
        # self.visualization()

    def visualization(self):
        feature_1 = self.x_pca[:, 0]
        feature_2 = self.x_pca[:, 1]
        labels = self.y
        cdict = {0: 'red', 1: 'green'}
        labl = {0: 'without bug', 1: 'bug'}
        marker = {0: '*', 1: 'o'}
        alpha = {0: .3, 1: .5}
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor('white')
        for l in np.unique(labels):
            ix = np.where(labels == l)
            ax.scatter(feature_1[ix], feature_2[ix], c=cdict[l], s=100,
                       label=labl[l], marker=marker[l], alpha=alpha[l])
        # for loop ends
        plt.xlabel("First Principal Component", fontsize=14)
        plt.ylabel("Second Principal Component", fontsize=14)
        plt.legend()
        plt.savefig(str(pathlib.Path().absolute()) + "/File/PCA_visualization.png")

if __name__ == '__main__':
    obj = PCA_check()


