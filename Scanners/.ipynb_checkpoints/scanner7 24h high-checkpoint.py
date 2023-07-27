import pandas as pd
import numpy as np
import websockets
import winsound
import datetime
import requests
import asyncio
import json
import time


def get_tickers():
    symbols = []
    api = "https://api.binance.com/api/v3/ticker/price"
    s_list = requests.get(api).json()
    expected = ""
    for x in range(len(s_list)):
        if "USDT" in s_list[x]['symbol']:  # Create list with cryptocurrencies that we can buy with BTC
            if s_list[x]['symbol'] in expected:
                symbols.append(s_list[x]['symbol'])
            if expected == "":
                symbols.append(s_list[x]['symbol'])
    return symbols


def calc_prcnt(num1, num2):
    return ((num1 - num2) / num2) * 100


def sorter(df, symbol):
    df = df[symbol]
    candle = df.iloc[-1]
    close = candle["Close"]
    vol_d = candle["Vol"] * close
    # rel_vol_d =
    at_high = highs[symbol]["high"]  # 24 high
    at_low = highs[symbol]["low"]  # 24 low
    prct_hl = calc_prcnt(at_high, at_low)
    prct = calc_prcnt(at_high, float(close))  # Percent between high and close

    if vol_d < 10000:  # vol in dollars has to be more than 10,000$
        return False
    if prct * 10 < prct_hl:  # Should be that only the top of the
        return True
    return False


def get_24_h():
    api = "https://api.binance.com/api/v3/ticker/24hr"
    s_list = requests.get(api).json()
    global highs
    for s in s_list:
        symbol = s["symbol"]
        high = float(s["highPrice"])
        low = float(s["lowPrice"])
        highs[symbol] = {"high": high, "low": low}


def alert():
    for i in range(10):
        winsound.Beep(2000, 80)


async def candle_stick_data():
    data = {}
    save_number = 1
    printed = {}

    url = "wss://stream.binance.com:9443/ws/"  # steam address
    symbols = get_tickers()
    to_remove = ["BTCUSDT", "BUSDUSDT", "USDTTRY", "USDTBRL", "USDTBIDR", "USDTRUB", "USDTDAI", "USDTUAH", "USDTIDRT", "USDTNGN"]  # Mostly fiat
    for sym_r in to_remove:
        symbols.remove(sym_r)
    symbols = [f"{sym.lower()}@kline_1m" for sym in symbols]
    first_pair = 'btcusdt@kline_1m'  # first pair

    connection = websockets.connect(url + first_pair)
    async with connection as sock:
        print(len(symbols))

        pairs = []
        while symbols:
            sym_list = symbols[:100]  # Make pairs with only 100 coins (to prevent payload too long)
            symbols = symbols[100:]

            pair = {"method": "SUBSCRIBE", "params": sym_list, "id": 1}
            pairs.append(json.dumps(pair))
        print("---------")
        for pair in pairs:
            await sock.send(pair)
        while True:
            resp = json.loads(await sock.recv())
            if "result" in resp:
                if resp["result"] is None:
                    continue
            symbol = resp["s"]
            e_time = int(resp["E"])
            kline_s = resp["k"]["t"]
            kline_c = resp["k"]["T"]
            interval = resp["k"]["i"]
            open_ = float(resp["k"]["o"])
            high = float(resp["k"]["h"])
            low = float(resp["k"]["l"])
            close = float(resp["k"]["c"])
            volume = float(resp["k"]["v"])
            is_closed = bool(resp["k"]["x"])
            if symbol not in data:
                data[symbol] = pd.DataFrame(np.array([[open_, high, close, low, volume, is_closed]]), index=[kline_s], columns=["Open", "High", "Close", "Low", "Vol", "Is Closed"])
            else:
                data[symbol].loc[kline_s] = (open_, high, close, low, volume, is_closed)  # Adds a new row
                if len(data[symbol]) > save_number:  # Deletes the first row for memory wise and so it doesn't calculate new relative volume with more than the last 5 candles
                    data[symbol].drop(index=data[symbol].index[0], axis=0, inplace=True)

            if symbol in printed:
                sb = time.time() - printed[symbol]  # Sent before (x) seconds
                if sb < 300:  # Print every 5 minutes so it won't spam
                    get_24_h()
                    continue

            nan = False
            for x in data[symbol].iloc[-1].tolist():
                if np.isnan(x):
                    nan = True
            if not nan:  # Check if there's a nan value in the array (The indicators)
                to_print = sorter(data, symbol)
                if to_print:
                    printed[symbol] = time.time()
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"--{symbol}---{current_time}--")
                    print(f"High: {highs[symbol]['high']}")
                    print(f"Price: {close}")
                    print("----------------")
                    alert()
                    get_24_h()  # Reset all the highs/lows


def main():
    get_24_h()
    print(datetime.datetime.now().strftime("%H:%M:%S"))
    asyncio.get_event_loop().run_until_complete(candle_stick_data())


if __name__ == '__main__':
    highs = {}
    main()

