import pyEX

# print(pyEX.symbolsList("sk_f7adab6d51024970a223590f9ce933d8", version="v1"))


def get_stocks():
    tickers = []
    with open(r"nasdaqtraded.txt", 'r') as f:
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


pyEX.bulkBatch(get_stocks(), ['chart'], '6m', token="sk_f7adab6d51024970a223590f9ce933d8", version="v1")
# pyEX.symbolsDF('sk_e987477a60ef4401905de8b8fffbb76c ').head()
