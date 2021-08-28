import finnhub
import time
import datetime


# https://tcoil.info/detect-double-bottom-in-stocks-with-python/

def get_stock_info(stock, token="c43om8iad3if0j0su4og"):
    indicator = ["rsi", 14]
    end = int(time.time())
    start_date = "25/3/2021"
    start = int(time.mktime(datetime.datetime.strptime(start_date, '%d/%m/%Y').timetuple()))
    finnhub_client = finnhub.Client(api_key=token)

    return finnhub_client.technical_indicator(symbol=stock, resolution='D', _from=start, to=end, indicator=indicator[0], indicator_fields={"timeperiod": indicator[1]})


def main():
    t = get_stock_info("AEHL")
    print(t)


if __name__ == '__main__':
    main()
