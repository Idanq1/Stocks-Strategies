import ffn
import time


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


s = time.time()
# tickers = get_tickers()
tickers = []
# print(tickers)
prices = ffn.get(",".join(tickers), start="2020-10-10")
print(prices)
print(time.time() - s)
