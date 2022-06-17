from sklearn.model_selection import train_test_split
from pandas_datareader import data
import pandas as pd
import numpy as np


def load_financial_data(start_date, end_date, output_file):
    try:
        df = pd.read_pickle(output_file)
        print('File data found...reading GOOG data')
    except FileNotFoundError:
        print('File not found...downloading the GOOG data')
        df = data.DataReader('GOOG', 'yahoo', start_date, end_date)
        df.to_pickle(output_file)
    return df


def create_classification_trading_condition(df):
    df['Open-Close'] = df.Open - df.Close
    df['High-Low'] = df.High - df.Low
    df = df.dropna()
    x = df[['Open-Close', 'High-Low']]
    y = np.where(df['Close'].shift(-1) > df['Close'], 1, -1)
    return x, y


def create_regression_trading_condition(df):
    df['Open-Close'] = df.Open - df.Close
    df['High-Low'] = df.High - df.Low
    df = df.dropna()
    x = df[['Open-Close', 'High-Low']]
    y = df['Close'].shift(-1) - df['Close']
    return x, y


def main():
    goog_data = load_financial_data(start_date='2001-01-01', end_date='2022-01-01', output_file='goog_data_large.pkl')
    # x, y = create_classification_trading_condition(goog_data)
    x, y = create_regression_trading_condition(goog_data)
    pd.plotting.scatter_matrix(goog_data[['Open-Close', 'High-Low', 'Target']], grid=True, diagonal='kde')

    x_train, x_test, y_train, y_test = train_test_split(x, y, shuffle=False, train_size=0.9)
    print(len(y_train))
    print(len(x_train))
    print(len(y_test))
    print(len(x_test))


if __name__ == '__main__':
    main()
