import datetime
import time
import yfinance as yf
import json
from CandleClass import Candle

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


def get_json(path=r"data\SMA.json"):
    """
    Returns if the json is legal
    :param path:
    :return:
    """
    with open(path, 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            return json.loads("{}")
        return data


def write_json(data, path=r"data/SMA.json"):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def reset_file(path=r"data/SMA.json"):
    with open(path, 'w') as f:
        f.write("")


def buy(stock, shares, price, date, path=r"data/SMA.json"):
    global bal
    # print(f"shares {shares}")
    # print(f"price {price}")
    # print(f"---------------")
    data = get_json()
    if "active" not in data:
        data["active"] = {}
    if stock not in data["active"]:
        data["active"][stock] = {"shares": shares, "buy": price, "date": str(date)}
    # print(data)
    bal -= (buy_shares * price)

    write_json(data, path)


def sell(stock, price, date, shares=None, path=r"data/SMA.json"):
    global bal
    data = get_json()

    if "active" not in data:
        return False
    elif data["active"] == {}:
        return False

    st = data["active"][stock]
    b_shares = st["shares"]
    b_date = st["date"]
    b_price = st["buy"]
    data["active"] = {}
    if not shares:
        shares = b_shares
    if "history" not in data:
        data["history"] = {}
    if stock not in data["history"]:
        data["history"][stock] = {}
    # print(date)
    # print(b_price)
    data["history"][stock][str(date)] = {"buy": {"price": b_price, "date": b_date, "shares": b_shares}, "sell": {"price": price, "date": str(date), "shares": shares}}

    bal += (shares * price)
    write_json(data, path)


ticker = "TWTR"
candles = download_candles(ticker, "max", "1d")
ticker_candles = get_candles(candles, ticker)

sma_period = 9
sma_calc = []
sma_value = None

rsi_period = 14
rsi_calc = []

bal = 10000
bought = False
prev_candle = None
prev_sma = None
conf = True
reset_file()
for candle in ticker_candles:
    if len(sma_calc) < sma_period:
        sma_calc.append(candle.close)
    else:
        sma_value = sum(sma_calc) / sma_period
        sma_calc = sma_calc[1:]
        sma_calc.append(candle.close)
    if conf:
        if not prev_candle:
            prev_candle = candle
            continue

    if sma_value:
        if conf:
            if not prev_sma:
                prev_sma = sma_value
                continue
        if candle.close > sma_value and not bought:  # BUY
            if not conf:
                buy_shares = int(bal / candle.close)
                buy(ticker, buy_shares, candle.close, candle.date)
                bought = True
            if conf:
                if prev_candle.close > prev_sma:
                    buy_shares = int(bal / candle.close)
                    buy(ticker, buy_shares, candle.close, candle.date)
                    bought = True
        elif candle.close < sma_value and bought:  # SELL
            sell(ticker, candle.close, candle.date)
            bought = False
    if conf:
        prev_candle = candle

if bought and candle:
    sell(ticker, candle.close, candle.date)

if conf:
    print(f"End balance- {bal} while confirmation is on")
else:
    print(f"End balance- {bal}")
print(time.time() - s)
