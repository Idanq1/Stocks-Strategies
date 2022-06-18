from pandas_datareader import data
import matplotlib.pyplot as plt
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


def double_moving_average(stock_data, short_window, long_window):
    signals = pd.DataFrame(index=stock_data.index)
    signals["signal"] = 0.0
    signals["short_mavg"] = stock_data["Close"].rolling(window=short_window, min_periods=1, center=False).mean()
    signals["long_mavg"] = stock_data["Close"].rolling(window=long_window, min_periods=1, center=False).mean()
    signals["signal"][short_window:] = np.where(signals["short_mavg"][short_window:] > signals["long_mavg"][short_window:], 1.0, 0.0)
    signals["orders"] = signals["signal"].diff()
    return signals


def plot_fig(ts, stock_data):
    fig = plt.figure()
    ax1 = fig.add_subplot(111, ylabel='Google price in $')
    stock_data["Adj Close"].plot(ax=ax1, color='g', lw=.5)
    ts["short_mavg"].plot(ax=ax1, color='r', lw=2.)
    ts["long_mavg"].plot(ax=ax1, color='b', lw=2.)
    ax1.plot(ts.loc[ts.orders == 1.0].index,
             stock_data["Adj Close"][ts.orders == 1.0],
             '^', markersize=7, color='k')
    ax1.plot(ts.loc[ts.orders == -1.0].index,
             stock_data["Adj Close"][ts.orders == -1.0],
             'v', markersize=7, color='k')
    plt.legend(["Price", "Short mavg", "Long mavg", "Buy", "Sell"])
    plt.title("Double Moving Average Trading Strategy")
    plt.show()


def main():
    goog_data = load_financial_data(start_date='2001-01-01', end_date='2020-01-01', output_file=r'data\goog_data_large.pkl')
    ts = double_moving_average(goog_data, 20, 100)
    plot_fig(ts, goog_data)


if __name__ == '__main__':
    main()
