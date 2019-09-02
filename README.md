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
