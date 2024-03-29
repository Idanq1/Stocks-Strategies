class Candle:
    def __init__(self, ticker, open_p, close, high, low, volume, date):
        self.ticker = ticker
        self.open = open_p
        self.close = close
        self.high = high
        self.low = low
        self.date = date
        self.volume = volume

    def head(self):
        """
        Returns the shadow up.
        :return:
        """
        if self.close > self.open:
            return self.high - self.close
        else:
            return self.high - self.open

    def tail(self):
        """
        Returns the shadow down.
        :return:
        """
        if self.close > self.open:
            return self.open - self.low
        else:
            return self.close - self.low

    def body(self):
        """
        Returns the body length.
        :return:
        """
        return abs(self.close - self.open)

    def is_green(self):
        return self.close > self.open

    def is_doji(self):
        """
        Finds if a candle is a doji or close to doji
        :return:
        """
        body = self.body()
        return body * 5 <= self.head() and body * 5 <= self.tail()  # 5 threshold, as bigger the number, the dojier the candle
