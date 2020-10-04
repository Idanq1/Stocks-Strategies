import yfinance as yf
import requests
import json

token = "3e7f436d6a3c2a7afcc35331978aa1d4"

# tickers = "TSLA AAPL DRKG"

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
    if len(tickers) > 1600:  # Around 1600 is the maximum
        break

url = f"https://financialmodelingprep.com/api/v3/quote/{','.join(tickers)}?apikey={token}"


def get_json(url):
    r = requests.get(url)
    print(r.text)


get_json(url)
