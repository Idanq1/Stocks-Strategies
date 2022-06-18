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


def naive_momentum_trading(stock_data, nb_conseq_days):
    signals = pd.DataFrame(index=stock_data.index)
    signals["orders"] = 0
    cons_day = 0
    prior_price = 0
    init = True
    for k in range(len(stock_data['Adj Close'])):
        price = stock_data['Adj Close'][k]
        # print(f"Price {price}")
        # print(f"Prior {prior_price}")
        # print(k)
        # print(cons_day)
        # print("-----------------")
        if init:
            prior_price = price
            init = False
            continue
        elif price > prior_price:
            if cons_day < 0:
                cons_day = 0
            cons_day += 1
        elif price < prior_price:
            if cons_day > 0:
                cons_day = 0
            cons_day -= 1
        if cons_day == nb_conseq_days:
            signals['orders'][k] = 1
        elif cons_day == -nb_conseq_days:
            signals['orders'][k] = -1
        prior_price = price
    return signals


def plot_fig(ts, stock_data):
    fig = plt.figure()
    ax1 = fig.add_subplot(111, ylabel='Google price in $')
    stock_data["Adj Close"].plot(ax=ax1, color='g', lw=.5)
    ax1.plot(ts.loc[ts.orders == 1.0].index,
             stock_data["Adj Close"][ts.orders == 1],
             '^', markersize=7, color='k')
    ax1.plot(ts.loc[ts.orders == -1.0].index,
             stock_data["Adj Close"][ts.orders == -1],
             'v', markersize=7, color='k')
    plt.legend(["Price", "Buy", "Sell"])
    plt.title("Turtle Trading Strategy")
    plt.show()


def main():
    goog_data = load_financial_data(start_date='2001-01-01', end_date='2020-01-01',
                                    output_file=r'data\goog_data_large.pkl')
    ts = naive_momentum_trading(goog_data, 8)
    plot_fig(ts, goog_data)


if __name__ == '__main__':
    main()
