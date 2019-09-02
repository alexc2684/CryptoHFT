"""
Robinhood crypto market data scraper

Example curl to get current market data for BTC:
curl 'https://api.robinhood.com/marketdata/forex/quotes/3d961844-d360-45fc-989b-f6fca761d511/' -H 'Authorization: Bearer <REDACTED>' --compressed
"""
import argparse
import logging

parser = argparse.ArgumentParser(description='Scrape robinhood data.')
parser.add_argument('--token-file', type=str, required=True,
                    help='File that contains the auth access token to use')
parser.add_argument('--output-csv', type=str, default="output.csv",
                    help='Output file to use. If the file exists, it will append onto it.')
parser.add_argument('--sleep-time', type=int, default=60,
                    help='Time to sleep between queries.')
parser.add_argument('--log-level', type=str, choices=['INFO', 'DEBUG', 'WARNING'],
                    default='INFO', help='Log level.')

def main(args):
    logging.info("Starting scraping with the following options:")
    for arg_name in args:
        logging.info("{0} = {1}".format(arg_name, args[arg_name]))

    while True:    
        # Get token from file

        # Send request

        # Save to file

        # Sleep 

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper())
    main(vars(args))
