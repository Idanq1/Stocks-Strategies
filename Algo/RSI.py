from pandas_datareader import data
import matplotlib.pyplot as plt
import statistics as stats
import pandas as pd


def load_stock_data(stock, start_date, end_date, output_file):
    try:
        df = pd.read_pickle(output_file)
        print('File data found...reading GOOG data')
    except FileNotFoundError:
        print('File not found...downloading the GOOG data')
        df = data.DataReader(stock, 'yahoo', start_date, end_date)
        df.to_pickle(output_file)
    return df


def calc_rsi(close, period=14):
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
    return rsi_values, avg_gain_values, avg_loss_values


def plot_chart(df, close, rsi_values, avg_gain_values, avg_loss_values):
    goog_data = df.assign(ClosePrice=pd.Series(close, index=df.index))
    goog_data = goog_data.assign(RelativeStrengthAvgGainOver20Days=pd.Series(avg_gain_values, index=goog_data.index))
    goog_data = goog_data.assign(RelativeStrengthAvgLossOver20Days=pd.Series(avg_loss_values, index=goog_data.index))
    goog_data = goog_data.assign(RelativeStrengthIndicatorOver20Days=pd.Series(rsi_values, index=goog_data.index))

    close_price = goog_data['ClosePrice']
    rs_gain = goog_data['RelativeStrengthAvgGainOver20Days']
    rs_loss = goog_data['RelativeStrengthAvgLossOver20Days']
    rsi = goog_data['RelativeStrengthIndicatorOver20Days']

    fig = plt.figure()
    ax1 = fig.add_subplot(311, ylabel='Google price in $')
    close_price.plot(ax=ax1, color='black', lw=2., legend=True)
    # ax2 = fig.add_subplot(312, ylabel='RS')
    # rs_gain.plot(ax=ax2, color='g', lw=2., legend=True)
    # rs_loss.plot(ax=ax2, color='r', lw=2., legend=True)
    ax3 = fig.add_subplot(313, ylabel='RSI')
    ax3.axhline(y=50, color='r', linestyle=':', alpha=0.5)
    ax3.axhline(y=30, color='g', linestyle='dashed', alpha=0.8)
    ax3.axhline(y=70, color='g', linestyle='dashed', alpha=0.8)
    rsi.plot(ax=ax3, color='b', lw=2., legend=True)
    plt.show()


def main():
    stock = "TSLA"
    start_date = '2022-01-01'
    end_date = '2023-01-01'

    df = load_stock_data(stock, start_date, end_date, r"data\goog_data.pkl")
    close = df["Close"]
    rsi_values, avg_gain_values, avg_loss_values = calc_rsi(close, 50)
    print(rsi_values)
    plot_chart(df, close, rsi_values, avg_gain_values, avg_loss_values)


if __name__ == '__main__':
    main()
