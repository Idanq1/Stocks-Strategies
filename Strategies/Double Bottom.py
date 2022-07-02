from scipy.signal import savgol_filter
from pandas_datareader import data
import matplotlib.pyplot as plt
import statistics as stats
import pandas as pd
import numpy as np


def load_stock_data(stock, start_date, end_date="2025-12-12"):
    df = data.DataReader(stock, 'yahoo', start_date, end_date)
    return df


def calc_rsi(df, period=14):
    close = df["Close"]
    gain_history = []  # history of gains overlook back period (0 if no gain, magnitude of gain if gain)
    loss_history = []  # history of losses overlook back period (0 if no loss, magnitude of loss if loss)
    avg_gain_values = []  # track avg gains for visualization purposes
    avg_loss_values = []  # track avg losses for visualization purposes
    rsi_values = []  # track computed RSI values
    last_price = 0  # current_price - last_price > 0 => gain. current_price -last_price < 0 => loss.
    for close_price in close:
        if last_price == 0:
            last_price = close_price

        gain_history.append(max(0, close_price - last_price))
        loss_history.append(max(0, last_price - close_price))
        last_price = close_price

        if len(gain_history) > period:  # maximum observations is equal to lookback period
            del (gain_history[0])
            del (loss_history[0])

        avg_gain = stats.mean(gain_history)  # average gain over lookback period
        avg_loss = stats.mean(loss_history)  # average loss over lookback period
        avg_gain_values.append(avg_gain)
        avg_loss_values.append(avg_loss)

        rs = 0
        if avg_loss > 0:  # to avoid division by 0, which is undefined
            rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)
    df = df.assign(RSI=pd.Series(rsi_values, index=df.index))
    return df


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


def double_bottom_main(df, threshold_pts=5, prcnt_between_points=2, dis_btwn_pts=10, dis_db_bottom=30, volume_threshold=10000, find_by="Adj Close"):
    v_avg = sum(df["Volume"].values) / len(df["Volume"].values)
    if v_avg < volume_threshold:
        return
    series = df[find_by]
    # series.index = np.arange(series.shape[0])

    atl = min(df[find_by])

    # Smooth
    month_diff = len(df.index) // 30
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
        print("A")
        return
    db_line = db[1]
    # pt1 = db[0][0]
    # pt2 = db[0][1]
    # print(pt1)
    if abs(calc_prcnt(db_line, atl)) >= dis_db_bottom:  # Distance double bottom line from all time low
        print("B")
        return

    abs_min_py = abs_min(local_min)
    support, resistance = avg_pts(local_min, local_max)

    if abs(calc_prcnt(abs_min_py[1], support)) > 10:
        print("C")
        return

    dif_lines = calc_prcnt(support, resistance)
    if abs(dif_lines) <= 10:  # Percent difference between support and resistance
        print("D")
        return

    print(round(db_line, 2))
    # print(round(resistance, 2))


def main():
    stock = "ACIW"
    start_date = '2022-02-02'
    end_date = '2023-01-01'

    df = load_stock_data(stock, start_date, end_date)
    df = calc_rsi(df, 14)
    double_bottom_main(df)


if __name__ == '__main__':
    main()
