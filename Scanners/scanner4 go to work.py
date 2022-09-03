import websockets
import datetime
import requests
import asyncio
import time
import json

# TODO: Add relative volume - request 5m klines as well
# TODO: Do not print the same coin twice on the same kline (Can use time)  -  V
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
    data = {}
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
                data[symbol] = {str(kline_s): {"open": open_, "high": high, "close": close, low: "low", "volume": volume, "is_closed": is_closed, "printed": False}}
            else:
                if str(kline_s) not in data[symbol]:
                    data[symbol][str(kline_s)] = {"open": open_, "high": high, "close": close, low: "low", "volume": volume, "is_closed": is_closed, "printed": False}
                else:
                    data[symbol][str(kline_s)]["open"] = open_
                    data[symbol][str(kline_s)]["high"] = high
                    data[symbol][str(kline_s)]["close"] = close
                    data[symbol][str(kline_s)]["low"] = low
                    data[symbol][str(kline_s)]["volume"] = volume
                    data[symbol][str(kline_s)]["is_closed"] = is_closed

            if len(data[symbol]) >= 3:
                rel_v = []
                for i in data[symbol]:
                    rel_v.append(data[symbol][i]["volume"])
                rel_v = sum(rel_v)/len(rel_v)
                print(symbol)
                print(rel_v)

            did_print = data[symbol][str(kline_s)]["printed"]
            if did_print:
                continue
            to_print = sorter(open_, high, low, close, volume)
            if to_print:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                data[symbol][str(kline_s)]["printed"] = True  # So it doesn't print twice
                print(f"--{symbol}---{current_time}--")
                print(f"Open: {open_}")
                print(f"Close: {close}")
                print(f"Percent change: {round(calc_prcnt(close, open_), 2)}%")
                # print(is_closed)
                print(f"Volume: {volume}")
                print(f"Volume in $: {volume * close}")
                if "rel_v" in data[symbol][str(kline_s)]:
                    print(f"Relative volume: {data[symbol][str(kline_s)]['rel_v']}")
                print(interval)
                print("-------------")

asyncio.get_event_loop().run_until_complete(candle_stick_data())
