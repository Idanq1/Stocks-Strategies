import pandas
import numpy
import talib

def get_average_up(pvs):
    sums = []
    while len(pvs) > 0:
        sums.append(sum(pvs)/len(pvs))
        pvs = pvs[:-1]
    return sum(sums)/len(sums)


candles_c = [1274, 1249, 1245, 1233, 1255, 1251, 1277, 1271, 1219, 1244, 1273, 1289, 1269, 1316, 1346, 1380, 1413]
period = 16
new_candle_c = candles_c[:period+1]
new_candle_c = pandas.DataFrame(new_candle_c)
print(talib.RSI(new_candle_c))
# dif = []
# for i in range(period):
#     dif.append(((new_candle_c[i+1] - new_candle_c[i])/new_candle_c[i])*100)
# dif = new_candle_c.diff()
# up = dif.clip(lower=0)
# down = dif.clip(upper=-0.0)
# down *= -1
# # print(up)
# # print(down)
#
# ema_up = up.ewm(com=period-1, adjust=False).mean()
# ema_down = down.ewm(com=period-1, adjust=False).mean()
# rs = ema_up/ema_down
# rsi = 100 - (100 / (1+rs))
# print(rsi)
# pv = [p for p in dif if p > 0]
# nv = [abs(n) for n in dif if n < 0]
# apv = sum(pv)/len(pv)
# anv = sum(nv)/len(nv)
# rs = apv/anv
# rsi = 100 - (100 / (1 + rs))
# print(rsi)
