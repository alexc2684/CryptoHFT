import json
import random
import os
from requests import get, post
from uuid import uuid4


class RobinhoodClient:
    DEFAULT_HEADERS = {
        # 'X-TimeZone-Id': 'America/Los_Angeles',
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
    AUTH_TOKEN = os.environ['RH_TOKEN']

    RH_API_URL = "https://api.robinhood.com/"
    RH_CRYPTO_URL = "https://nummus.robinhood.com/"

    ACCOUNT_ID = "cc0342b5-9765-437d-97f6-e8942ab3ebc5"  # TODO: Don't hard code this
    CLIENT_ID = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"
    DEVICE_TOKEN = ""

    currency_pairs = {}

    def __init__(self):
        self.get_currency_pairs()
        self.generate_device_token()

    def login(self):
        headers = {
                **self.DEFAULT_HEADERS,
                **self.LOGIN_HEADERS
                }

        data = {
                'client_id': self.CLIENT_ID,
                'device_token': self.DEVICE_TOKEN,
                'expires_in': 86400,
                'grant_type': 'password',
                'username': self.USERNAME,
                'password': self.PASSWORD,
                'scope': 'internal',
                'challenge_type': 'sms'
                }

        print("---")
        print(data)
        print(headers)
        print("---")

        res = post(self.RH_API_URL + 'oauth2/token/', headers = headers, data = json.dumps(data))
        print(res.reason)
        print(res)
        data = json.loads(res.content)
        print(data)
        #TODO: save auth token to file
        return data['access_token']

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
    def generate_device_token(self):
        rands = []
        for i in range(0,16):
            r = random.random()
            rand = 4294967296.0 * r
            rands.append((int(rand) >> ((3 & i) << 3)) & 255)

        hexa = []
        for i in range(0,256):
            hexa.append(str(hex(i+256)).lstrip("0x").rstrip("L")[1:])

        id = ""
        for i in range(0,16):
            id += hexa[rands[i]]

            if (i == 3) or (i == 5) or (i == 7) or (i == 9):
                id += "-"

        self.DEVICE_TOKEN = id

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
