from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update
import telegram
from binance import Client
import yfinance as yf
import datetime
import json
import time


def get_ticker_price(ticker, coin=False):
    if ticker and not coin:
        print("Does not work for now.")
        start_t = datetime.datetime.fromtimestamp(time.time() - 120)
        end_t = datetime.datetime.fromtimestamp(time.time())
        data = yf.download(ticker, start=start_t, end=end_t, progress=False, show_errors=False, group_by="ticker")
        for dat in data:
            print(dat)
    elif ticker and coin:
        b_api_key = "8AiGAyxlhYQaRpE1s7097hx5sZ12Ogtr8ir9DsyztaD5j24LrI0fEoToDzCI5lle"
        b_api_secret = "VhudTs0HsBVFNdSTghmqfCjUuIXF6rFiXIfROxHIaM71TGgib7NeZ5aOsJUHjI9f"
        client = Client(b_api_key, b_api_secret)
        res = client.get_all_tickers()
        for token in res:
            if ticker == token["symbol"]:
                return token["price"]
        return False


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
        text = "Could not find that ticker."
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
    elif not coin:
        ctx.bot.send_message(chat_id=update.effective_chat.id, text="Try again later.")
        return
    ticker = ctx.args[1]
    alert_p = ctx.args[2]
    tmp_price = get_ticker_price(ticker, coin)
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
    for ticker in data:
        is_c = data[ticker]["coin"]
        ticker_p = get_ticker_price(ticker, is_c)
        for user in data[ticker]["users"]:
            for alert_p in data[ticker]["users"][user]:
                alert_s = data[ticker]["users"][user][alert_p]
                if (alert_s == "b" and alert_p > ticker_p) or (alert_s == "a" and alert_p < ticker_p):
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
    updater.start_polling()
    while True:
        check_empty_stock()
        check_alerts()
        time.sleep(2)


if __name__ == '__main__':
    token = "1871537273:AAFGJOKn5tPb92BZ1E20JpHnJGFfA7to4WA"
    bot = telegram.Bot(token=token)
    main()
