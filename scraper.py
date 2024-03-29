"""
Robinhood crypto market data scraper
"""
import argparse
import csv
import logging
import requests
import time
import json
import asyncio
import websockets
from RobinhoodClient.RobinhoodClient import RobinhoodClient

parser = argparse.ArgumentParser(description='Scrape robinhood data.')
parser.add_argument('--output-file-fmt', type=str, default="output.csv",
                    help='Output file to use. If the file exists, it will append onto it.')
parser.add_argument('--sleep-time', type=float, default=1.0,
                    help='Time to sleep between queries.')

SCRAPE_CURRENCIES = [
    'BTC-USD', # Bitcoin
]

assert len(SCRAPE_CURRENCIES) == 1 # Because I switched out the pool.map to a normal map

# Sent on all requests
DEFAULT_HEADERS = {
    'X-TimeZone-Id': 'America/Los_Angeles'
}

class CurrencyPairs(object):
    """
    House info about all the coins we are watching
    """

    def __init__(self):
        self.pairs = SCRAPE_CURRENCIES
        self.pairs_to_ids = dict()
        self.update_pairs_to_ids()

    def update_pairs_to_ids(self):
        url = 'https://nummus.robinhood.com/currency_pairs/'
        headers = {**DEFAULT_HEADERS}
        resp = requests.get(url, headers=headers)
        all_currency_pairs = resp.json()['results']
        for pair in all_currency_pairs:
            if pair['symbol'] in self.pairs:
                self.pairs_to_ids[pair['symbol']] = pair["id"]

    def __str__(self):
        return str(self.pairs_to_ids)

def get_curr_data(args):
    currency_pair_id, auth_token = args
    url = "https://api.robinhood.com/marketdata/forex/quotes/{0}/".format(currency_pair_id)
    headers = {
        **DEFAULT_HEADERS,
        'Authorization': 'Bearer {0}'.format(auth_token)
    }
    req_time = time.time()
    try:
        results = requests.get(url, headers=headers).json()
        results['refresh'] = False
    except:
        client.refresh_login()
        refresh = True
        headers['Authorization'] = 'Bearer {0}'.format(client.get_auth_token()) #TODO: put all requests in RobinhoodClient
        results = requests.get(url, headers=headers).json()
        results['refresh'] = True
    results['_time'] = req_time
    return results

def write_headers(filename, headers):
    with open(filename, 'w') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, headers)
        w.writeheader()

def save_metrics_to_csv(args):
    """
    Assume metrics is a dict like
    {'ask_price': '6.283982', 'bid_price': '6.266302', 'mark_price': '6.275142', 'high_price': '6.343000', 'low_price': '6.091000', 'open_price': '6.247500', 'symbol': 'ETCUSD', 'id': '7b577ce3-489d-4269-9408-796a0d1abb3a', 'volume': '23452255.152900'}
    """
    filename, metrics, write_headers = args

    if write_headers:
        headers = metrics.keys()
        write_headers(filename, headers)

    with open(filename, 'a') as f:
        writer = csv.DictWriter(f, metrics.keys())
        writer.writerow(metrics)

async def send_price_data(prices):
     uri = "ws://localhost:8765"
     async with websockets.connect(uri) as websocket:
         await websocket.send(prices)
         await websocket.recv()

def main(args):
    args_dict = vars(args)
    currency_pairs = CurrencyPairs()

    with open('auth.secret', 'r') as tf:
            data = json.loads(tf.read())
            auth_token = data['auth_token']

    # is_first_loop = True
    while True:
        try:
            start_time = time.time()

            # Send requests in parallel to make it faster
            all_parallel_args = []
            for _, pair_id in currency_pairs.pairs_to_ids.items():
                curr_parallel_args = [pair_id, auth_token]
                all_parallel_args.append(curr_parallel_args)
            # all_pair_data = pool.map(get_curr_data, all_parallel_args)
            # Not in parallel!
            all_pair_data = map(get_curr_data, all_parallel_args)

            # Save to file
            # all_parallel_args = []
            for pair_data in all_pair_data:
                filename = args.output_file_fmt.format(pair_data['symbol'])
                # all_parallel_args.append([filename, pair_data, is_first_loop])
                ask_price = pair_data['ask_price']
                bid_price = pair_data['bid_price']
                mark_price = pair_data['mark_price']
                refresh = pair_data['refresh']
                asyncio.get_event_loop().run_until_complete(send_price_data('{} {} {} {} {}'.format(bid_price, ask_price, mark_price, start_time, refresh)))
            # is_first_loop = False

            # logging.info("Updating currency pairs")
            # currency_pairs.update_pairs_to_ids()

            # Sleep the remaining time to sleep only.
            sleep_time = args.sleep_time - (time.time() - start_time)
            time.sleep(sleep_time)
        except Exception as e:
            print(str(e))

if __name__ == "__main__":
    args = parser.parse_args()
    client = RobinhoodClient()
    client.login()
    main(args)
