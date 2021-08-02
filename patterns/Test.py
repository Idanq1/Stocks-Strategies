import finnhub
import datetime
import time
period = 4
start_time = datetime.datetime.now() - datetime.timedelta(days=period)
finnhub_client = finnhub.Client(api_key="c43oqsaad3if0j0su8b0")
ticker = "BBWI.V"
interval = "D"
try:
    candles_data = finnhub_client.stock_candles(ticker, interval, int(start_time.timestamp()), int(time.time()))
    print(candles_data)
except Exception as e:

    print(e.status_code)  # 429
