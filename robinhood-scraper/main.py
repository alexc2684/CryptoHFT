"""
Robinhood crypto market data scraper

Example curl to get current market data for BTC:
curl 'https://api.robinhood.com/marketdata/forex/quotes/3d961844-d360-45fc-989b-f6fca761d511/' -H 'Authorization: Bearer <REDACTED>' --compressed
"""
import argparse

parser = argparse.ArgumentParser(description='Scrape robinhood data.')
parser.add_argument('--token-file', type=str, required=True,
                    help='File that contains the auth access token to use')
parser.add_argument('--output-csv', type=str, default="output.csv",
                    help='Output file to use. If the file exists, it will append onto it.')
parser.add_argument('--sleep-time', type=int, default=60,
                    help='Time to sleep between queries.')

def main(args):
    print(vars(args))

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
