import pandas as pd
import numpy as np
import websockets
import winsound
import datetime
import requests
import asyncio
import json
import time


# TODO: Add relative volume  - V
# TODO: Do not print the same coin twice on the same kline (Can use time)  -  V
# TODO: Alert noise  - V
# TODO: Also print time  - V


def get_tickers():
    symbols = []
    api = "https://api.binance.com/api/v3/ticker/price"
    sList = requests.get(api).json()
    expected = ""
    for x in range(len(sList)):
        if "USDT" in sList[x]['symbol']:  # Create list with cryptocurrencies that we can buy with BTC
            if sList[x]['symbol'] in expected:
                symbols.append(sList[x]['symbol'])
            if expected == "":
                symbols.append(sList[x]['symbol'])
    return symbols


def calc_prcnt(num1, num2):
    return ((num1 - num2) / num2) * 100


def sorter(df):
    prcnt_threshold = 1
    volume_threshold = 15000
    volume_above_threshold = 2  # Multiply by how much
    volume_d_rel = 9000
    last_candle = df.iloc[-1]
    open_ = last_candle["Open"]
    close = last_candle["Close"]
    low = last_candle["Low"]
    high = last_candle["High"]
    rel_v = last_candle["rel_v"]
    volume = last_candle["Volume"]

    d_volume = volume * close  # Volume in $s
    prcnt = calc_prcnt(high, open_)
    if prcnt > prcnt_threshold:  # Candle is up by 1.5%
        if rel_v * volume_above_threshold < volume:  # Checks if there's a spike in the volume (at least x2 of the previous 5 candles)
            if d_volume > volume_threshold:
                if rel_v * close > volume_d_rel:
                    return True
    return False


def alert():
    for i in range(10):
        winsound.Beep(2000, 80)


async def candle_stick_data():
    data = {}
    rel_v_period = 5
    printed = []

    url = "wss://stream.binance.com:9443/ws/"  # steam address
    symbols = get_tickers()
    symbols.remove("BTCUSDT")  # Cause I have no idea what to put on first pair
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

            rel_v = np.nan
            if symbol not in data:
                data[symbol] = pd.DataFrame(np.array([[open_, high, close, low, volume, is_closed, rel_v]]), index=[kline_s], columns=["Open", "High", "Close", "Low", "Volume", "Is Closed", "rel_v"])
            else:
                if len(data[symbol]) >= rel_v_period:
                    volumes = data[symbol]["Volume"].tolist()
                    rel_v = sum(volumes)/len(volumes)
                data[symbol].loc[kline_s] = (open_, high, close, low, volume, is_closed, rel_v)  # Adds a new row
                if len(data[symbol]) > rel_v_period:  # Deletes the first row for memory wise and so it doesn't calculate new relative volume with more than the last 5 candles
                    data[symbol].drop(index=data[symbol].index[0], axis=0, inplace=True)

            if symbol in printed:
                if is_closed:  # So it doesn't print twice the same candle
                    printed.remove(symbol)
                continue

            nan = False
            for x in data[symbol].iloc[-1].tolist():
                if np.isnan(x):
                    nan = True
            if not nan:  # Check if there's a nan value in the array (The indicators)
                to_print = sorter(data[symbol])
                rel_v = data[symbol].iloc[-1]['rel_v']
                rel_v_d = rel_v * close
                if to_print:
                    printed.append(symbol)
                    alert()
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"--{symbol}---{current_time}--")
                    print(f"Percent change: {round(calc_prcnt(close, open_), 2)}%")
                    print(f"Relative Volume in $: {rel_v_d}")
                    print(f"Volume in $: {rel_v}")
                    print(interval)
                    print("----------------")


asyncio.get_event_loop().run_until_complete(candle_stick_data())
