import pandas as pd
import datetime
import sys
from multiprocessing import cpu_count, Pool

df2018 = pd.read_hdf("result2018.h5", key="df")
df2019 = pd.read_hdf("result2019.h5", key="df")


ARTICLES_DF = pd.concat([df2018, df2019]).drop_duplicates().reset_index(drop=True)

### UTC to CST. UTC is ahead of 6 hours, which is 3600*6 seconds ###
ARTICLES_DF["article_datetime_CST"] = ARTICLES_DF.apply(
    lambda x: x["article_datetime"] - datetime.timedelta(0, 3600 * 6), axis=1
)
COMPANIES_LIST = ARTICLES_DF.company_code.unique()
CPU_NUM = range(cpu_count())


def my_func(company):
    def getPriceDiffPercentage(stockdf1, ticker, time, interval):
        """
        calculate stock price data of the time nearest to plus/minus of the given interval, from the publish time
        """
        endTime = time + datetime.timedelta(0, interval)
        startTime = time

        endStockPrice = stockdf1.iloc[
            (stockdf1["datetime"] - endTime).abs().argsort()[:2]
        ].iloc[0]["Close"]

        startStockPrice = stockdf1.iloc[
            (stockdf1["datetime"] - startTime).abs().argsort()[:2]
        ].iloc[0]["Close"]

        return (endStockPrice - startStockPrice) * 100 / startStockPrice

    TIME_INTERVAL = [180, 300, 900, 3600, 21600, 86400]

    stockdf = pd.read_csv("../data/stock/{}.csv".format(company), header=0)
    stockdf["datetime"] = stockdf.apply(
        lambda x: datetime.datetime.strptime(x["Date"], "%Y-%m-%d %H:%M:%S"), axis=1
    )
    company_df = ARTICLES_DF[
        (ARTICLES_DF.company_code == company)
        # & (
        #     ARTICLES_DF.article_datetime_CST
        #     > datetime.datetime(int(sys.argv[1]), 1, 18, 0, 0, 0)
        # )
    ]
    for interval in TIME_INTERVAL:
        company_df["priceAfter{}".format(interval)] = company_df.apply(
            lambda x: getPriceDiffPercentage(
                stockdf, x["company_code"], x["article_datetime_CST"], interval
            ),
            axis=1,
        )
    print(company_df.sort_values("priceAfter86400", ascending=True))
    return company_df


if __name__ == "__main__":
    # haha = pd.read_hdf("priceDf.h5", key="priceDf")
    # print(haha.columns.values)

    pool = Pool()
    results = pool.map(my_func, COMPANIES_LIST)
    pool.close()
    pool.join()

    results = pd.concat(results)
    results.to_hdf("priceDf.h5", key="priceDf")
