import yfinance as yf
import datetime
from patterns.CandleClass import Candle
import time
s = time.time()


def get_candle_class(ticker, period="max", interval="1d", start=None, end=None):
    if start and not end:
        end = datetime.date.today()
    elif not start and end:
        print("Gotta give me a start m8")
        return

    candles = []

    data = yf.download(ticker, period=period, interval=interval, start=start, end=end, progress=False, show_errors=False)
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

for ticker in tickers:
    ticker_candles = get_candle_class(ticker, "10d", "1d")
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
                    print(f"Bullish- {ticker}- Inverted Hammer- {candle.date}")
                else:  # Uptrend
                    print(f"Dubi- {ticker}- Shooting star- {candle.date}")
            elif candle.tail() >= candle.body() * 2 and candle.head() <= candle.body() * 0.8:  # Hammer & Hanging man
                if sma_value < candle.close:  # Downtrend
                    print(f"Bullish- {ticker}- Hammer- {candle.date}")
                else:  # Uptrend
                    print(f"Dubi- {ticker}- Hanging man- {candle.date}")
        # else:
        #     if candle.head() >= candle.body() * 2 and candle.tail() <= candle.body() * 0.8:  # Shooting Star
        #         print(f"Bullish- Shooting Star- {candle.date}")
        #     elif candle.tail() >= candle.body() * 2 and candle.head() <= candle.body() * 0.8:  # Hammer
        #         print(f"Bullish- - {candle.date}")
                # if candle.head() >= candle.body() * 2 and candle.tail() <= candle.body() * 1:  # Inverted hammer, shooting star
