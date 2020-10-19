import yfinance as yf
import datetime
from CandleClass import Candle
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


all_tickers = get_tickers()

ticker = "TSLA"
candles = download_candles(ticker, "max", "1d")
ticker_candles = get_candles(candles, ticker)
sma_period = 9
sma_calc = []
sma_value = None
first_candle = None
second_candle = None
# F - S - C
for candle in ticker_candles:
    print("CODE GOES HERE!")
    # if len(sma_calc) < sma_period:
    #     sma_calc.append(candle.close)
    # else:
    #     sma_value = sum(sma_calc) / sma_period
    #     sma_calc = sma_calc[1:]
    #     sma_calc.append(candle.close)
    #
    # print(candle.open)

print(time.time() - s)
