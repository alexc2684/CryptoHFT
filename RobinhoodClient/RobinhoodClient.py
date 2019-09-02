import requests
import json
import os

DEFAULT_HEADERS = {'X-TimeZone-Id': 'America/Los_Angeles', 'content-type': 'application/json', 'Sec-Fetch-Mode': 'cors', 'Referer': 'https://robinhood.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

TOKEN = os.environ['RH_TOKEN']

API_URL = "https://nummus.robinhood.com/"
HEADERS = {**DEFAULT_HEADERS, 'Authorization': 'Bearer ' + TOKEN}

class RobinhoodClient:
    currency_to_id = {}

    def place_buy_order(self, symbol, quantity, price):
        if not len(list(self.currency_to_id.keys())):
            self.get_currency_ids()

    def get_currency_ids(self):
        raw_ids = requests.get(API_URL + 'currency_pairs/', headers = DEFAULT_HEADERS)
        currency_ids = json.loads(raw_ids.content)
        results = currency_ids['results']
        for result in results:
            currency = result['asset_currency']['code']
            pair_id = result['id']
            self.currency_to_id[currency] = pair_id

