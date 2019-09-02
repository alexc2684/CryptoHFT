"""
Robinhood crypto market data scraper
"""
import argparse
import logging
import time

parser = argparse.ArgumentParser(description='Scrape robinhood data.')
parser.add_argument('--token-file', type=str, required=True,
                    help='File that contains the auth access token to use')
parser.add_argument('--output-csv', type=str, default="output.csv",
                    help='Output file to use. If the file exists, it will append onto it.')
parser.add_argument('--sleep-time', type=float, default=60.0,
                    help='Time to sleep between queries.')
parser.add_argument('--log-level', type=str, choices=['INFO', 'DEBUG', 'WARNING'],
                    default='INFO', help='Log level.')

def main(args):
    logging.info("Starting scraping with the following options:")
    args_dict = vars(args)
    for arg_name in args_dict:
        logging.info("{0} = {1}".format(arg_name, args_dict[arg_name]))

    while True:    
        # Get token from file
        with open(args.token_file, 'r') as tf:
            token = tf.readline()
        
        # Send request
        resp = requests.get()

        # Save to file

        # Sleep 
        time.sleep(args.sleep_time)

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    main(args)
