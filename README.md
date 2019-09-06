# Crypto HFT

## Robinhood API Documentation:
cURL to get a list of cryptocurrencies:
```
$ curl 'https://nummus.robinhood.com/currencies/' -H 'X-TimeZone-Id: America/Los_Angeles' -H 'Authorization: Bearer <REDACTED>' --compressed
```

cURL to get a list of currency pairs:
```
$ curl 'https://nummus.robinhood.com/currency_pairs/' -H 'X-TimeZone-Id: America/Los_Angeles' --compressed
```

cURL to get current market data for BTC in particular:
```
$ curl 'https://api.robinhood.com/marketdata/forex/quotes/3d961844-d360-45fc-989b-f6fca761d511/' -H 'Authorization: Bearer <REDACTED>' --compressed
```


### RobinhoodClient.py
Handles all transactions with the Robinhood API
`login()` - Login to your account. Requires 2 Factor Authentication via SMS
`place_buy_order(symbol, quantity, price)` - Buy a cryptocurrency at said quantity and price
`place_sell_order(symbol, quantity, price)` - Sell a cryptocurrency at said quantity and price
`get_currency_price(symbol)` - Return price of the currency

