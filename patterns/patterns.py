from CandleClass import Candle


class Candles:
    def __init__(self, candle1: Candle, candle2: Candle, candle3: Candle, candle4: Candle):
        self.candle1 = candle1  # Current candle
        self.candle2 = candle2  # Previous candle
        self.candle3 = candle3  # Second candle (2 candles ago)
        self.candle4 = candle4  # First candle (3 candles ago)
        self.ticker = self.get_ticker()

    def get_ticker(self):
        return self.candle1.ticker

    def average_volume(self):
        return (self.candle1.volume + self.candle2.volume + self.candle3.volume + self.candle4.volume) / 4

    def is_bullish_engulfing(self):
        """
        Returns if the candles form a bullish engulfing https://candlestick.co.il/bullish-engulfing
        :return bool:
        """
        if (not self.candle2.is_green() and self.candle1.is_green()) and self.candle1.open < self.candle2.close < self.candle2.open < self.candle1.close:
            return True
        return False

    def is_bearish_engulfing(self):
        """
        Returns if the candles form a bearish engulfing https://candlestick.co.il/bearish-engulfing
        :return bool:
        """
        if (self.candle2.is_green() and not self.candle1.is_green()) and (self.candle1.open > self.candle2.close and self.candle1.close < self.candle2.open):
            return True
        return False

    def is_hammer(self):
        """
        Returns if the candle is a hammer
        https://candlestick.co.il/bullish-hammer  first image
        :return bool:
        """
        if self.candle1.tail() >= self.candle1.body() * 2 and self.candle1.head() <= self.candle1.body() * 0.8:
            return True
        return False

    def is_inverted_hammer(self):
        """
        Returns if the candle is a inverted hammer https://candlestick.co.il/inverted-hammer- first image
        Does not consider the trend
        :return bool:
        """
        if self.candle1.head() >= self.candle1.body() * 2 and self.candle1.tail() <= self.candle1.body() * 0.8:
            return True
        return False

    def is_morning_star(self):
        """
        Returns if the candles form a morning DOJI star https://candlestick.co.il/morning-doji-star
        Does not consider the trend
        Bullish
        :return bool:
        """
        if not self.candle3.is_green() and self.candle2.is_doji() and self.candle2.high < self.candle3.low:
            if self.candle3.close < self.candle1.close < self.candle3.open and self.candle1.is_green():
                return True
        return False

    def is_evening_star(self):
        """
        Returns if the candles form an evening DOJI star https://candlestick.co.il/evening-doji-star
        Bearish
        :return bool:
        """
        if self.candle3.is_green() and self.candle2.is_doji() and self.candle2.low > self.candle3.high:
            if self.candle3.open < self.candle1.close < self.candle3.close and not self.candle1.is_green():
                return True
        return False

    def is_piercing_line(self):
        """
        https://candlestick.co.il/piercing-line
        Does not consider the trend
        Bullish
        High reliability
        :return bool:
        """
        if not self.candle3.is_doji():  # To help me figure out if the following candle is bigger then usual
            if not self.candle2.is_green() and self.candle3.change() < (self.candle2.change() * 2):
                if self.candle1.is_green() and self.candle3.change() < (self.candle1.change() * 2):
                    if self.candle1.open < self.candle2.close and self.candle1.close > (self.candle2.open - (self.candle2.body()/2)):
                        return True
        return False

    def is_bullish_kicking(self):
        """
        https://candlestick.co.il/bullish-kicking
        Bullish
        High reliability
        :return bool:
        """
        if not self.candle2.is_green() and self.candle1.is_green():
            if (self.candle2.is_no_wick()) and (self.candle1.is_no_wick()):
                if self.candle1.open > self.candle2.open:
                    if (self.candle2.high + (self.candle2.body()/5)) < self.candle1.open:  # Gap
                        return True
        return False

    def is_three_inside_up(self):
        """
        https://candlestick.co.il/three-inside-up
        Also called confirmed bullish harami
        Bullish
        High reliability
        :return bool:
        """
        if not self.candle3.is_green() and self.candle2.is_green() and self.candle2.open > self.candle3.close and self.candle2.close < self.candle3.open:  # Bullish harami
            if self.candle1.is_green() and self.candle1.close > self.candle2.close:
                return True

    def is_bullish_harami(self):
        """
        https://candlestick.co.il/bullish-harami
        Bullish
        Low reliability
        :return bool:
        """
        if not self.candle2.is_green() and self.candle1.is_green() and self.candle1.open > self.candle2.close and self.candle1.close < self.candle2.open:
            return True
        return False

    def is_three_white_soldiers(self):
        """
        https://candlestick.co.il/three-white-soldiers
        Bullish
        High reliability
        May be a bit off due to the fact that I didn't measure if there's big candles
        :return bool:
        """
        if self.candle1.is_green() and self.candle2.is_green() and self.candle3.is_green():
            if (self.candle1.head() * 5) <= self.candle1.body() and (self.candle2.head() * 5) <= self.candle2.body() and (self.candle3.head() * 5) <= self.candle3.body():
                if self.candle3.open < self.candle2.open and self.candle3.open < self.candle2.close < self.candle3.close:
                    if self.candle2.open < self.candle1.open and self.candle2.open < self.candle1.close < self.candle2.close:
                        return True
        return False

    def is_concealing_babyswallow(self):
        """
        https://candlestick.co.il/concealing-babyswallow
        Bullish
        High reliability
        :return bool:
        """
        if not self.candle1.is_green() and not self.candle2.is_green() and not self.candle3.is_green() and not self.candle4.is_green():
            if self.candle4.is_no_wick() and self.candle3.is_no_wick() and self.candle1.is_no_wick():
                if self.candle2.open < self.candle3.close < self.candle4.close < self.candle3.open < self.candle4.open:
                    if (self.candle2.body()*1.7) <= (self.candle2.head()) and self.candle2.body() >= (self.candle2.tail()*5):  # Only head shadow
                        if self.candle1.open > self.candle2.high > self.candle1.close:
                            return True
        return False

    def is_three_outside_up(self):
        """
        https://candlestick.co.il/three-outside-up
        also called confirmed bullish engulfing
        Bullish
        High reliability
        :return bool:
        """
        if not self.candle3.is_green() and self.candle2.is_green() and self.candle2.open < self.candle3.close < self.candle3.open < self.candle2.close:  # Bullish engulfing
            if self.candle1.is_green() and self.candle1.close > self.candle2.close:
                return True
        return False
