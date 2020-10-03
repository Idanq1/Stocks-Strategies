import yfinance as yf
import datetime
import dateutil.relativedelta
import os
import sys
import time
import pandas as pd

# TODO: Join pandas when downloading and not after

s = time.time()


# tsla = yf.Ticker("TSLA")
#
# print(tsla.history(prepost=True))
# print(tsla.history(interval="1m", prepost=True, start="2020-09-28"))


def get_price(ticker):
    current_date = datetime.date.today() + datetime.timedelta(days=1)
    past_date = current_date - dateutil.relativedelta.relativedelta(days=1)
    sys.stdout = open(os.devnull, "w")
    data = yf.download(ticker, past_date, current_date)
    sys.stdout = sys.__stdout__
    return data[["Close"]]['Close'].iloc[0]
    # yf.Download(ticker, )


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


stocks_div = 10
tmp = tickers.copy()
stocks700 = []
while tmp:
    stocks700.append(tmp[:stocks_div])
    del tmp[:stocks_div]
# print(len(stocks700))
n = 0
stocks_splt = []
print(f"Downloading {len(tickers)}")
all_stocks = None
for stocks in stocks700:
    current_date = datetime.date.today()
    past_date = current_date - dateutil.relativedelta.relativedelta(days=100)
    if not all_stocks:
        all_stocks = yf.download(" ".join(stocks), start=past_date, end=current_date, group_by="ticker", show_errors=False, progress=True)
    else:
        info = yf.download(" ".join(stocks), start=past_date, end=current_date, group_by="ticker", show_errors=False, progress=True)
        all_stocks = all_stocks.join(info)
    # stocks_splt.append(yf.download(" ".join(stocks), start=past_date, end=current_date, group_by="ticker", show_errors=False, progress=True))
    # if n == 2:
    #     break
    # n += 1

stocks_info = stocks_splt[0]
for i in range(len(stocks_splt)):
    if i == 0:
        continue
    stocks_info = stocks_info.join(stocks_splt[i])

print(stocks_info)

for stock in tickers:
    try:
        price = float(stocks_info[stock]['Close'].iloc[-1])
    except KeyError:
        # print(f"Couldn't find {stock}")
        continue
    if pd.isna(price):
        continue
    print(f"{stock}- {price}")


print(time.time() - s)
