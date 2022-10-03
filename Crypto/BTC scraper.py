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

