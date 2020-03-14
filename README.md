# Stock Price Prediction using Sentence Classification

by Joo Seung Lee, Wungjae Lee, Thomas Chen

## Problem Statement

Supply and demand in the market determine stock price. Many high frequency trading firm and investment firm deploys sentiment analysis algorithms for news to aid their trading. Company event news and earnings news affect investors' valuation of a company, but other factors contribute to supply and demand, such as their sentiments, attitudes, and expectations.

In our project, we aimed to develop a model that tells you if you should buy, hold, or sell a stock, given a news article.

### Input & Output

Input: A title of a news article in English. ("Amazon’s 2Q profits miss Wall Street expectations - The Washington Post")

Output: Classification result, one of "buy", "sell", or "hold".

## Core Model

We built a variety of different models ranging from classical machine learning models such as support vector machine(SVM), logistic regression to some deep learning methods mentioned in literature such as convolutional neural network(CNN) and convolutional neural network + long short term memory model (C-LSTM) for text classification purposes.
As to examine the results of our models, for the three class classification case, we examine
confusion matrix and backtest of our strategy based on the models’ outputs. For confusion matrix, we mainly look at the precision for predicting +1 and -1, and we only care the samples that are either actual +1 or -1 because with actual label of 0, means that the return will be between -0.25% to +0.25% and with larger number their mean converge to 0% return which is trivial. As for backtest, we naively simulate a strategy that buys when prediction is +1, do nothing when prediction is 0, and sell when prediction is -1, with a holding time equal to our prediction time lag (15min, 60min, 1day etc..) and we attach a backtest result here.

## Deliverables

- [Link to web interface](http://stockprice.us-east-2.elasticbeanstalk.com/)
- [News articles data (2018-2019)](https://drive.google.com/drive/folders/1Ld2C_N9ZJjwqVfdf9I8KjNENT52m7ff_?usp=sharing)
- [Stock price data (2018-2019)](https://drive.google.com/drive/folders/1Qv4c7VqtB9EDhakoLCJOCuFSj_Mzf2C4?usp=sharing)
- [Google's Pretrained Word2Vec Model](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit)
- [Code running on Northwestern machine](https://github.com/jooseung2/stockpriceprediction/blob/master/commoncrawl/src/main/java/jooseung/lee/App.java)
- [Code running on AWS Elastic Beanstalk](https://github.com/jooseung2/stockpriceprediction/tree/master/webapp)
- [Dockerfile](https://github.com/jooseung2/stockpriceprediction/tree/master/webapp/Dockerfile)
- [Docker Image on Docker Hub](https://hub.docker.com/repository/docker/jlee6741/stockprice)
- [Docker Image (in .tar) on Google Drive](https://drive.google.com/file/d/1N2mE7gJfQkTpufFArW639hxWxR97h4uI/view?usp=sharing)

## Run Model

1. Clone this repo

```
git clone https://github.com/wungjaelee/stock-sentiment-analysis.git
cd stock-sentiment-analysis
```

2. Create a virtual environment

```
conda create -n stock python=3.6
conda activate stock
/user/anaconda3/bin/pip install -r requirements.txt
```

### Data Collection and Cleaning

1. Download news articles from Common Crawl and Parse
   You need to have Java SE v.11.0.4 installed to run the script that downloads from Common Crawl and parses HTML documents.

```
cd crawler/target/
export aws_access_key_id=<your aws access key id>
export aws_secret_access_key=<your aws secret access key>
java -jar news-import-1.0-SNAPSHOT-jar-with-dependencies.jar <year> <month>
```

Such as: java -jar news-import-1.0-SNAPSHOT-jar-with-dependencies.jar 2019 12
These data are accessible in [here](https://drive.google.com/drive/folders/1Ld2C_N9ZJjwqVfdf9I8KjNENT52m7ff_?usp=sharing).

2. Put news article data into dataframe and merge stock price data
   Stock price data are accessible in [here](https://drive.google.com/drive/folders/1Qv4c7VqtB9EDhakoLCJOCuFSj_Mzf2C4?usp=sharing)

```
cd ..
python buildDataframe.py <year>
python mergeStockPrice.py <year>
python labelStockPrice.py
```

3. Label as described in the core model section.

### Preprocessing and Model Training

1. Training script

```
cd ../model
python preprocess.py --max_features <MAX_FEATURES>
python svm.py --max_features <MAX_FEATURES>
python cnn.py
```

2. CNN Hyperparameters

| Argument         | Type                          | Description                                                                                                    |
| ---------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------- |
| embedding_dim    | 300                           | dimension of the dense embedding                                                                               |
| n_layers         | 2                             | number of layers                                                                                               |
| hidden_units     | 500                           | dimensionality of the output space                                                                             |
| batch_size       | 100                           | number of samples per gradient update                                                                          |
| patience         | 2                             | number of epochs that produced the monitored quantity with no improvement after which training will be stopped |
| dropout_rate     | 0.3                           | fraction of the input units to drop                                                                            |
| n_filters        | 100                           | the dimensionality of the output space                                                                         |
| window_size      | 8                             | the length of the 1D convolution window                                                                        |
| dense_activation | relu                          | activation function to use                                                                                     |
| regularizer      | l2_penalty with factor 0.0003 |                                                                                                                |
| epochs           | 10                            | Number of epochs to train the model                                                                            |
| validation_split | 0.1                           | fraction of the training data to be used as validation data                                                    |

### Docker Containerization and Deploy on AWS

We followed the guide on [here](https://linuxacademy.com/blog/linux-academy/deploying-a-containerized-flask-application-with-aws-ecs-and-docker/) to deploy our model to AWS ECR.

1. create new directory (webapp/models) that contains just the pickled model files and the flask app

2. Run docker / aws commands to create image and push to ECR

```
docker build -t webapp .

aws ecr create-repository --repository-name stockprice --region us-east-2
docker tag 275d923a596f 179460613492.dkr.ecr.us-east-2.amazonaws.com/stockprice
aws ecr get-login-password | docker login --username AWS --password-stdin 179460613492.dkr.ecr.us-east-2.amazonaws.com
docker push 179460613492.dkr.ecr.us-east-2.amazonaws.com/stockprice
```

3. Deploy on ECS

- Running Locally

```
docker pull jlee6741/stockprice:secondtry
docker run -d -p 5000:5000 jlee6741/stockprice:secondtry
```

Go to 0.0.0.0:5000 to try.

```
docker ps -a      # find pid of docker image being run
docker kill <pid> # kill process when you are done
```

## References

[Convolutional Neural Networks for Sentence Classification](https://arxiv.org/pdf/1408.5882.pdf)

[Deep Learning for Event-Driven Stock Prediction](https://www.aaai.org/ocs/index.php/IJCAI/IJCAI15/paper/viewFile/11031/10986)

[On the Importance of Text Analysis for Stock Price Prediction](https://nlp.stanford.edu/pubs/lrec2014-stock.pdf)

[Using NLP on news headlines to predict index trends](https://arxiv.org/pdf/1806.09533.pdf)
