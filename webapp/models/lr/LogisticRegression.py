import pickle


class LogisticRegression:
    def __init__(self):
        self.model_filename = (
            "models/lr/LogisticRegressionClassifierTrainedOn24HRLabeling.model"
        )
        self.vectorizer_filename = "models/lr/BOWVectorizer.sav"
        self.model = pickle.load(open(self.model_filename, "rb"))
        self.vectorizer = pickle.load(open(self.vectorizer_filename, "rb"))

    def predict(self, text_or_text_arr):
        """
        string or array of strings => array of int (labels: -1, 0, 1)
        """
        if isinstance(text_or_text_arr, str):
            x = self.vectorizer.transform([text_or_text_arr])
            return self.model.predict(x)[0]
        X = self.vectorizer.transform(text_or_text_arr)
        return self.model.predict(X)
