from sklearn.model_selection import train_test_split
from pandas_datareader import data
from sklearn import linear_model
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def load_financial_data(start_date, end_date, output_file):
    try:
        df = pd.read_pickle(output_file)
        print('File data found...reading GOOG data')
    except FileNotFoundError:
        print('File not found...downloading the GOOG data')
        df = data.DataReader('GOOG', 'yahoo', start_date, end_date)
        df.to_pickle(output_file)
    return df


def create_classification_trading_condition(df):
    df['Open-Close'] = df.Open - df.Close
    df['High-Low'] = df.High - df.Low
    df = df.dropna()
    x = df[['Open-Close', 'High-Low']]
    y = np.where(df['Close'].shift(-1) > df['Close'], 1, -1)
    return x, y


def create_regression_trading_condition(df):
    df['Open-Close'] = df.Open - df.Close
    df['High-Low'] = df.High - df.Low
    df = df.dropna()
    x = df[['Open-Close', 'High-Low']]
    y = df['Close'].shift(-1) - df['Close']
    df["Target"] = y
    return df, x, y


def calculate_return(df, split_value, symbol):
    cum_goog_return = df[split_value:]['%s_Returns' % symbol].cumsum() * 100
    df['Strategy_Returns'] = df['%s_Returns' % symbol] * df['Predicted_Signal'].shift(1)
    return cum_goog_return


def calculate_strategy_return(df, split_value, symbol):
    cum_strategy_return = df[split_value:]['Strategy_Returns'].cumsum() * 100
    return cum_strategy_return


def plot_chart(cum_symbol_return, cum_strategy_return, symbol):
    plt.figure(figsize=(10, 5))
    plt.plot(cum_symbol_return, label='%s Returns' % symbol)
    plt.plot(cum_strategy_return, label='Strategy Returns')
    plt.legend()
    plt.show()


def sharpe_ratio(symbol_returns, strategy_returns):
    strategy_std = strategy_returns.std()
    sharpe = (strategy_returns - symbol_returns) / strategy_std
    return sharpe.mean()


def main():
    goog_data = load_financial_data(start_date='2001-01-01', end_date='2022-01-01', output_file='goog_data_large.pkl')
    goog_data, x, y = create_regression_trading_condition(goog_data)
    x_train, x_test, y_train, y_test = train_test_split(x, y, shuffle=False, train_size=0.9)

    # pd.plotting.scatter_matrix(goog_data[['Open-Close', 'High-Low', 'Target']], grid=True, diagonal='kde')
    # plt.show()
    ols = linear_model.LinearRegression()
    ols.fit(x_train, y_train)
    print('Coefficients: \n', ols.coef_)

    # Visualize returns
    goog_data['Predicted_Signal'] = ols.predict(x)
    goog_data['GOOG_Returns'] = np.log(goog_data['Close'] / goog_data['Close'].shift(1))

    cum_goog_return = calculate_return(goog_data, split_value=len(x_train), symbol='GOOG')
    cum_strategy_return = calculate_strategy_return(goog_data, split_value=len(x_train), symbol='GOOG')
    plot_chart(cum_goog_return, cum_strategy_return, symbol='GOOG')
    print(sharpe_ratio(cum_strategy_return, cum_goog_return))


if __name__ == '__main__':
    main()
