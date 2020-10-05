import yfinance as yf
import datetime
from patterns.CandleClass import Candle
import time
s = time.time()


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
# return data


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


def get_tickers():
    tickers = []
    with open(r"..\nasdaqtraded.txt", 'r') as f:
        stock_list = f.readlines()

    for stock in stock_list:  # 700
        stock_ticker = stock.split("|")[1]
        if stock_ticker == "Symbol":
            continue
        if "$" in stock_ticker:
            continue
        if stock_ticker == "":
            continue
        tickers.append(stock_ticker)
    return tickers


tickers = get_tickers()

n = 0
div = 700
volume_threshold = 100000  # Filter out stocks with less than this volume.
tmp_tickers = []
ticker_candles = None
for stock_ticker in tickers:
    if n < div:
        tmp_tickers.append(stock_ticker)
        n += 1
        continue
    n = 0
    # ticker_candles = get_candle_class(ticker, "10d", "1d")
    candles = download_candles(tmp_tickers, "10d", "1d")
    for tmp_ticker in tmp_tickers:
        ticker_candles = get_candles(candles[tmp_ticker], tmp_ticker)
        if ticker_candles[-2].volume < volume_threshold:  # Two because the volume on the last candle isn't complete
            continue
        sma_period = 9
        sma_calc = []
        sma_value = None
        for candle in ticker_candles:
            if len(sma_calc) < sma_period:
                sma_calc.append(candle.close)
            else:
                sma_value = sum(sma_calc) / sma_period
                sma_calc = sma_calc[1:]
                sma_calc.append(candle.close)

            if sma_value:
                if candle.head() >= candle.body() * 2 and candle.tail() <= candle.body() * 0.8:  # Inverted hammer & Shooting star
                    if sma_value < candle.close:  # Downtrend
                        print(f"Bullish- {candle.ticker}- Inverted Hammer- {candle.date}")
                    else:  # Uptrend
                        print(f"Dubi- {candle.ticker}- Shooting star- {candle.date}")
                elif candle.tail() >= candle.body() * 2 and candle.head() <= candle.body() * 0.8:  # Hammer & Hanging man
                    if sma_value < candle.close:  # Downtrend
                        print(f"Bullish- {candle.ticker}- Hammer- {candle.date}")
                    else:  # Uptrend
                        print(f"Dubi- {candle.ticker}- Hanging man- {candle.date}")
    tmp_tickers = []
print(time.time() - s)
