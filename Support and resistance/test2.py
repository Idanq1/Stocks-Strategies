import time
import finnhub
import datetime
import numpy as np
import pandas as pd
from math import sqrt
import matplotlib.pyplot as plt
import pandas_datareader as web
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression


def pythag(pt1, pt2):
    a_sq = (pt2[0] - pt1[0]) ** 2
    b_sq = (pt2[1] - pt1[1]) ** 2
    return sqrt(a_sq + b_sq)


def regression_ceof(pts):
    X = np.array([pt[0] for pt in pts]).reshape(-1, 1)
    y = np.array([pt[1] for pt in pts])
    model = LinearRegression()
    model.fit(X, y)
    return model.coef_[0], model.intercept_


def local_min_max(pts):
    local_min = []
    local_max = []
    prev_pts = [(0, pts[0]), (1, pts[1])]
    for i in range(1, len(pts) - 1):
        append_to = ''
        if pts[i-1] > pts[i] < pts[i+1]:
            append_to = 'min'
        elif pts[i-1] < pts[i] > pts[i+1]:
            append_to = 'max'
        if append_to:
            if local_min or local_max:
                prev_distance = pythag(prev_pts[0], prev_pts[1]) * 0.5
                curr_distance = pythag(prev_pts[1], (i, pts[i]))
                if curr_distance >= prev_distance:
                    prev_pts[0] = prev_pts[1]
                    prev_pts[1] = (i, pts[i])
                    if append_to == 'min':
                        local_min.append((i, pts[i]))
                    else:
                        local_max.append((i, pts[i]))
            else:
                prev_pts[0] = prev_pts[1]
                prev_pts[1] = (i, pts[i])
                if append_to == 'min':
                    local_min.append((i, pts[i]))
                else:
                    local_max.append((i, pts[i]))
    return local_min, local_max


def get_stock_info(stock, token="c43om8iad3if0j0su4og"):
    # end = int(time.time())
    start_date = "07/01/2021"
    # end_date = "9/2/2021"

    start = int(time.mktime(datetime.datetime.strptime(start_date, '%d/%m/%Y').timetuple()))
    # end = int(time.mktime(datetime.datetime.strptime(end_date, '%d/%m/%Y').timetuple()))
    end = int(time.time())
    finnhub_client = finnhub.Client(api_key=token)

    return finnhub_client.stock_candles(symbol=stock, resolution='D', _from=start, to=end)


symbol = "AEHL"
data = get_stock_info(symbol)

# print(t)
del data["s"]
data["Close"] = data.pop("c")
data["High"] = data.pop("h")
data["Low"] = data.pop("l")
data["Open"] = data.pop("o")
data["Volume"] = data.pop("v")
data["Time"] = data.pop("t")
df = pd.DataFrame(data)
series = df['Close']
series.index = np.arange(series.shape[0])

month_diff = series.shape[0] // 30
if month_diff == 0:
    month_diff = 1

smooth = int(2 * month_diff + 3)

pts = savgol_filter(series, smooth, 3)

local_min, local_max = local_min_max(pts)

local_min_slope, local_min_int = regression_ceof(local_min)
local_max_slope, local_max_int = regression_ceof(local_max)
support = (local_min_slope * np.array(series.index)) + local_min_int
resistance = (local_max_slope * np.array(series.index)) + local_max_int

plt.title(symbol)
plt.xlabel('Days')
plt.ylabel('Prices')
plt.plot(series, label=symbol)
plt.plot(pts, label="Smooth")
plt.plot(support, label='Support', c='r')
plt.plot(resistance, label='Resistance', c='g')
plt.legend()
plt.show()