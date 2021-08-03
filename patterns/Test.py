import json


def get_tickers():
    all_tickers = []
    with open(r"..\nasdaqtradedTest.txt", 'r') as f:
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


tokens_pool_path = r"api_pool.json"
with open(tokens_pool_path, 'r') as f:
    d = json.load(f)

tokens_list = d["tokens"]
print(tokens_list)
allocated_tokens = allocate_tokens(tokens_list, get_tickers())
