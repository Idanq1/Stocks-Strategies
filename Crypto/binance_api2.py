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


def main():
    tokens = get_all_tokens()
    for token in tokens:
        candles = get_historical_data(token, "1m", "12 minutes ago UTC")
        change_sum = []
        for candle in candles:
            if candle == candles[-2]:
                if sum(change_sum) == 0:
                    break
                change_sum = [c for c in change_sum if c > 0]  # Delete all 0 numbers
                avg_change = sum(change_sum)/len(change_sum)

                # if abs(candle.change()) > (avg_change * 10) and candle.volume > 50000:
                if abs(candle.change()) > 3:
                    print(candle.ticker)
                    print("last candle change:", candle.change())
                    print(avg_change * 10)
                    print("-------")
                    for i in range(10):
                        winsound.Beep(2000, 80)
                break
            else:
                change_sum.append(abs(candle.change()))


if __name__ == '__main__':
    while True:
        # s = time.time()
        main()
        # print(time.time() - s)
