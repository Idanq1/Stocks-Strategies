import yfinance as yf
import datetime
from patterns.CandleClass import Candle


def get_candle_class(ticker, period="max", interval="1d", start=None, end=None):
    if start and not end:
        end = datetime.date.today()
    elif not start and end:
        print("Gotta give me a start m8")
        return

    candles = []

    data = yf.download(ticker, period=period, interval=interval, start=start, end=end)
    rows = data.shape[0]
    for i in range(rows):
        open_ = data[["Open"]]["Open"].iloc[i]
        close = data[["Close"]]["Close"].iloc[i]
        high = data[["High"]]["High"].iloc[i]
        low = data[["Low"]]["Low"].iloc[i]
        vol = data[["Volume"]]["Volume"].iloc[i]
        date = data.index[i]
        candles.append(Candle(ticker, open_, close, high, low, vol, date))
    return reversed(candles)


# TODO: Find trend
# TODO: Do for hammer and hanging well as well

tsla_candles = get_candle_class("TSLA", "max", "1d")
for candle in tsla_candles:
    if candle.head() >= candle.body() * 2 and candle.tail() <= candle.body() * 1:  # Inverted hammer, shooting star
        print(candle.date)
