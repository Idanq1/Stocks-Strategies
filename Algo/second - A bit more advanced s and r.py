from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

start_date = '2014-01-01'
end_date = '2018-01-01'
SRC_DATA_FILENAME = 'goog_data.pkl'

try:
    goog_data = pd.read_pickle(SRC_DATA_FILENAME)
except FileNotFoundError:
    goog_data = data.DataReader('GOOG', 'yahoo', start_date, end_date)
    goog_data.to_pickle(SRC_DATA_FILENAME)

goog_data_signal = pd.DataFrame(index=goog_data.index)
goog_data_signal['price'] = goog_data['Adj Close']


def trading_support_resistance(data, bin_width=20):
    data['sup_tolerance'] = pd.Series(np.zeros(len(data)))
    data['res_tolerance'] = pd.Series(np.zeros(len(data)))
    data['sup_count'] = pd.Series(np.zeros(len(data)))
    data['res_count'] = pd.Series(np.zeros(len(data)))
    data['sup'] = pd.Series(np.zeros(len(data)))
    data['res'] = pd.Series(np.zeros(len(data)))
    data['positions'] = pd.Series(np.zeros(len(data)))
    data['signal'] = pd.Series(np.zeros(len(data)))
    in_support = 0
    in_resistance = 0

    for x in range((bin_width - 1) + bin_width, len(data)):
        data_section = data[x - bin_width:x + 1]
        support_level = min(data_section['price'])
        resistance_level = max(data_section['price'])
        range_level = resistance_level - support_level
        data['res'][x] = resistance_level
        data['sup'][x] = support_level
        data['sup_tolerance'][x] = support_level + 0.2 * range_level
        data['res_tolerance'][x] = resistance_level - 0.2 * range_level
        if data['res_tolerance'][x] <= data['price'][x] <= data['res'][x]:
            in_resistance += 1
            data['res_count'][x] = in_resistance
        elif data['sup_tolerance'][x] >= data['price'][x] >= data['sup'][x]:
            in_support += 1
            data['sup_count'][x] = in_support
        else:
            in_support = 0
            in_resistance = 0
        if in_resistance > 2:
            data['signal'][x] = 1
        elif in_support > 2:
            data['signal'][x] = 0
        else:
            data['signal'][x] = data['signal'][x - 1]
    data['positions'] = data['signal'].diff()


trading_support_resistance(goog_data_signal)

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Google price in $')
goog_data_signal['sup'].plot(ax=ax1, color='g', lw=2.)
goog_data_signal['res'].plot(ax=ax1, color='b', lw=2.)
goog_data_signal['price'].plot(ax=ax1, color='r', lw=2.)
ax1.plot(goog_data_signal.loc[goog_data_signal.positions == 1.0].index, goog_data_signal.price[goog_data_signal.positions == 1.0], '^', markersize=7, color='k', label='buy')
ax1.plot(goog_data_signal.loc[goog_data_signal.positions == -1.0].index, goog_data_signal.price[goog_data_signal.positions == -1.0], 'v', markersize=7, color='k', label='sell')
plt.legend()
plt.show()
