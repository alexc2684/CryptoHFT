import json
import os
from time import time
from requests import post
from uuid import uuid4

from Request import Request
from RobinhoodClient.Robinhood import Robinhood
from RobinhoodClient.RequestUtils import generateDeviceToken
from RobinhoodClient.RobinhoodRequests import get_login_tokens 

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

    AUTH_FILE_PATH = 'auth.secret'
    USERNAME = os.environ['RH_USERNAME']
    PASSWORD = os.environ['RH_PASSWORD']
    DEVICE_TOKEN = ""
    AUTH_TOKEN = ""
    REFRESH_TOKEN = ""
    EXPIRE_TIME = None

    RH_API_URL = "https://api.robinhood.com/"
    RH_CRYPTO_URL = "https://nummus.robinhood.com/"

    ACCOUNT_ID = "cc0342b5-9765-437d-97f6-e8942ab3ebc5"  # TODO: Don't hard code this
    CLIENT_ID = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"

    currency_pairs = {}

    def __init__(self):
      self.DEVICE_TOKEN = generateDeviceToken()

      self.get_currency_pairs()
      # self.client = Robinhood()

    #API
    def login(self):
        auth_data_json = self.read_file(self.AUTH_FILE_PATH)
        
        if auth_data_json:
            auth_data = json.loads(auth_data_json)
            expire_time = auth_data['expire_time']

            if self.auth_requires_refresh_token(expire_time):
                self.refresh_login()
            else:
                self.cache_auth_data(auth_data)

        else:
            print("No user found, new sign in required")
            login_tokens = get_login_tokens(self.USERNAME, self.PASSWORD, self.DEVICE_TOKEN)
            self.save_login_tokens(login_tokens)


    def refresh_login(self):
        self.client.relogin_oauth2()
        # self.save_auth_data_from_client(self.client)

    def cache_auth_data(self, auth_data):
      self.AUTH_TOKEN = auth_data['auth_token']
      self.REFRESH_TOKEN = auth_data['refresh_token']
      self.EXPIRE_TIME = auth_data['expire_time']

    def save_login_tokens(self, login_tokens):
        auth_data = {}
        
        auth_data['refresh_token'] = login_tokens['refresh_token']
        self.REFRESH_TOKEN = login_tokens['refresh_token']

        auth_data['auth_token'] = login_tokens['access_token']
        self.AUTH_TOKEN = login_tokens['access_token']
        self.DEFAULT_HEADERS['Authorization'] = 'Bearer ' + self.AUTH_TOKEN

        expiration_time = int(time()) + login_tokens['expires_in']
        auth_data['expire_time'] = expiration_time
        self.EXPIRE_TIME = expiration_time

        self.write_json_data_file(self.AUTH_FILE_PATH, auth_data)

    def get_currency_price_data(self, symbol):
        assert symbol in self.currency_pairs

        headers = {
            **self.DEFAULT_HEADERS,
            'Authorization': 'Bearer ' + self.AUTH_TOKEN
        }
        request_url = self.RH_API_URL + "marketdata/forex/quotes/{}/".format(self.currency_pairs[symbol])
        request = Request(headers, request_url)
        response = self.authorized_get_request(request)

        content = json.loads(response.content)
        price_data = dict(content)
        price_data['time'] = time()
        return price_data

    def authorized_get_request(self, request):
        try:
            return request.get_request()
        except:
            self.refresh_login()
            return request.get_request()

    def get_currency_pairs(self):
        headers = self.DEFAULT_HEADERS
        request_url = self.RH_CRYPTO_URL + 'currency_pairs/'
        request = Request(headers, request_url)
        response = request.get_request()

        currency_ids = json.loads(response.content)
        results = currency_ids['results']
        for result in results:
            currency = result['asset_currency']['code']
            pair_id = result['id']
            self.currency_pairs[currency] = pair_id

        return self.currency_pairs

    #Util Methods
    def auth_requires_refresh_token(self, expire_time):
        return time() > expire_time

    def read_file(self, filepath) -> (str, None):
        if self.is_existing_file(filepath):
            data = open(filepath, 'r').read()
            return data

    def is_existing_file(self, filepath):
        try:
            f = open(filepath)
            f.close()
            return True
        except IOError:
            return False

    def write_json_data_file(self, filepath, data):
        with open(filepath, 'w') as f:
            f.write(json.dumps(data))

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
