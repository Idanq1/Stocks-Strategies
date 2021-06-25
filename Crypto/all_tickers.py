import requests
import json

tokens_url = "https://www.binance.com/bapi/asset/v2/public/asset-service/product/get-products?includeEtf=true"

req = requests.get(tokens_url)

data = json.loads(req.text)

tokens_list = []

for token in data["data"]:
    if "TetherUS" in token["qn"]:
        tokens_list.append(token["s"])

print(tokens_list)
print(len(tokens_list))