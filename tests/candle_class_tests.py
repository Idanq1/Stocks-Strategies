import yfinance as yf
import datetime
from CandleClass import Candle
import time
import Crypto.patterns as patterns


def download_candles(ticker, period="max", interval="1d", start=None, end=None):
    if start and not end:
        end = datetime.date.today()
    elif not start and end:
        print("Gotta give me a start m8")
        return
    if isinstance(ticker, list):
        return yf.download(" ".join(ticker), period=period, interval=interval, start=start, end=end, progress=False, show_errors=False, group_by="ticker")
    elif isinstance(ticker, str):
        return yf.download(ticker, period=period, interval=interval, start=start, end=end, progress=False, show_errors=False, group_by="ticker")
        # return yf.download(ticker, period=period, interval=interval, start=start, end=end, progress=False, show_errors=False, group_by="ticker")


def get_candles(data, ticker):
    candles = []
    rows = data.shape[0]
    for i in range(rows):
        open_ = data[["Open"]]["Open"].iloc[i]
        close = data[["Close"]]["Close"].iloc[i]
        high = data[["High"]]["High"].iloc[i]
        low = data[["Low"]]["Low"].iloc[i]
        vol = data[["Volume"]]["Volume"].iloc[i]
        date = data.index[i]
        candles.append(Candle(ticker, open_, close, high, low, vol, date))
    # return reversed(candles)
    return candles


def main():
    test_ticker = "TSLA"
    candles = get_candles(download_candles(test_ticker, "7d"), test_ticker)
    print(patterns.is_bullish_engulfing(, candles[-2])


if __name__ == '__main__':
    s = time.time()
    main()
    print(f"Took: {round(time.time() - s, 3)} seconds")




