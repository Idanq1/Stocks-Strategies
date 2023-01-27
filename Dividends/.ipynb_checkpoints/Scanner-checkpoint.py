import yfinance as yf
import datetime as dt

start_date = '1970-01-01'
end_date = dt.datetime.today()

yf.pdr_override()

goog = yf.Ticker("GOOG")

# df = data.DataReader('GOOG', start_date, end_date)

print(goog.fast_info)
print(goog.info)