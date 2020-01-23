import time
from datetime import datetime
from DynamoDBClient import DynamoDBClient
from RobinhoodClient.RobinhoodClient import RobinhoodClient

class DataScraper:

    def __init__(self, price_recording_time_interval=1.0, asset_name='BTC', queue_size=100):
        self.price_recording_time_interval = price_recording_time_interval
        self.asset_name = asset_name
        self.queue_size = queue_size

        self.client = RobinhoodClient()
        self.client.login()

        currency_pairs = self.client.get_currency_pairs()
        self.asset_id = currency_pairs[self.asset_name]

        self.dynamo_client = DynamoDBClient()

    def get_currency_price_data(self):
        return self.client.get_currency_price_data(self.asset_name)

    def send_currency_price_data(self, data):
        self.dynamo_client.batch_write_price_data(data)

    def run_scraper(self):
        i = 0
        data_queue = []

        print("Starting data collection")

        while True:
            start_time = time.time()
            data = self.get_currency_price_data()
            data["index"] = i
            data_queue.append(data)
            i += 1

            if i % self.queue_size == 0:
                self.send_currency_price_data(data_queue)
                data_queue = []
                print("Sending data to AWS at: {}".format(datetime.now().strftime("%c")))

            self.sleep_remaining_time(start_time)


    def sleep_remaining_time(self, start_time):
        sleep_time = self.price_recording_time_interval - (time.time() - start_time)
        if sleep_time > 0:
            time.sleep(sleep_time)

