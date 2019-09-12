import json
import random
import os
from requests import get, post
from uuid import uuid4

from RobinhoodClient.Robinhood import Robinhood


class RobinhoodClient:
    DEFAULT_HEADERS = {
        'Content-Type': 'application/json',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://robinhood.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

    LOGIN_HEADERS = {
        'X-Robinhood-API-Version': '1.280.0',
        'Referer': 'https://robinhood.com/',
        'Origin': 'https://robinhood.com',
    }

    USERNAME = os.environ['RH_USERNAME']
    PASSWORD = os.environ['RH_PASSWORD']
    DEVICE_TOKEN = ""
    AUTH_TOKEN = ""
    REFRESH_TOKEN = ""

    RH_API_URL = "https://api.robinhood.com/"
    RH_CRYPTO_URL = "https://nummus.robinhood.com/"

    ACCOUNT_ID = "cc0342b5-9765-437d-97f6-e8942ab3ebc5"  # TODO: Don't hard code this
    CLIENT_ID = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"

    currency_pairs = {}

    def __init__(self):
        self.get_currency_pairs()
        self.client = Robinhood()
        self.login()

    def login(self):
        try:
            data = open('auth.secret', 'r').read()
            print(data)
            auth_data = json.loads(data)
            if "auth_token" in auth_data:
                self.AUTH_TOKEN = auth_data['auth_token']
                self.DEVICE_TOKEN = auth_data['device_token']
                self.REFRESH_TOKEN = auth_data['refresh_token']
                print("Client loaded from previous sign in")
        except BaseException:
            print("No user found, new sign in required")
            self.client.login(
                username=self.USERNAME,
                password=self.PASSWORD,
                challenge_type='sms')
            self.save_auth_data(self.client)

    def refresh_login(self):
        self.client.relogin_oauth2()
        self.save_auth_data(self.client)

    def place_order(self, symbol, quantity, price, order_type):
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

        res = post(
            self.RH_CRYPTO_URL +
            "orders/",
            headers=headers,
            data=json.dumps(data))

        if res.status_code == 201:
            print("Order successfully placed")
            print(res.content)
            return True
        else:
            print("Error while placing order")
            print("Status code: {}".format(res.status_code))
            print(res.content)
            return False

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
        price = float(content['mark_price'])
        return price

    def get_auth_token(self):
        return self.AUTH_TOKEN

    # Utils
    def save_auth_data(self, client):
        auth_data = {}
        auth_data['device_token'] = client.device_token
        self.DEVICE_TOKEN = client.device_token
        auth_data['auth_token'] = client.auth_token
        self.AUTH_TOKEN = client.auth_token
        auth_data['refresh_token'] = client.refresh_token
        self.REFRESH_TOKEN = client.refresh_token
        open('auth.secret', 'w').write(json.dumps(auth_data))

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
