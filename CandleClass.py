class Candle:
    def __init__(self, ticker, open_p, close, high, low, volume, date):
        self.ticker = ticker
        self.open = open_p
        self.close = close
        self.high = high
        self.low = low
        self.date = date
        self.volume = volume
        self.status = self.get_status()

    def head(self):
        """
        Returns the length of the top wick.
        :return:
        """
        if self.close > self.open:
            return self.high - self.close
        else:
            return self.high - self.open

    def tail(self):
        """
        Returns the length of the bottom wick.
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
        return body * 5 <= self.head() and body * 5 <= self.tail()

    def change(self):
        """
        Returns change from open to close in percent
        :return:
        """
        try:
            return ((self.close/self.open) * 100) - 100
        except ZeroDivisionError:
            return 0

    def is_no_wick(self):
        """
        Returns if the candle has a wick. Also returns true if the wick is small considering to the body.
        :return:
        """
        return self.body() >= (self.head()*5) and self.body() >= (self.tail()*5)

    def get_status(self):
        """
        Returns True if the candle is defined based on volume
        :return:
        """
        return isinstance(self.volume, int) and self.volume > 0
