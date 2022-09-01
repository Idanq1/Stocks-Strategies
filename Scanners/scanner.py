import requests, talib, threading, time, csv
import numpy as np
import pandas as pd
import time



symbols = []
api = "https://api.binance.com/api/v3/ticker/price"
api2 = "https://api.binance.com/api/v1/ticker/24hr?symbol="
sList = requests.get(api).json()
expected = ""

for x in range(len(sList)):
    if ("BTC" in sList[x]['symbol']):  # Create list with cryptocurrencies that we can buy with BTC
        if sList[x]['symbol'] in expected:
            symbols.append(sList[x]['symbol'])
        if expected == "":
            symbols.append(sList[x]['symbol'])

date_list = []
open_list = []
high_list = []
low_list = []
close_list = []
volume_list = []
short_window = 9
long_window = 26
RSI_window = 14
timeFrame = "15m"


def gen_signals():
    print("Generating signals...")
    while True:
        for symbol in symbols:
            data = requests.get(api2 + symbol).json()
            openTime = str(data['openTime'])
            closeTime = str(data['closeTime'])
            candle_data = requests.get("https://api.binance.com/api/v1/klines?symbol=" + data['symbol']
                                       + "&interval=" + timeFrame + "&startTime=" + openTime + "&endTime=" + closeTime).json()
            if not candle_data:
                continue

            with open("data\\" + symbol + '.csv', 'wt', newline='') as file:
                header = ['Date', 'Open', 'High', 'Low', 'Close']
                writer = csv.writer(file, delimiter=',')
                writer.writerow(i for i in header)
                for frame in candle_data:
                    writer.writerow(frame[:5])

            # build DataFrame
            df = pd.read_csv("data\\" + symbol + '.csv', header=0)
            df['Date'] = pd.to_datetime(df['Date'], unit='ms')

            # Use TA Lib to generate moving averages
            signals = pd.DataFrame(index=df.index)
            signals['signal'] = 0.0
            signals['short_sma'] = talib.SMA(df['Close'], short_window)
            signals['long_sma'] = talib.SMA(df['Close'], long_window)
            signals['RSI'] = talib.RSI(df['Close'], RSI_window)
            signals['signal'][short_window:] = np.where(signals['short_sma'][short_window:]
                                                        > signals['long_sma'][short_window:], 1.0, 0.0)
            signals['positions'] = signals['signal'].diff()
            print(float(signals['positions'].iloc[-1:].values), float(signals['signal'].iloc[-1:].values), float(signals['RSI'].iloc[-1:].values), symbol)
            close_value = float(df['Close'].iloc[-1:].values)
            close = str('{:.8f}'.format(close_value))
            print(close)
        time.sleep(900)
        threading.Thread(target=gen_signals).start()

# gen_signals()


# threading.Thread(target=gen_signals).start()




if __name__ == '__main__':
    gen_signals()
