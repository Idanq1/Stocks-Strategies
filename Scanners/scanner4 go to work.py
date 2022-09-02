import asyncio
import websockets
import requests
import time
import json


# TODO: Add relative volume
# TODO: Do not print the same coin twice on the same kline (Can use time)
# TODO: Alert noise
# TODO: Also print time

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
    return ((num1-num2)/num2) * 100


def sorter(open_, high, low, close, volume):
    prcnt = calc_prcnt(close, open_)
    if prcnt > 1.5:
        return True
    return False


async def candle_stick_data():
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
            pair = str(pair)
            pair = pair.replace("'", '"')
            print(pair)
            pairs.append(pair)

        print("---------")
        for pair in pairs:
            await sock.send(pair)
        while True:
            resp = json.loads(await sock.recv())
            if "result" in resp:
                if resp["result"] is None:
                    continue
            new_time = True

            symbol = resp["s"]
            e_time = int(resp["E"])
            # kline_s = resp["k"]["t"]
            # kline_c = resp["k"]["T"]
            interval = resp["k"]["i"]
            open_ = float(resp["k"]["o"])
            high = float(resp["k"]["h"])
            low = float(resp["k"]["l"])
            close = float(resp["k"]["c"])
            volume = float(resp["k"]["v"])
            is_closed = bool(resp["k"]["x"])

            if is_closed:
                new_time = True

            to_print = sorter(open_, high, low, close, volume)
            if to_print:
                print(symbol)
                print(open_)
                print(close)
                print(is_closed)
                print(volume)
                print(interval)
                print("-------------")

asyncio.get_event_loop().run_until_complete(candle_stick_data())
