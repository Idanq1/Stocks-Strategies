from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def load_stock_data(stock, start_date, end_date, output_file):
    try:
        df = pd.read_pickle(output_file)
        print('File data found...reading GOOG data')
    except FileNotFoundError:
        print('File not found...downloading the GOOG data')
        df = data.DataReader(stock, 'yahoo', start_date, end_date)
        df.to_pickle(output_file)
    return df


def turtle(stock_data, window_size):
    signals = pd.DataFrame(index=stock_data.index)
    signals["orders"] = 0
    signals["high"] = stock_data["Adj Close"].shift(1).rolling(window_size).max()
    signals["low"] = stock_data["Adj Close"].shift(1).rolling(window_size).min()
    signals["avg"] = stock_data["Adj Close"].shift(1).rolling(window_size).mean()

    signals["long_entry"] = stock_data['Adj Close'] > signals.high
    signals["short_entry"] = stock_data['Adj Close'] < signals.low

    signals['long_exit'] = stock_data['Adj Close'] < signals.avg
    signals['short_exit'] = stock_data['Adj Close'] > signals.avg
    init = True
    position = 0
    for i in range(len(signals)):
        if signals['long_entry'][i] and position == 0:
            signals.orders.values[i] = 1
            position = 1
        # elif signals['short_entry'][i] and position == 0:
            # signals.orders.values[i] = -1
            # position = -1
        # elif signals['short_exit'][i] and position > 0:
            # signals.orders.values[i] = -1
            # position = 0
        elif signals['long_exit'][i] and position > 0:
            signals.orders.values[i] = -1
            position = 0
        else:
            signals.orders.values[i] = 0
    return signals


def plot_fig(ts, stock_data):
    fig = plt.figure()
    ax1 = fig.add_subplot(111, ylabel='Google price in $')
    stock_data["Adj Close"].plot(ax=ax1, color='g', lw=.5)
    stock_data["money"].plot(ax=ax1, color='m', lw=.5)
    ts["high"].plot(ax=ax1, color='b', lw=.5)
    ts["low"].plot(ax=ax1, color='r', lw=.5)
    ts["avg"].plot(ax=ax1, color='y', lw=.5)
    ax1.plot(ts.loc[ts.orders == 1.0].index, stock_data["Adj Close"][ts.orders == 1], '^', markersize=7, color='k')
    ax1.plot(ts.loc[ts.orders == -1].index, stock_data["Adj Close"][ts.orders == -1], 'v', markersize=7, color='k')
    plt.legend(["Price", "returns", "high", "low", "avg", "Buy", "Sell"])
    plt.title("Turtle Trading Strategy")
    plt.show()


def calculate_gain(ts, stock_data, start_money):
    money_in_stocks = start_money
    stock_data["money"] = money_in_stocks
    stocks = 0
    money_left_aside = 0
    holding = False
    for i in range(len(ts)):
        price = stock_data["Close"][i]
        money = money_in_stocks + money_left_aside
        stock_data["money"][i] = money

        if holding:
            money_in_stocks = stocks * price

        if ts.orders.values[i] == 1:  # Buy
            stocks = money // price
            if stocks == 0:
                continue
            money_in_stocks = stocks * price
            money_left_aside = money - money_in_stocks
            holding = True

        elif ts.orders.values[i] == -1:  # Sell
            stocks = 0
            money_left_aside = money
            money_in_stocks = 0
            holding = False
    return stock_data


def calculate_returns(ts, stock_data, start_money):
    stock_data["prcnt"] = ((stock_data["Adj Close"] - stock_data["Adj Close"][0]) / stock_data["Adj Close"][0]) * 100
    print(stock_data)
    print(stock_data["Adj Close"][0])
    money_in_stocks = start_money
    stock_data["sim_prcnt"] = money_in_stocks
    stocks = 0
    money_left_aside = 0
    holding = False
    for i in range(len(ts)):
        price = stock_data["Close"][i]
        money = money_in_stocks + money_left_aside
        stock_data["sim_prcnt"][i] = ((money - start_money) / start_money) * 100

        if holding:
            money_in_stocks = stocks * price

        if ts.orders.values[i] == 1:  # Buy
            stocks = money // price
            if stocks == 0:
                continue
            money_in_stocks = stocks * price
            money_left_aside = money - money_in_stocks
            holding = True

        elif ts.orders.values[i] == -1:  # Sell
            stocks = 0
            money_left_aside = money
            money_in_stocks = 0
            holding = False
    return stock_data


def plot_fig_returns(ts, stock_data):
    fig = plt.figure()
    ax1 = fig.add_subplot(111, ylabel='Percents')
    stock_data["prcnt"].plot(ax=ax1, color='g', lw=.5)
    stock_data["sim_prcnt"].plot(ax=ax1, color='m', lw=.5)
    # ts["high"].plot(ax=ax1, color='b', lw=.5)
    # ts["low"].plot(ax=ax1, color='r', lw=.5)
    # ts["avg"].plot(ax=ax1, color='y', lw=.5)
    ax1.plot(ts.loc[ts.orders == 1.0].index, stock_data["prcnt"][ts.orders == 1], '^', markersize=7, color='k')
    ax1.plot(ts.loc[ts.orders == -1].index, stock_data["prcnt"][ts.orders == -1], 'v', markersize=7, color='k')
    ax1.plot(ts.loc[ts.orders == 1.0].index, stock_data["sim_prcnt"][ts.orders == 1], '^', markersize=7, color='k')
    ax1.plot(ts.loc[ts.orders == -1].index, stock_data["sim_prcnt"][ts.orders == -1], 'v', markersize=7, color='k')
    plt.legend(["Google returns", "My returns", "Buy", "Sell"])
    plt.title("Turtle Trading Strategy")
    plt.show()


def main():
    goog_data = load_stock_data(stock="PRFX", start_date='2001-01-01', end_date='2022-06-06', output_file=r'data\goog_data_large.pkl')
    ts = turtle(goog_data, 100)
    # goog_data = calculate_gain(ts, goog_data, 300.0)
    # plot_fig(ts, goog_data)
    goog_data = calculate_returns(ts, goog_data, 1000.0)
    plot_fig_returns(ts, goog_data)


if __name__ == '__main__':
    main()
