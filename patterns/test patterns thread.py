import json
from CandleClass import Candle
from patterns import Candles
import time
import finnhub
import datetime
import threading


def download_candles(ticker, period=4, interval="D", token=None):
    if not token:
        return False
    day = datetime.datetime.today().weekday()
    if day == 6:
        period += 1
    elif day == 0:
        period += 2
    start_time = datetime.datetime.now() - datetime.timedelta(days=period)
    finnhub_client = finnhub.Client(api_key=token)
    try:
        candles_data = finnhub_client.stock_candles(ticker, interval, int(start_time.timestamp()), int(time.time()))
    except Exception as e:
        exception_status = e.status_code
        return exception_status
        # 429- limit error
        # 403- BBWI.V
    return candles_data


def get_candles(data, symbol):
    candles_data = []
    if data["s"] != "ok":
        return False
    for i in range(len(data["v"])):
        close = data["c"][i]
        open_ = data["o"][i]
        high = data["h"][i]
        low = data["l"][i]
        volume = data["v"][i]
        date = data["t"][i]
        candles_data.append(Candle(symbol, open_, close, high, low, volume, date))
    return candles_data


def get_tickers():
    all_tickers = []
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
        all_tickers.append(stock_ticker)
    return all_tickers


def main(ticker, token="c43f8kiad3if0j0skdvg"):
    global allocated_tokens
    candles = download_candles(ticker, 4, "D", token)
    if candles == 429:
        allocated_tokens[token]["status"] = False
        return
        # limit
    if candles == 403:
        return
    if not candles:
        return
    ticker_candles = get_candles(candles, ticker)
    if not ticker_candles:
        return
    try:
        candles = Candles(ticker_candles[-1], ticker_candles[-2], ticker_candles[-3], ticker_candles[-4])
    except IndexError:
        return
    if candles.is_bearish_engulfing():
        results["bearish_engulfing"].append(ticker)
    if candles.is_bullish_engulfing():
        results["bullish_engulfing"].append(ticker)
    if candles.is_hammer():
        results["hammer"].append(ticker)
    if candles.is_inverted_hammer():
        results["inverted_hammer"].append(ticker)
    if candles.is_morning_star():
        results["morning_star"].append(ticker)
    if candles.is_evening_star():
        results["evening_star"].append(ticker)
    if candles.is_piercing_line():
        results["piercing_line"].append(ticker)
    if candles.is_bullish_kicking():
        results["bullish_kicking"].append(ticker)
    if candles.is_three_white_soldiers():
        results["three_white_soldiers"].append(ticker)
    if candles.is_concealing_babyswallow():
        results["concealing_babyswallow"].append(ticker)
    if candles.is_three_outside_up():
        results["three_outside_up"].append(ticker)


def allocate_tokens(tokens, all_tickers):
    allocated_tokens = {}
    for token in tokens:
        allocated_tokens[token] = {"status": True, "tickers": []}
    while True:
        for token in tokens:
            allocated_tokens[token]["tickers"].append(all_tickers[0])
            all_tickers.pop(0)
            if not all_tickers:
                break
        if not all_tickers:
            break
    return allocated_tokens


if __name__ == '__main__':
    s = time.time()
    tokens_pool_path = r"api_pool.json"
    with open(tokens_pool_path, 'r') as f:
        d = json.load(f)
    tokens_list = d["tokens"]
    results = {"bullish_engulfing": [], "bearish_engulfing": [], "hammer": [], "inverted_hammer": [],
               "morning_star": [], "evening_star": [], "piercing_line": [], "bullish_kicking": [],
               "three_inside_up": [], "bullish_harami": [], "three_white_soldiers": [], "concealing_babyswallow": [],
               "three_outside_up": []}
    tested_tic = []
    allocated_tokens = allocate_tokens(tokens_list, get_tickers())
    tickers = get_tickers()
    while len(tickers) > 3:
        for token in tokens_list:
            for ticker in allocated_tokens[token]["tickers"]:
                if not allocated_tokens[token]["status"]:
                    allocated_tokens[token]["status"] = True
                    break
                if ticker in tested_tic:
                    continue
                tested_tic.append(ticker)
                main1 = threading.Thread(target=main, args=(ticker, token))
                main1.start()
                tickers.remove(ticker)
        if len(tickers) == 0:
            break
        time.sleep(59)
    main1.join()
    print(results)
    print(time.time() - s)
