import json
from datetime import datetime
import pandas as pd
import numpy as np
import sys

with open("companies.json") as file2:
    COMPANIES = json.load(file2)


def findCompany(title):
    found = []

    for key, value in COMPANIES.items():
        if title.find(key) != -1:
            found.append((key, value["ticker"], value["market"]))
    # [(companyName, companyTicker, companyMarket)]
    return found


def rightTime(year, articleTime):
    minTime = datetime(year, 1, 1, 0, 0, 0)
    maxTime = datetime(year, 12, 31, 23, 59, 59)
    return minTime < articleTime < maxTime

def findSource(articleUrl):
    temp = articleUrl.split(".com")[0]
    if len(temp.split(".")) == 2:
        return temp.split(".")[-1]
    else:
        return temp.split("/")[-1]


def makeRowsFromArticle(articleJson, year, titles, duplicates):
    articleTitle = articleJson["title"]
    if articleTitle in titles:
        duplicates[0] += 1
        return []
    titles.append(articleTitle)
    articleBody = articleJson["text"]
    articleDatetime = datetime.strptime(
        articleJson["datePublished"], "%Y-%m-%dT%H:%M:%S"
    )
    if not rightTime(year, articleDatetime):
        return []
    articleUrl = articleJson["url"]
    articleSource = findSource(articleUrl)
    companiesFound = findCompany(articleTitle)

    return [
        [
            articleTitle,
            articleBody,
            articleDatetime,
            articleUrl,
            articleSource,
            i[0],
            i[1],
            i[2],
        ]
        for i in companiesFound
    ]


def main():
    titles = []
    results = np.zeros((1, 8))
    duplicates = [0]

    for year in ['2018', '2019']
    for i in range(1, 13):
        try:
            with open("data/{}/result{}{}.json".format(year, year, i if i > 9 else "0" + str(i))) as file1:
                data = json.load(file1)
            print("For the month of {}, {} articles found. ".format(i, len(data)))
        except FileNotFoundError:
            continue

        for j in data:
            rows = makeRowsFromArticle(j, year, titles, duplicates)
            for row in rows:
                results = np.append(results, [np.array(row)], axis=0)

    print("This many duplicates: {}".format(duplicates[0]))
    results = np.delete(results, 0, 0)
    columns = [
        "article_title",
        "article_body",
        "article_datetime",
        "article_url",
        "article_source",
        "company_name",
        "company_code",
        "company_market",
    ]

    # and put into a dataframe
    df = pd.DataFrame(results, index=range(len(results)), columns=columns)
    df.to_hdf("result.h5", key="df")
    # print
    for company in COMPANIES.keys():
        company_count = df[df.company_name == company].shape[0]
        print("{} entries for company {}.".format(company_count, company))
    print(len(titles))
    # to load:
    # df = pd.read_hdf("result.h5", key="df")


if __name__ == "__main__":
    # df = pd.read_hdf("result.h5", key="df")
    # for i in df["article_datetime"]:
    #     print(i)
    main()