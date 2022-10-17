from binance import ThreadedWebsocketManager
import pandas as pd

api_key = "8AiGAyxlhYQaRpE1s7097hx5sZ12Ogtr8ir9DsyztaD5j24LrI0fEoToDzCI5lle"
api_secret = "VhudTs0HsBVFNdSTghmqfCjUuIXF6rFiXIfROxHIaM71TGgib7NeZ5aOsJUHjI9f"


def stream_data(msg):
    print("AD")
    print(msg)
    print("A")


twm = ThreadedWebsocketManager()
twm.start()

print("Aa")
# twm.start_symbol_miniticker_socket(callback=stream_data, symbol="BTCUSDT")
twm.start_kline_socket(callback=stream_data, symbol="BTCUSDT")
twm.join()
