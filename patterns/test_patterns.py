from CandleClass import Candle
from patterns import Candles
import time
import finnhub
import datetime


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
    except finnhub.exceptions.FinnhubAPIException:
        return False
    return candles_data

    # url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?region=US&lang=en-US&includePrePost=false&interval={interval}&useYfid=true&range={period}&corsDomain=finance.yahoo.com&.tsrc=finance"
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    # res = requests.get(url, headers=headers)
    # return json.loads(res.text)


def get_candles(data, symbol):
    candles_data = []
    if data["s"] != "ok":
        print(data["s"])
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


def main():
    tickers = get_tickers()
    results = {"bullish_engulfing": [], "bearish_engulfing": [], "hammer": [], "inverted_hammer": [],
               "morning_star": [], "evening_star": [], "piercing_line": [], "bullish_kicking": [],
               "three_inside_up": [], "bullish_harami": [], "three_white_soldiers": [], "concealing_babyswallow": [],
               "three_outside_up": []}
    print(len(tickers))
    n = 0
    s = time.time()
    tokens = ["c43baq2ad3iaavqonarg", "c437gqqad3iaavqojj0g"]
    token = tokens[0]
    token_counter = 0
    for stock_ticker in tickers:
        if token_counter > 57:
            token = tokens[0]
            tokens.reverse()
            token_counter = 0

        candles = download_candles(stock_ticker, 4, "D", token)
        token_counter += 1

        if not candles:
            continue
        ticker_candles = get_candles(candles, stock_ticker)
        if not ticker_candles:
            print(stock_ticker)
            continue
        try:
            candles = Candles(ticker_candles[-1], ticker_candles[-2], ticker_candles[-3], ticker_candles[-4])
        except IndexError:
            print(stock_ticker)
            continue
        if candles.average_volume() < 10000:
            continue
        n += 1

        if candles.is_bearish_engulfing():
            results["bearish_engulfing"].append(stock_ticker)
        if candles.is_bullish_engulfing():
            results["bullish_engulfing"].append(stock_ticker)
        if candles.is_hammer():
            results["hammer"].append(stock_ticker)
        if candles.is_inverted_hammer():
            results["inverted_hammer"].append(stock_ticker)
        if candles.is_morning_star():
            results["morning_star"].append(stock_ticker)
        if candles.is_evening_star():
            results["evening_star"].append(stock_ticker)
        if candles.is_piercing_line():
            results["piercing_line"].append(stock_ticker)
        if candles.is_bullish_kicking():
            results["bullish_kicking"].append(stock_ticker)
        if candles.is_three_white_soldiers():
            results["three_white_soldiers"].append(stock_ticker)
        if candles.is_concealing_babyswallow():
            results["concealing_babyswallow"].append(stock_ticker)
        if candles.is_three_outside_up():
            results["three_outside_up"].append(stock_ticker)

        print(n)
        if n % 100 == 0:
            print(f"{n}/{len(tickers)}")
            print(time.time() - s)
            s = time.time()
    for result in results:
        print(result)
        print(results[result])
        print("------------------")


if __name__ == '__main__':
    main()
