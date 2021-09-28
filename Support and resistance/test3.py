import time
import finnhub
import datetime
import numpy as np
import pandas as pd
from math import sqrt
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression
import math


def get_stock_info(stock, token="c43om8iad3if0j0su4og"):
    # end = int(time.time())
    start_date = "07/01/2021"
    # end_date = "9/2/2021"
    start_months = 9
    start = int(time.time()) - (start_months * 30 * 24 * 60 * 60)
    # start = int(time.mktime(datetime.datetime.strptime(start_date, '%d/%m/%Y').timetuple()))
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
    return pd.DataFrame(finnub_data)


def local_min_max(pts):
    local_min = []
    local_max = []
    # prev_pts = [(0, pts[0]), (1, pts[1]), (2, pts[2])]
    # days_threshold = 3
    prev_pts = []
    next_pts = []
    for i in range(2, len(pts) - 2):
        # for j in range(1, days_threshold + 1):  # Later for days threshold
        #     prev_pts.append(pts[i-j])  # Later for days threshold
        prev_pts = [pts[i-2], pts[i-1]]
        next_pts = [pts[i+1], pts[i+2]]
        max_prev = max(prev_pts)
        min_prev = min(prev_pts)
        max_next = max(next_pts)
        min_next = min(next_pts)
        pt = pts[i]
        if min_prev > pt < min_next:
            local_min.append((i, pts[i]))
        elif max_prev < pt > max_next:
            local_max.append((i, pts[i]))
    return local_min, local_max


def abs_min_max(local_min, local_max):
    # Max
    max_rd = 0  # Remember day
    max_v = local_max[0][1]
    for pt in local_max:
        day = pt[0]
        val = pt[1]
        if val > max_v:
            max_rd = day
            max_v = val
    abs_max = (max_rd, max_v)

    # Min
    min_rd = 0  # Remember day
    min_v = local_min[0][1]
    for pt in local_min:
        day = pt[0]
        val = pt[1]
        if val < min_v:
            min_rd = day
            min_v = val
    abs_min = (min_rd, min_v)
    return abs_min, abs_max


# def numpy_to_list(local_pts):
#     pts = []
#     for pt in local_pts:
#         pts.append(pt[1])
#     return [x[1] for x in pts]
#     return pts


def threshold_averaged(local_min, local_max, abs_min, abs_max, threshold=2):
    numpy_to_list = lambda pts: [x[1] for x in pts]
    local_min_value = numpy_to_list(local_min)
    local_max_value = numpy_to_list(local_max)

    # Min
    tmp_min_pts = [pt ** (1/threshold) for pt in local_min_value]
    tmp_min_avg = sum(tmp_min_pts) / len(tmp_min_pts)
    support = tmp_min_avg ** threshold

    # Max
    tmp_max_pts = [pt ** threshold for pt in local_max_value]
    tmp_max_avg = sum(tmp_max_pts) / len(tmp_max_pts)
    resistance = tmp_max_avg ** (1 / threshold)
    return support, resistance


def avg_pts(local_min, local_max):
    # Min
    support = [pt[1] for pt in local_min]
    support = sum(support) / len(support)

    # Max
    resistance = [pt[1] for pt in local_max]
    resistance = sum(resistance) / len(resistance)
    return support, resistance


def main():
    symbol = "NVGS"
    df = get_stock_info(symbol)

    series = df['Close']
    series.index = np.arange(series.shape[0])

    month_diff = series.shape[0] // 30
    if month_diff == 0:
        month_diff = 1

    smooth = int(2 * month_diff + 3)
    lines_threshold = 30
    pts = savgol_filter(series, smooth, 3)
    local_min, local_max = local_min_max(pts)
    abs_min, abs_max = abs_min_max(local_min, local_max)
    th_support, th_resistance = threshold_averaged(local_min, local_max, abs_min, abs_max, lines_threshold)
    support, resistance = avg_pts(local_min, local_max)

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
    # print(support)
    # print(resistance)
    plt.title(symbol)
    plt.xlabel('Days')
    plt.ylabel('Prices')
    plt.plot(series, label=symbol)
    plt.scatter(x_min, y_min, c='g', label="min")
    plt.scatter(x_max, y_max, c='r', label="max")
    plt.axhline(th_support, c="g", label="Threshold Support")
    plt.axhline(th_resistance, c="r", label="Threshold Resistance")
    plt.axhline(support, c="m", label="Support")
    plt.axhline(resistance, c="y", label="Resistance")
    plt.plot(pts, label="Smooth")
    plt.legend()
    plt.show()
    # local_min, local_max = local_min_max(pts)

    # support = (local_min_slope * np.array(series.index)) + local_min_int
    # resistance = (local_max_slope * np.array(series.index)) + local_max_int

    # plt.title(symbol)
    # plt.xlabel('Days')
    # plt.ylabel('Prices')
    # plt.plot(series, label=symbol)
    # plt.plot(pts, label="Smooth")
    # plt.plot(support, label='Support', c='r')
    # plt.plot(resistance, label='Resistance', c='g')
    # plt.legend()
    # plt.show()


if __name__ == '__main__':
    main()