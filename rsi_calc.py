import pandas
import numpy as np


def get_average_up(pvs):
    sums = []
    while len(pvs) > 0:
        sums.append(sum(pvs)/len(pvs))
        pvs = pvs[:-1]
    return sum(sums)/len(sums)


def get_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period+ 1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi


candles_c = [1274, 1249, 1245, 1233, 1255, 1251, 1277, 1271, 1219, 1244, 1273, 1289, 1269, 1316, 1346, 1380, 1413]

period = 14
# new_candle_c = candles_c[:period+1]
# new_candle_c = pandas.DataFrame(candles_c)

print(get_rsi(candles_c, period))
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
