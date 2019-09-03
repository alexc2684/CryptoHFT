"""
Robinhood crypto market data scraper
"""
import argparse
import csv
import logging
import multiprocessing
import os
import requests
import time

parser = argparse.ArgumentParser(description='Scrape robinhood data.')
parser.add_argument('--token-file', type=str, required=True,
                    help='File that contains the auth access token to use')
parser.add_argument('--output-file-fmt', type=str, default="output_{0}.csv",
                    help='Output file to use. If the file exists, it will append onto it.')
parser.add_argument('--sleep-time', type=float, default=60.0,
                    help='Time to sleep between queries.')
parser.add_argument('--log-level', type=str, choices=['INFO', 'DEBUG', 'WARNING'],
                    default='INFO', help='Log level.')

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
    results = requests.get(url, headers=headers).json()
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
    filename, metrics = args

    if not os.path.isfile(filename):
        logging.info("Writing headers and initializing file {0}".format(filename))
        headers = metrics.keys()
        write_headers(filename, headers)

    with open(filename, 'a') as f:
        logging.info("Saving metrics to {0}".format(filename))
        writer = csv.DictWriter(f, metrics.keys())
        writer.writerow(metrics)

def main(args):
    logging.info("Starting scraping with the following options:")
    args_dict = vars(args)
    for arg_name in args_dict:
        logging.info("{0} = {1}".format(arg_name, args_dict[arg_name]))

    currency_pairs = CurrencyPairs()
    pool = multiprocessing.Pool(10)
    pool_write = multiprocessing.Pool(10)

    with open(args.token_file, 'r') as tf:
            auth_token = tf.readline()

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
            all_parallel_args = []
            for pair_data in all_pair_data:
                filename = args.output_file_fmt.format(pair_data['symbol'])
                all_parallel_args.append([filename, pair_data])
            pool_write.map_async(save_metrics_to_csv, all_parallel_args)

            # logging.info("Updating currency pairs")
            # currency_pairs.update_pairs_to_ids()

            # Sleep the remaining time to sleep only.
            sleep_time = args.sleep_time - (time.time() - start_time)
            if sleep_time <= 0.0:
                # Something went wrong
                logging.warning("sleep_time = {0}".format(sleep_time))
                logging.warning("current time = {0}".format(time.time()))
            else:
                time.sleep(sleep_time)
        except Exception (e):
            logging.error("------- Exception -------")
            logging.error(str(e))

    pool.close()
    pool.join()
    pool_write.close()
    pool_write.join()

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    main(args)
