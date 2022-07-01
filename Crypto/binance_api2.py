from CandleClass import Candle
from binance import Client
import threading
import winsound
import time

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


def main(token):
    candles = get_historical_data(token, "1m", "15 minutes ago UTC")
    change_sum = []
    for candle in candles:
        if candle == candles[-2]:  # Doesn't take from the lasts (I think)
            if sum(change_sum) == 0:
                break
            change_sum = [c for c in change_sum if c > 0]  # Delete all 0 numbers
            print(candle.open)
            if candle.open > 100:
                print(token)
            # avg_change = sum(change_sum)/len(change_sum)
        #
        #     if abs(candle.change()) > (avg_change * 10) and candle.volume > 50000:  # Sudden spike
        #         print(candle.ticker)
        #         print("last candle change:", candle.change())
        #         print(avg_change * 10)
        #         print("-------")
        #         alert()
        #     break
        # else:
        #     change_sum.append(abs(candle.change()))


if __name__ == '__main__':
    tokens_list = get_all_tokens()
    # tokens_list = tokens_list[:3]
    # print(tokens_list)
    # time.sleep(42)
    while True:
        s = time.time()
        for coin in tokens_list:
            main1 = threading.Thread(target=main, args=[coin])
            main1.start()
        print("finished_loop")
        time.sleep(60)
        print(s-time.time())
