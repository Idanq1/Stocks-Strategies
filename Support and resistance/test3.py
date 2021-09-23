import time
import finnhub
import datetime
import numpy as np
import pandas as pd
from math import sqrt
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression


def get_stock_info(stock, token="c43om8iad3if0j0su4og"):
    # end = int(time.time())
    start_date = "07/01/2021"
    # end_date = "9/2/2021"

    start = int(time.mktime(datetime.datetime.strptime(start_date, '%d/%m/%Y').timetuple()))
    # end = int(time.mktime(datetime.datetime.strptime(end_date, '%d/%m/%Y').timetuple()))
    end = int(time.time())
    finnhub_client = finnhub.Client(api_key=token)
    finnub_data = finnhub_client.stock_candles(symbol=stock, resolution='D', _from=start, to=end)
    del finnub_data["s"]
    finnub_data["Close"] = finnub_data.pop("c")
    finnub_data["High"] = finnub_data.pop("h")
    finnub_data["Low"] = finnub_data.pop("l")
    finnub_data["Open"] = finnub_data.pop("o")
    finnub_data["Volume"] = finnub_data.pop("v")
    finnub_data["Time"] = finnub_data.pop("t")
    df = pd.DataFrame(finnub_data)
    series = df['Close']
    series.index = np.arange(series.shape[0])




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