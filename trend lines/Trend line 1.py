from scipy.signal import savgol_filter
from pandas_datareader import data
import matplotlib.pyplot as plt
import statistics as stats
import pandas as pd
import numpy as np


# def load_stock_data(stock, start_date, end_date="2025-12-12"):
#     df = data.DataReader(stock, 'yahoo', start_date, end_date)
#     return df


def load_stock_data(stock, start_date, end_date="2025-12-12", output_file=r"test.pkl"):
    try:
        df = pd.read_pickle(output_file)
        print('File data found...reading GOOG data')
    except FileNotFoundError:
        print('File not found...downloading the GOOG data')
        df = data.DataReader(stock, 'yahoo', start_date, end_date)
        df.to_pickle(output_file)
    return df


def smooth(df):
    ...


def calc_min_max_points(df, window_size):
    df['res'] = pd.Series(np.zeros(len(df)))
    for i in range(window_size - 1 + window_size, len(df), window_size + 1):
        print(i)
        data_selection = df[i - window_size:i + 1]
        # print(data_selection["Adj Close"])
        # print(max(data_selection["Adj Close"]))
        res = max(data_selection["Adj Close"])
        print(res)
        for x in range(i, i+10):
            df["res"][i] = res
        # print(df)
        # print(data_selection)
        # print(i)
    print(df)

def main():
    df = load_stock_data("TSLA", "2022-01-01")
    calc_min_max_points(df, 10)


if __name__ == '__main__':
    main()
