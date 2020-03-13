# Stock Price Prediction using Sentence Classification

## Problem Statement

Supply and demand in the market determine stock price. Many high frequency trading firm and investment firm deploys sentiment analysis algorithms for news to aid their trading. Company event news and earnings news affect investors' valuation of a company, but other factors contribute to supply and demand, such as their sentiments, attitudes, and expectations.

In our project, we aimed to develop a model that tells you if you should buy, hold, or sell a stock, given a news article.

### Input & Output

Input: A title of a news article in English. ("Amazon’s 2Q profits miss Wall Street expectations - The Washington Post")

Output: Classification result, one of "buy", "sell", or "hold".

## Core Model

## Deliverables

- [News articles data (2018-2019)](https://github.com/jooseung2/stockpriceprediction/tree/master/data)
- [Google's Pretrained Word2Vec Model](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit)
- [Code running on Northwestern machine](linktowherejavacodeis)
- [Code running on AWS Elastic Beanstalk](linktoFlaskApp)
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

2. Put news article data into dataframe and merge stock price data

```
cd ..
python buildDataframe.py <year>
python mergeStockPrice.py <year>
python labelStockPrice.py
```

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

1. create new directory that contains just the pickled model files and the flask app

```

```

2. Run docker / aws commands to create image and push to ECR

```
docker build -t webapp .
docker run -d -p 5000:5000 <image id>

aws ecr create-repository --repository-name stockprice --region us-east-2
docker tag 275d923a596f 179460613492.dkr.ecr.us-east-2.amazonaws.com/stockprice
aws ecr get-login-password | docker login --username AWS --password-stdin 179460613492.dkr.ecr.us-east-2.amazonaws.com
docker push 179460613492.dkr.ecr.us-east-2.amazonaws.com/stockprice
```

3. Deploy on ECS

## References
