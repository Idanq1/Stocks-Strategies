from CandleClass import Candle


def is_bullish_engulfing(candle1: Candle, candle2: Candle):
    """
    Returns if the candles form a bullish engulfing
    :param candle1: Previous candle
    :param candle2: Current candle
    :return:
    """
    if (not candle1.is_green() and candle2.is_green()) and (candle2.open > candle1.high and candle2.close < candle1.low):
        return True
    return False
