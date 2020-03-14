import pandas as pd
import sys


def label(percent):
    if percent > 1.0:
        return 1
    elif percent < -1.0:
        return -1
    else:
        return 0


def label_then_save(df, interval):
    """
    input: 
        df : dataframe with articles and stock price changes in percentile, for each time interval
        interval : time interval in seconds
    output:
        None
        saves labeled data in csv in 'data/labeled' folder, with filename corresponding to the interval
    """
    temp_df = df[["article_title", "priceAfter{}".format(interval)]]
    temp_df["label"] = temp_df.apply(
        lambda x: label(x["priceAfter{}".format(interval)]), axis=1
    )
    file_name = "../data/labeled/{}.csv".format(interval)
    temp_df[["article_title", "label"]].to_csv(
        file_name, sep=",", encoding="utf-8", index=False
    )


if __name__ == "__main__":
    TIME_INTERVAL = [180, 300, 900, 3600, 21600, 86400]
    PRICE_DF = pd.read_hdf("priceDf.h5", key="priceDf")

    for interval in TIME_INTERVAL:
        label_then_save(PRICE_DF, interval)
