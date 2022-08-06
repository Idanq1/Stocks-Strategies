from binance import Client
import time
from CandleClass import Candle
import winsound

api_key = "8AiGAyxlhYQaRpE1s7097hx5sZ12Ogtr8ir9DsyztaD5j24LrI0fEoToDzCI5lle"
api_secret = "VhudTs0HsBVFNdSTghmqfCjUuIXF6rFiXIfROxHIaM71TGgib7NeZ5aOsJUHjI9f"
client = Client(api_key, api_secret)


def get_all_tokens(currency="USDT"):
    res = client.get_all_tickers()
    tokens = []
    for token in res:
        if currency in token["symbol"]:
            tokens.append(token["symbol"])
    return tokens


def get_historical_data(token, interval, start, end=None):
    candles_data = client.get_historical_klines(token, interval, start, end)
    candles = []
    for candle in candles_data:
        candles.append(Candle(token, float(candle[1]), float(candle[4]), float(candle[2]), float(candle[3]), float(candle[5]), float(candle[0])))
    return candles


def alert():
    for i in range(10):
        winsound.Beep(2000, 80)


def calc_sma(candles, length):
    closes = []
    i = 0
    for candle in candles:
        if i >= length:
            break
        closes.append(candle.close)
        i += 1
    return sum(closes)/len(closes)


def is_ok(candles):
    if not candles:
        return False
    return True


def main():
    s = time.time()
    tokens = get_all_tokens()
    i = 0
    for token in tokens:
        i += 1
        print(token)
        candles = get_historical_data(token, "5m", "4 hours ago UTC")
        if not is_ok(candles):
            continue
        sma = calc_sma(candles, 15)
        print(sma)
        print("-------------------")


if __name__ == '__main__':
    # while True:
    #     s = time.time()
    main()
    #     print(s-time.time())
