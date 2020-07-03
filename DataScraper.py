import json
import requests
import os
import time
from datetime import datetime

from DynamoDBClient import DynamoDBClient
from RobinhoodClient.RobinhoodClient import RobinhoodClient

class DataScraper:
    server_url = os.getenv("SERVER_URL")

    def __init__(self, price_recording_time_interval=1.0, asset_name='BTC', queue_size=100):
      self.price_recording_time_interval = price_recording_time_interval
      self.asset_name = asset_name
      self.queue_size = queue_size

      response = requests.get(self.server_url + '/currencies')
      currency_pairs = dict(json.loads(response.text))
      self.asset_id = currency_pairs[self.asset_name]
      self.dynamo_client = DynamoDBClient()

    def get_currency_price_data(self):
      endpoint = self.server_url + '/price/{}'.format(self.asset_name)
      response = requests.get(endpoint)
      print(response.text)
      data = dict(json.loads(response.text))
      return data

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

