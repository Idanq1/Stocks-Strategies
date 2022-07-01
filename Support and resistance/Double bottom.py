import os
import time
import finnhub
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter


def get_stock_info(stock, start_months):
    finnub_data = {"s": "no_data"}  # Just so the stupid error will go away
    start = int(time.time()) - (start_months * 30 * 24 * 60 * 60)
    end = int(time.time())
    finnhub_client = finnhub.Client(api_key=current_token)
    try:
        finnub_data = finnhub_client.stock_candles(symbol=stock, resolution='D', _from=start, to=end)
    except Exception as e:
        try:
            exception_status = e.status_code
        except AttributeError:
            return False
        if exception_status == 429:
            change_token()
            get_stock_info(stock, start_months)
        else:
            # print(e)
            # print(exception_status)
            return False
    if finnub_data["s"] == "no_data":
        return False
    del finnub_data["s"]
    finnub_data["Close"] = finnub_data.pop("c")
    finnub_data["High"] = finnub_data.pop("h")
    finnub_data["Low"] = finnub_data.pop("l")
    finnub_data["Open"] = finnub_data.pop("o")
    finnub_data["Volume"] = finnub_data.pop("v")
    finnub_data["Time"] = finnub_data.pop("t")
    return pd.DataFrame(finnub_data)


def change_token():
    global current_token
    token_index = tokens.index(current_token)
    if token_index >= len(tokens) - 1:
        current_token = tokens[0]
    else:
        current_token = tokens[token_index + 1]


def get_tickers():
    all_tickers = []
    with open(r"..\nasdaqtraded.txt", 'r') as f:
        stock_list = f.readlines()

    for symbol in stock_list:  # 700
        stock_ticker = symbol.split("|")[1]
        if stock_ticker == "Symbol":
            continue
        if "$" in stock_ticker:
            continue
        if stock_ticker == "":
            continue
        all_tickers.append(stock_ticker)
    return all_tickers


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
        if min_prev >= pt < min_next:
            local_min.append((i, pts[i]))
        elif max_prev <= pt > max_next:
            local_max.append((i, pts[i]))
    return local_min, local_max


def avg_pts(local_min, local_max):
    # Min
    avg_min = [pt[1] for pt in local_min]
    avg_min = sum(avg_min) / len(avg_min)

    # Max
    avg_max = [pt[1] for pt in local_max]
    avg_max = sum(avg_max) / len(avg_max)
    return avg_min, avg_max


def is_double_bottom(local_min, current_price, prcnt_between_points, dis_btwn_pts):
    # Calculate % between local mins
    # pts = [pt[1] for pt in local_min]
    for pt1 in local_min:
        day1 = pt1[0]
        price1 = pt1[1]
        prc_price = abs(calc_prcnt(price1, current_price))
        if prc_price >= 4:  # Double bottom line less than 4% from the current price
            continue
        for pt2 in local_min:
            day2 = pt2[0]
            price2 = pt2[1]

            if day1 == day2:
                continue
            if abs(day1-day2) <= dis_btwn_pts:
                continue
            prc_pts = calc_prcnt(price1, price2)
            if abs(prc_pts) >= prcnt_between_points:
                continue
            return (pt1, pt2), (price1+price2)/2  # pts, double bottom line
    return False
    # for i in range(1, len(pts)):
    #     pt = pts[i]
    #     prev_pt = pts[i-1]
    #     prc_pts = calc_prcnt(pt, prev_pt)
    #     prc_price = calc_prcnt(pt, current_price)  # Distance current price from double bottom line
    #     if abs(prc_pts) <= prcnt_between_points:
    #         if abs(prc_price) <= 4:  # Double bottom line less than 4% from the current price
    #             return True
    # return False


def abs_min(local_min):  # Absolute min
    # Min
    min_rd = 0  # Remember day
    min_v = local_min[0][1]
    for pt in local_min:
        day = pt[0]
        val = pt[1]
        if val < min_v:
            min_rd = day
            min_v = val
    return min_rd, min_v


def calc_prcnt(var1, var2):
    return ((var1/var2)*100)-100


def main(symbol, start_month, find_by, threshold_pts, prcnt_between_points, volume_threshold, dis_btwn_pts, dis_db_bottom):
    df = get_stock_info(symbol, start_month)
    if df is False:
        return

    v_avg = sum(df["Volume"].values) / len(df["Volume"].values)
    if v_avg < volume_threshold:
        return

    series = df[find_by]
    series.index = np.arange(series.shape[0])

    atl = min(series.values)

    # Smooth
    month_diff = series.shape[0] // 30
    if month_diff == 0:
        month_diff = 1
    smooth = int(2 * month_diff + 3)
    try:
        pts = savgol_filter(series, smooth, 3)
    except ValueError:
        # print(f"CRASHED: {symbol}")
        return

    current_price = pts[-1]
    local_min, local_max = local_min_max(pts, threshold_pts)

    if len(local_min) == 0 or len(local_max) == 0:
        return
    db = is_double_bottom(local_min, current_price, prcnt_between_points, dis_btwn_pts)
    if not db:  # Didn't find DB
        return
    db_line = db[1]
    pt1 = db[0][0]
    pt2 = db[0][1]
    # print(pt1)
    if abs(calc_prcnt(db_line, atl)) >= dis_db_bottom:  # Distance double bottom line from all time low
        return

    abs_min_py = abs_min(local_min)
    support, resistance = avg_pts(local_min, local_max)

    if abs(calc_prcnt(abs_min_py[1], support)) > 10:
        return

    dif_lines = calc_prcnt(support, resistance)
    if abs(dif_lines) <= 10:  # Percent difference between support and resistance
        return

    print(symbol, round(support, 2))

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
    # plt.scatter(x_min, y_min, c='g')
    # plt.scatter(x_max, y_max, c='r')
    plt.scatter(pt2[0], pt2[1], c="m")
    plt.scatter(pt1[0], pt1[1], c="m")
    plt.axhline(db_line, c="r", label="Double bottom line")
    plt.plot(pts, label="Smooth")
    plt.legend()

    date = datetime.datetime.now().strftime("%Y_%m_%d")
    if "Results" not in os.listdir():
        os.mkdir("Results")
    if date not in os.listdir("Results"):
        os.mkdir(f"Results\\{date}")
    plt.savefig(f"Results\\{date}\\{symbol}.jpg", dpi=1200)
    plt.clf()


if __name__ == '__main__':
    # date = datetime.datetime.now().strftime("%Y_%m_%d")
    tokens = ["c43om8iad3if0j0su4og", "c43baq2ad3iaavqonarg", "c437gqqad3iaavqojj0g", "c43f8kiad3if0j0skdvg", "c43opbaad3if0j0su7bg", "c43oqsaad3if0j0su8b0", "c43ordiad3if0j0su8sg", "c43oseqad3if0j0su9e0", "c43ossiad3if0j0su9pg", "c43otbqad3if0j0sua3g"]
    current_token = tokens[0]

    months_back = 5
    volume_thrs = 10000  # Minimum average volume in the given time
    fnd_by = "Low"  # Open, Low, Close, High
    percent_pts_threshold = 2  # Percents between minima points to qualify as double bottom
    threshold_days = 5  # How many days can count as a minima/maxima noise and ignore it
    dis_between_min_pts = 10  # Distance in days between local minima points
    db_dis_bottom = 30  # Double bottom line distance from the all-time-low
    stocks = get_tickers()
    s = time.time()
    for stock in stocks:
        main(stock, months_back, fnd_by, threshold_days, percent_pts_threshold, volume_thrs, dis_between_min_pts, db_dis_bottom)
    print(time.time() - s)

