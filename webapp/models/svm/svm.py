import pickle


class SVM:
    def __init__(self):
        self.tfidf = pickle.load(
            open("models/svm/tfidfVectorizer_features=1500.pkl", "rb")
        )
        self.svm = pickle.load(
            open("models/svm/stockprice_svm_features=1500.model", "rb")
        )

    def predict(self, text):
        x = self.tfidf.transform([text])
        result = self.svm.predict(x)
        return int(result[0])
