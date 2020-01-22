import boto3
from decimal import Decimal

class DynamoDBClient:
    def __init__(self):
        self.session = boto3.Session(profile_name='crypto')
        self.resource = self.session.resource('dynamodb')
        self.table = self.resource.Table('bitcoin_price_data_in_secs')

    def batch_write_price_data(self, price_data):
        with self.table.batch_writer() as batch:
            for fields in price_data:
                batch.put_item(Item={
                    "time": Decimal(fields['time']),
                    "ask_price": Decimal(fields['ask_price']),
                    "bid_price": Decimal(fields['bid_price']),
                    "mark_price": Decimal(fields['mark_price']),
                    "high_price": Decimal(fields['high_price']),
                    "open_price": Decimal(fields['open_price'])
                })

