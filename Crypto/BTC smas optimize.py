import time

import matplotlib.pyplot as plt
from binance import Client
import pandas as pd
import numpy as np
import winsound
import datetime
import talib
import json

api_key = "8AiGAyxlhYQaRpE1s7097hx5sZ12Ogtr8ir9DsyztaD5j24LrI0fEoToDzCI5lle"
api_secret = "VhudTs0HsBVFNdSTghmqfCjUuIXF6rFiXIfROxHIaM71TGgib7NeZ5aOsJUHjI9f"
client = Client(api_key, api_secret)


def get_all_tokens(currency="USDT"):
    res = client.get_all_tickers()
    tokens = []
    for token in res:
        if currency in token["symbol"]:
            tokens.append(token["symbol"])
    return tokens


def get_historical_data(token, interval, start=None, end=None):
    candles_data = client.get_historical_klines(token, interval, start, end)
    return candles_data


def draw_figure(df):
    closes = df["Close"]
    ema1 = df["EMA9"]
    ema2 = df["EMA16"]
    rsi = df["RSI14"]
    fig = plt.figure()
    ax1 = fig.add_subplot(111, ylabel='BTCUSDT')
    ax1.plot(df.loc[df.positions == 1.0].index, df.Close[df.positions == 1.0], "^", markersize=5, color='g')
    ax1.plot(df.loc[df.positions == -1.0].index, df.Close[df.positions == -1.0], "v", markersize=5, color='r')
    closes.plot(ax=ax1, color='c', lw=1.2, legend=True)
    ema1.plot(ax=ax1, color="tab:orange", lw=1.2, legend=True)
    ema2.plot(ax=ax1, color='m', lw=1.2, legend=True)
    ax3 = fig.add_subplot(313, ylabel='RSI')
    ax3.axhline(y=70)
    ax3.axhline(y=50, linestyle='dotted', lw=1.)
    ax3.axhline(y=30)
    rsi.plot(ax=ax3, color='b', lw=1.5, legend=True)
    plt.show()


def alert():
    for i in range(10):
        winsound.Beep(2000, 80)


def main(df, ema_1, ema_2, rsi_period, sma_1):
    initial_capital = float(20000.0)

    for candle in hist_data:

        timestmp = candle[0]
        open_ = float(candle[1])
        high = float(candle[2])
        low = float(candle[3])
        close = float(candle[4])
        vol = float(candle[5])
        df.loc[timestmp] = (open_, high, close, low, vol)
    df = df.assign(RSI14=pd.Series(talib.RSI(df["Close"], rsi_period)))
    df = df.assign(EMA9=pd.Series(talib.EMA(df["Close"], ema_1)))
    df = df.assign(EMA16=pd.Series(talib.EMA(df["Close"], ema_2)))
    df = df.assign(SMA100=pd.Series(talib.EMA(df["Close"], sma_1)))
    df["signal"] = np.where((df["EMA9"] > df["EMA16"]) & (df["Close"] > df["EMA9"]) & (df["RSI14"] > 50) & (df["SMA100"] < df["Close"]), 1.0, 0.0)
    df["positions"] = df["signal"].diff()


    pd.set_option('display.max_columns', None)
    # print(df)
    # draw_figure(df)

    positions = pd.DataFrame(index=df.index).fillna(0.0)
    portfolio = pd.DataFrame(index=df.index).fillna(0.0)
    positions["BTCUSDT"] = df["signal"]
    portfolio['positions'] = (positions.multiply(df['Close'], axis=0))
    portfolio['cash'] = initial_capital - (positions.diff().multiply(df['Close'], axis=0)).cumsum()
    portfolio['total'] = portfolio['positions'] + portfolio['cash']
    return portfolio.iloc[-1]["total"]


if __name__ == '__main__':
    s = time.time()
    hist_data = get_historical_data("ETHUSDT", "5m")
    data = pd.DataFrame(columns=["Open", "High", "Close", "Low", "Volume"])

    tests = []
    sma1 = range(50, 200, 25)
    ema1 = range(4, 20)
    ema2 = range(7, 20)
    rsi = range(5, 18)
    i = 0
    for shrt_ema in ema1:
        print(f"Checking ema1: {shrt_ema}")
        for long_ema in ema2:
            for rsi_v in rsi:
                for long_sma in sma1:
                    total = main(data, shrt_ema, long_ema, rsi_v, long_sma)
                    if total < 20000:
                        continue
                    tests.append({"ema1": shrt_ema, "ema2": long_ema, "rsi": rsi_v, "sma1": long_sma, "total": total})

    tests = sorted(tests, key=lambda x: x["total"])
    tests.reverse()
    for test in tests:
        print(test)
    print(time.time() - s)