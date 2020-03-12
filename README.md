# Stock Price Prediction using Sentence Classification

## Problem Statement

Supply and demand in the market determine stock price. Many high frequency trading firm and investment firm deploys sentiment analysis algorithms for news to aid their trading. Company event news and earnings news affect investors' valuation of a company, but other factors contribute to supply and demand, such as their sentiments, attitudes, and expectations.

In our project, we aimed to develop a model that tells you if you should buy, hold, or sell a stock, given a news article.

### Input & Output

Input: A title of a news article in English. ("Amazon’s 2Q profits miss Wall Street expectations - The Washington Post")

Output: Classification result, one of "buy", "sell", or "hold".

## Core Model

## Deliverables

- News articles data (2018-2019)
- [Google's Pretrained Word2Vec Model](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit)
- [Code running on Northwestern machine](linktowherejavacodeis)
- [Code running on AWS Elastic Beanstalk](linktoFlaskApp)
- Dockerfile
- Docker Image

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

Make sure you have Java SE v.11.0.4 installed

```
cd crawler/target/
export aws_access_key_id=<your aws access key id>
export aws_secret_access_key=<your aws secret access key>
java -jar news-import-1.0-SNAPSHOT-jar-with-dependencies.jar <year> <month>
```

Such as: java -jar news-import-1.0-SNAPSHOT-jar-with-dependencies.jar 2019 12

```
cd ..
python buildDataframe.py <year>
python mergeStockPrice.py <year>
python labelStockPrice.py
```

### Preprocessing and Model Training

```
cd ../model
python preprocess.py --max_features <MAX_FEATURES>
python svm.py --max_features <MAX_FEATURES>
python cnn.py
```

### Docker Containerization and Deploy

create new directory that contains just the pickled model files and the flask app

```


```

## References

### 우리 읽었던 페이퍼 붙이고 참고했다고 하고
