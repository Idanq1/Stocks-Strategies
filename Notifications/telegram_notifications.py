from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from telegram import Update
import telegram
from binance import Client
import json
import time


def get_ticker_price(ticker, coin=False):
    if ticker and not coin:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?region=US&lang=en-US&includePrePost=false&interval=1m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        res = requests.get(url, headers=headers)
        data = json.loads(res.text)
        try:
            return float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])
        except TypeError:
            return False
    elif ticker and coin:
        b_api_key = "8AiGAyxlhYQaRpE1s7097hx5sZ12Ogtr8ir9DsyztaD5j24LrI0fEoToDzCI5lle"
        b_api_secret = "VhudTs0HsBVFNdSTghmqfCjUuIXF6rFiXIfROxHIaM71TGgib7NeZ5aOsJUHjI9f"
        client = Client(b_api_key, b_api_secret)
        res = client.get_all_tickers()
        if isinstance(ticker, str):
            for c_ticker in res:
                if ticker == c_ticker["symbol"]:
                    return c_ticker["price"]
            return False
        elif isinstance(ticker, list):
            tickers_prices = {}
            for c_ticker in res:
                if c_ticker["symbol"] in ticker:
                    tickers_prices[c_ticker["symbol"]] = c_ticker["price"]
            return tickers_prices


def start(update, ctx):
    txt = "/alert- Make a new alert.\n" \
          "/delete- Delete an alert.\n" \
          "/alerts- List of all alerts."
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=txt)


def echo(update: Update, ctx: CallbackContext):
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=" ".join(ctx.args))


def stock_price(update: Update, ctx: CallbackContext):
    ticker = ctx.args[0]
    ticker_price = get_ticker_price(ticker, True)
    if ticker_price:
        text = str(ticker_price)
    else:
        try:
            text = str(round(get_ticker_price(ticker, False), 2))
        except IndexError:
            text = "Couldn't find that instrument."
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=text)


def alert(update: Update, ctx: CallbackContext):
    json_path = r"alerts.json"
    coin = False
    user_id = str(update.effective_user.id)
    if len(ctx.args) != 3:
        ctx.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /alert [coin/stock] [ticker] [alert price]")
        return
    elif ctx.args[0].lower() == "coin":
        coin = True
    stock_or_coin = ["coin" if coin else "stock"][0]
    ticker = ctx.args[1].upper()
    alert_p = float(ctx.args[2])
    tmp_price = get_ticker_price(ticker, coin)
    if not tmp_price:
        ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"Couldn't find that {stock_or_coin}.")
        return
    if tmp_price > alert_p:
        alert_status = "b"  # Alert below
    else:
        alert_status = "a"  # Alert above
    with open(json_path, 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            data = {}

    if ticker not in data:
        data[ticker] = {"coin": coin, "users": {}}
    if user_id not in data[ticker]["users"]:
        data[ticker]["users"][user_id] = {}
    data[ticker]["users"][user_id][alert_p] = alert_status

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

        ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"Made an alert for {ticker} at ${alert_p}")


def alert_user(user, ticker, price):
    bot.send_message(chat_id=user, text=f"<b>{ticker}</b> has reached the price of <b>{price}</b>", parse_mode=telegram.ParseMode.HTML)


def my_id(update: Update, ctx: CallbackContext):
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_user.id)


def check_alerts():
    json_path = r"alerts.json"
    with open(json_path, 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            return
    all_coins = []
    for ticker in data:
        if data[ticker]["coin"]:
            all_coins.append(ticker)
    if all_coins:
        coins_prices = get_ticker_price(all_coins, coin=True)
        for ticker in data:
            is_c = data[ticker]["coin"]
            if is_c:
                ticker_p = float(coins_prices[ticker])
                # noinspection DuplicatedCode
                for user in data[ticker]["users"]:
                    for alert_p in data[ticker]["users"][user]:
                        alert_s = data[ticker]["users"][user][alert_p]
                        if (alert_s == "b" and float(alert_p) > ticker_p) or (alert_s == "a" and float(alert_p) < ticker_p):
                            alert_user(user, ticker, alert_p)
                            delete_alert(ticker, user, alert_p)
    for ticker in data:
        if not data[ticker]["coin"]:
            ticker_p = get_ticker_price(ticker, False)
            # noinspection DuplicatedCode
            for user in data[ticker]["users"]:
                for alert_p in data[ticker]["users"][user]:
                    alert_s = data[ticker]["users"][user][alert_p]
                    if (alert_s == "b" and float(alert_p) > ticker_p) or (alert_s == "a" and float(alert_p) < ticker_p):
                        alert_user(user, ticker, alert_p)
                        delete_alert(ticker, user, alert_p)


def delete_alert(ticker, user, alert_p):
    json_path = r"alerts.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
        del data[ticker]["users"][user][alert_p]
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)


def my_alerts(update: Update, ctx: CallbackContext):
    json_path = r"alerts.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
    txt = ""
    i = 1
    user_id = str(update.effective_user.id)
    for ticker in data:
        for user in data[ticker]["users"]:
            if user != user_id:
                continue
            for alert_p in data[ticker]["users"][user]:
                if not alert_p:
                    continue
                txt += f"{i}. {ticker}- ${alert_p}\n"
                i += 1

    if not txt:
        txt = "You don't have any alerts. To create a new alert use /alert"
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=txt)


def delete_a(update: Update, ctx: CallbackContext):
    to_delete = int(ctx.args[0])
    json_path = r"alerts.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
    user_id = str(update.effective_user.id)
    i = 1
    for ticker in data:
        for user in data[ticker]["users"]:
            if user != user_id:
                continue
            for alert_p in data[ticker]["users"][user]:
                if not alert_p:
                    continue
                if i == to_delete:
                    delete_alert(ticker, user_id, alert_p)
                    ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"Successfully deleted {ticker}'s alert at ${alert_p}")
                    return
                i += 1
    ctx.bot.send_message(chat_id=update.effective_chat.id, text="Couldn't find that alert, try /alerts to see all alerts")


def delete_ticker(ticker):
    json_path = r"alerts.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
    del data[ticker]
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)


def check_empty_stock():
    json_path = r"alerts.json"
    with open(json_path, 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            return
    for ticker in data:
        empty_ticker = True
        for user in data[ticker]["users"]:
            if data[ticker]["users"][user]:
                empty_ticker = False
        if empty_ticker:
            delete_ticker(ticker)


def change_sleep(update: Update, ctx: CallbackContext):
    global sleep_time
    sleep_time = int(ctx.args[0])
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"Changed sleep time to {ctx.args[0]}")


def main():
    bot_token = "1871537273:AAFGJOKn5tPb92BZ1E20JpHnJGFfA7to4WA"
    updater = Updater(token=bot_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('echo', echo))
    dp.add_handler(CommandHandler('price', stock_price))
    dp.add_handler(CommandHandler('id', my_id))
    dp.add_handler(CommandHandler("alert", alert))
    dp.add_handler(CommandHandler("alerts", my_alerts))
    dp.add_handler(CommandHandler("delete", delete_a))
    dp.add_handler(CommandHandler("sleep", change_sleep))
    updater.start_polling()
    while True:
        check_empty_stock()
        check_alerts()
        time.sleep(sleep_time)


if __name__ == '__main__':
    token = "1871537273:AAFGJOKn5tPb92BZ1E20JpHnJGFfA7to4WA"
    bot = telegram.Bot(token=token)
    sleep_time = 2
    main()
