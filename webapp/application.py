import os
from flask import Flask, request, render_template
from models.cnn.cnn import CNN
from models.svm.svm import SVM
from models.lr.LogisticRegression import LogisticRegression

application = Flask(__name__)
cnn = CNN()
svm = SVM()
lr = LogisticRegression()
defaultModel = "svm"
defaultTitle = ""


@application.route("/")
def my_form():
    return render_template("index.html", model=defaultModel)


@application.route("/", methods=["POST"])
def my_form_post():
    title = request.form["title"]
    classifier = request.form["type"]
    defaultTitle = title

    if classifier == "cnn":
        result = cnn.predict(title)
    elif classifier == "svm":
        result = svm.predict(title)
    elif classifier == "lr":
        result = lr.predict(title)

    # sell, buy, hold = -1, 1, 0
    action = ["hold for", "buy", "sell"]
    return render_template(
        "index.html", title=title, action=action[result], model=classifier
    )


if __name__ == "__main__":
    application.run(debug=True,host='0.0.0.0')
