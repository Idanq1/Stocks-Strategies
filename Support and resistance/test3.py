import time
import finnhub
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter


def get_stock_info(stock, start_months, token="c43om8iad3if0j0su4og"):
    start = int(time.time()) - (start_months * 30 * 24 * 60 * 60)
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


def local_min_max(pts, days_threshold):
    local_min = []
    local_max = []
    for i in range(days_threshold, len(pts) - days_threshold):
        prev_pts = []
        next_pts = []
        for j in range(1, days_threshold + 1):
            prev_pts.append(pts[i-j])
            next_pts.append(pts[i+j])
        max_prev = max(prev_pts)
        min_prev = min(prev_pts)
        max_next = max(next_pts)
        min_next = min(next_pts)
        pt = pts[i]
        if min_prev >= pt <= min_next:
            local_min.append((i, pt))
        elif max_prev <= pt >= max_next:
            local_max.append((i, pt))
    return local_min, local_max


def abs_min_max(local_min, local_max):  # Absolute min/max
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


def main(symbol, start_month, find_by, threshold_pts):
    df = get_stock_info(symbol, start_month)

    series = df[find_by]
    series.index = np.arange(series.shape[0])

    month_diff = series.shape[0] // 30
    if month_diff == 0:
        month_diff = 1

    smooth = int(2 * month_diff + 3)
    lines_threshold = 100
    pts = savgol_filter(series, smooth, 2)
    local_min, local_max = local_min_max(pts, threshold_pts)
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

    plt.title(symbol)
    plt.xlabel('Days')
    plt.ylabel('Prices')
    plt.plot(series, label=symbol)
    plt.scatter(x_min, y_min, c='g')
    plt.scatter(x_max, y_max, c='r')
    plt.axhline(th_support, c="g", label="Threshold Support")
    plt.axhline(th_resistance, c="r", label="Threshold Resistance")
    plt.axhline(support, c="m", label="Support")
    plt.axhline(resistance, c="y", label="Resistance")
    plt.plot(pts, label="Smooth")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    sym = "YVR"
    months_back = 3
    fnd_by = "Close"
    threshold_days = 2  # How many days can count as a minima/maxima noise and ignore it
    main(sym, months_back, fnd_by, threshold_days)
