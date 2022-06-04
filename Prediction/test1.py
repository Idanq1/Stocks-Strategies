from tensorflow.keras.layers import Conv2D, MaxPool2D, Dense, Flatten, Dropout, LSTM, BatchNormalization
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from datetime import datetime
from binance import Client
import tensorflow as tf
import pandas as pd
import numpy as np
import random
import time

api_key = "8AiGAyxlhYQaRpE1s7097hx5sZ12Ogtr8ir9DsyztaD5j24LrI0fEoToDzCI5lle"
api_secret = "VhudTs0HsBVFNdSTghmqfCjUuIXF6rFiXIfROxHIaM71TGgib7NeZ5aOsJUHjI9f"
client = Client(api_key, api_secret)


def get_all_tokens(currency="USDT"):
    res = client.get_all_tickers()
    tokens = []
    for token in res:
        if currency in token["symbol"]:
            tokens.append(token["symbol"])
    return tokens


def get_historical_data(token, interval, start, end=None):
    candles_data = client.get_historical_klines(token, interval, start, end)  # OHLC
    for candle in candles_data:
        # timestamp = candle[0] / 1000
        # date_time = datetime.fromtimestamp(float(timestamp))
        # candle[0] = date_time.strftime("%d/%m/%Y")
        del candle[5:12]
    df = pd.DataFrame.from_records(candles_data)
    return df


def format_data(df, length):
    data = []
    labels = []
    df_len = df.shape[0]
    for i in range(df_len - length):
        # part_df = df.iloc[i + length]
        part_df = df[i: i+length]
        is_up = 1 if (float(df.iloc[i + length].iloc[4]) > float(df.iloc[i + length].iloc[1])) else 0
        data.append(part_df)
        labels.append(is_up)

    # Shuffles same order
    tmp = list(zip(data, labels))
    random.shuffle(tmp)
    data, labels = zip(*tmp)
    data = np.array(data).astype(float)
    labels = np.array(labels)
    return train_test_split(data, labels, test_size=0.1, random_state=42)


def train_model(x_train, x_test, y_train, y_test, epochs=60, batch=64):
    model = Sequential()
    model.add(LSTM(128, input_shape=(x_train.shape[1:]), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(LSTM(128, return_sequences=True))
    model.add(Dropout(0.1))
    model.add(BatchNormalization())

    model.add(LSTM(128))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))

    model.add(Dense(2, activation='softmax'))

    opt = tf.keras.optimizers.Adam(lr=0.001, decay=1e-6)

    model.compile(loss="sparse_categorical_crossentropy", optimizer=opt, metrics=["accuracy"])

    history = model.fit(
        x_train, y_train,
        batch_size=batch,
        epochs=epochs,
        validation_data=(x_test, y_test)
    )
    model.save(r"model1")
    score = model.evaluate(x_test, y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])


def main():
    epochs = 60
    batch = 64
    length = 10
    coins = get_all_tokens()
    dfs = None

    for coin in coins:
        print(f"{coins.index(coin)}/{len(coins)}")
        df = get_historical_data(coin, "1d", 0)
        if dfs is None:
            dfs = df
        else:
            dfs = pd.concat([dfs, df], ignore_index=True)
        print(dfs.shape)

    x_train, x_test, y_train, y_test = format_data(dfs, length)
    train_model(x_train, x_test, y_train, y_test, epochs, batch)


if __name__ == '__main__':
    s = time.time()
    main()
    print(time.time() - s)
