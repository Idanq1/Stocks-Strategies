import pandas as pd
import numpy as np
import random

data = {"BTCUSDT": pd.DataFrame(
    np.array([[1, 2, 3, 4, 5, True, np.nan], [1, 2, 3, 3, 2, True, np.nan], [3, 5, 2, 5, 1, True, np.nan]]),
    index=[1, 2, 3], columns=["Open", "High", "Close", "Low", "Volume", "Is Closed", "rel_v"])}

# print(data["BTCUSDT"])
# data["BTCUSDT"].drop(index=data["BTCUSDT"].index[0], axis=0, inplace=True)
# print(data["BTCUSDT"])

for i in range(4, 14):
    print(data["BTCUSDT"])
    rel_v = np.nan
    if len(data["BTCUSDT"]) >= 5:
        volumes = data["BTCUSDT"]["Volume"].tolist()
        rel_v = sum(volumes)/len(volumes)
    data["BTCUSDT"].loc[i] = (random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), False, rel_v)
    if len(data["BTCUSDT"]) > 5:
        data["BTCUSDT"].drop(index=data["BTCUSDT"].index[0], axis=0, inplace=True)

# data[symbol].loc[kline_s] = (open_, high, close, low, volume, is_closed, rel_v)
