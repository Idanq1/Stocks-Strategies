import finnhub
"""
"c43om8iad3if0j0su4og",
"c43baq2ad3iaavqonarg",
"c437gqqad3iaavqojj0g",
"c43f8kiad3if0j0skdvg",
"c43opbaad3if0j0su7bg",
"c43oqsaad3if0j0su8b0",
"c43ordiad3if0j0su8sg",
"c43oseqad3if0j0su9e0",
"c43ossiad3if0j0su9pg",
"c43otbqad3if0j0sua3g"
"""
finnhub_client = finnhub.Client(api_key="c43otbqad3if0j0sua3g")

print(finnhub_client.stock_candles('AAPL', 'D', 1590988249, 1591852249))
