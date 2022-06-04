import requests
import json

tokens_url = "https://www.binance.com/bapi/asset/v2/public/asset-service/product/get-products?includeEtf=true"
req = requests.get(tokens_url)

data = json.loads(req.text)

coins_list = []

for coin in data["data"]:
    if "TetherUS" in coin["qn"]:
        coins_list.append(coin["s"])

print(coins_list)
print(len(coins_list))
