import time
import math
import finnhub
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression


# https://tcoil.info/detect-double-bottom-in-stocks-with-python/
# https://python.plainenglish.io/estimate-support-and-resistance-of-a-stock-with-python-beginner-algorithm-f1ae1508b66d


def get_stock_info(stock, token="c43om8iad3if0j0su4og"):
    # end = int(time.time())
    start_date = "8/7/2020"
    # end_date = "9/2/2021"
    start_months = 6
    start = int(time.time()) - (start_months * 30 * 24 * 60 * 60)
    # start = int(time.mktime(datetime.datetime.strptime(start_date, '%d/%m/%Y').timetuple()))
    # end = int(time.mktime(datetime.datetime.strptime(end_date, '%d/%m/%Y').timetuple()))
    end = int(time.time())
    finnhub_client = finnhub.Client(api_key=token)

    return finnhub_client.stock_candles(symbol=stock, resolution='D', _from=start, to=end)


def pythag(pt1, pt2):
    a_sq = (pt2[0] - pt1[0]) ** 2
    b_sq = (pt2[1] - pt1[1]) ** 2
    return math.sqrt(a_sq + b_sq)


def local_min_max(pts):
    local_min = []
    local_max = []
    prev_pts = [(0, pts[0]), (1, pts[1])]
    for i in range(1, len(pts) - 1):
        append_to = ''
        if pts[i - 1] > pts[i] < pts[i + 1]:
            append_to = 'min'
        elif pts[i - 1] < pts[i] > pts[i + 1]:
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


def regression_ceof(pts):
    x = np.array([pt[0] for pt in pts]).reshape(-1, 1)
    y = np.array([pt[1] for pt in pts])
    model = LinearRegression()
    model.fit(x, y)
    return model.coef_[0], model.intercept_


def main():
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
    print(df)
    close = df["Low"]
    days = close.shape[0]  # Number of days
    month_diff = days // 30
    if month_diff == 0:  # We want it bigger than 0
        month_diff = 1
    smooth = int(2 * month_diff + 3)  # Simple algo to determine smoothness  I have no idea how it works
    pts = savgol_filter(close, smooth, 3)
    local_min, local_max = local_min_max(pts)
    x_min = []
    x_max = []
    y_min = []
    y_max = []
    for min_point in local_min:
        x_min.append(min_point[0])
        y_min.append(min_point[1])
    for max_point in local_max:
        x_max.append(max_point[0])
        y_max.append(max_point[1])

    local_min_slope, local_min_int = regression_ceof(local_min)
    local_max_slope, local_max_int = regression_ceof(local_max)

    support = (local_min_slope * np.array(close.index)) + local_min_int
    resistance = (local_max_slope * np.array(close.index)) + local_max_int

    # plotting
    plt.title(symbol)
    plt.xlabel("Days")
    plt.ylabel("Prices")
    plt.plot(pts, label=f"Smooth {symbol}")
    plt.plot(support, label="Support", c="r")
    plt.plot(resistance, label="Resistance", c="g")
    plt.scatter(x_min, y_min)
    plt.scatter(x_max, y_max)
    plt.legend()
    plt.show()
    # STEP 4


if __name__ == '__main__':
    main()
