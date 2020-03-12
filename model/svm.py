from sklearn.svm import LinearSVC
import pandas as pd
import pickle
import argparse
from scipy import sparse


def train(max_features):
    df = pd.read_csv("../data/shuffled_86400.csv")

    label = df[["label"]].values.ravel()
    recordCount = df.shape[0]
    fourFifths = 4 * (recordCount // 5)
    oneFifth = recordCount // 5
    features = sparse.load_npz(
        "features_ngram=1,2_features={}.npz".format(max_features)
    ).toarray()

    svm = LinearSVC(random_state=0).fit(features[:fourFifths, :], label[:fourFifths])
    pickle.dump(
        svm, open("stockprice_svm_features={}.model".format(max_features), "wb")
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_features",
        type=int,
        help="will preprocess for vocabulary that only consider the top <max_features> ordered by term frequency across the corpus",
    )

    dargs = parser.parse_args()
    assert isinstance(dargs.max_features, int) and dargs.max_features > 0

    MAX_FEATURES = dargs.max_features
    train(MAX_FEATURES)
