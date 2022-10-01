import matplotlib.pyplot as plt
from binance import Client
import pandas as pd
import numpy as np
import winsound
import datetime
import talib


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


def main(ema_1, ema_2, rsi_period, sma_1):
    hist_data = get_historical_data("BTCUSDT", "5m")
    df = pd.DataFrame(columns=["Open", "High", "Close", "Low", "Volume"])
    # ema_1 = 9  # Period
    # ema_2 = 16  # Period
    # rsi_period = 14  # Period
    initial_capital = float(20000.0)

    for candle in hist_data:
        str_time = datetime.datetime.fromtimestamp(candle[0]//1000).strftime('%H:%M:%S')
        # candle[0] = str_time

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
    print(portfolio)


if __name__ == '__main__':
    main(9, 16, 14, 100)

