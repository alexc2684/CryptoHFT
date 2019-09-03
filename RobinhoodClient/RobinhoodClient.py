import json
import os
from requests import get, post
from uuid import uuid4


class RobinhoodClient:
    DEFAULT_HEADERS = {
        'X-TimeZone-Id': 'America/Los_Angeles',
        'content-type': 'application/json',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://robinhood.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

    AUTH_TOKEN = os.environ['RH_TOKEN']
    RH_API_URL = "https://api.robinhood.com/"
    RH_CRYPTO_URL = "https://nummus.robinhood.com/"
    ACCOUNT_ID = "cc0342b5-9765-437d-97f6-e8942ab3ebc5"  # TODO: Don't hard code this
    currency_pairs = {}

    def __init__(self):
        self.get_currency_pairs()

    def place_order(self, symbol, quantity, price, order_type):
        # validate symbol is in currency_pair
        assert symbol in self.currency_pairs
        assert order_type in ['buy', 'sell']

        currency_id = self.currency_pairs[symbol]

        headers = {
            **self.DEFAULT_HEADERS,
            'Authorization': 'Bearer ' + self.AUTH_TOKEN
        }

        data = {
            "type": "market",
            "side": order_type,
            "quantity": str(quantity),
            "account_id": self.ACCOUNT_ID,
            "currency_pair_id": str(currency_id),
            "price": str(price),
            "ref_id": str(uuid4()),
            "time_in_force": "gtc"
        }

        res = post(self.RH_CRYPTO_URL + "orders/", headers=headers, data=data)
        print(res.content)

    def place_buy_order(self, symbol, quantity, price):
        self.place_order(symbol, quantity, price, 'buy')

    def place_sell_order(self, symbol, quantity, price):
        self.place_order(symbol, quantity, price, 'sell')

    def get_currency_price(self, symbol):
        assert symbol in self.currency_pairs

        headers = {
            **self.DEFAULT_HEADERS,
            'Authorization': 'Bearer ' + self.AUTH_TOKEN
        }

        res = get(
            self.RH_API_URL +
            "marketdata/forex/quotes/{}/".format(
                self.currency_pairs[symbol]),
            headers=headers)
        content = json.loads(res.content)
        return content['mark_price']

    # Utils

    def get_currency_pairs(self):
        raw_ids = get(
            self.RH_CRYPTO_URL +
            'currency_pairs/',
            headers=self.DEFAULT_HEADERS)
        currency_ids = json.loads(raw_ids.content)
        results = currency_ids['results']
        for result in results:
            currency = result['asset_currency']['code']
            pair_id = result['id']
            self.currency_pairs[currency] = pair_id
