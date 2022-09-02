import asyncio
import websockets
import requests
import json


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


async def candle_stick_data():
    url = "wss://stream.binance.com:9443/ws/"  # steam address
    first_pair = 'bnbbtc@kline_1m'  # first pair
    # first_pair = '!miniTicker@arr'  # first pair

    connection = websockets.connect(url + first_pair)
    async with connection as sock:
        symbols = get_tickers()
        symbols = [f"{sym.lower()}@kline_1m" for sym in symbols]
        print(len(symbols))
        # sym_list = []
        # for symbol in symbols:
        #     sym_list.append(f"{symbol.lower()}@kline_1m")
        # pairs = {"method": "SUBSCRIBE", "params": sym_list, "id": 1}  # other pairs

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
            e_time = resp["E"]
            kline_s = resp["k"]["t"]
            kline_c = resp["k"]["T"]
            interval = resp["k"]["i"]
            open_ = resp["k"]["o"]
            high = resp["k"]["h"]
            low = resp["k"]["l"]
            close = resp["k"]["c"]
            volume = resp["k"]["v"]
            is_closed = resp["k"]["x"]
            # if not is_closed:
            #     continue
            print(symbol)
            print(open_)
            print(close)
            print(is_closed)
            print(volume)
            print(interval)
            print("-------------")

asyncio.get_event_loop().run_until_complete(candle_stick_data())
