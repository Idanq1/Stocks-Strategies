from binance import Client
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update


def get_ticker_price(ticker, coin=False):
    if ticker and not coin:
        print("Get stock price")
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
    ctx.bot.send_message(chat_id=update.effective_chat.id, text="I am the best bot on earth")


def echo(update: Update, ctx: CallbackContext):
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=" ".join(ctx.args))


def price(update: Update, ctx: CallbackContext):
    ticker = ctx.args[-1]
    ticker_price = get_ticker_price(ticker, True)
    if ticker_price:
        text = str(ticker_price)
    else:
        text = "Could not find that ticker."
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=text)


def main():
    token = "1871537273:AAFGJOKn5tPb92BZ1E20JpHnJGFfA7to4WA"

    # bot = telegram.Bot(token=TOKEN)

    updater = Updater(token=token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('echo', echo))
    dp.add_handler(CommandHandler('price', price))
    updater.start_polling()
    print(get_ticker_price("BTCUSDT", True))
    print("bot ready")


if __name__ == '__main__':
    main()
