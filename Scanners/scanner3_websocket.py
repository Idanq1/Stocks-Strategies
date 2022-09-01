import websocket
import datetime


def on_message(ws, message):
    print()
    print(str(datetime.datetime.now()) + ": ")
    print(message)


def on_error(ws, error):
    print(error)


def on_close(close_msg):
    print("### closed ###" + close_msg)


def streamKline(currency, interval):
    websocket.enableTrace(False)
    socket = f'wss://stream.binance.com:9443/ws/{currency}@kline_{interval}'
    ws = websocket.WebSocketApp(socket,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()


streamKline('solusdt', '1m')
# streamKline('bnbusdt', '1m')
# streamKline('ethusdt', '1m')
# streamKline('btcusdt', '1m')
# streamKline('shibusdt', '1m')
# streamKline('adausdt', '1m')
