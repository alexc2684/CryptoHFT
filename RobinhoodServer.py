import json

from flask import Flask, make_response
from RobinhoodClient.RobinhoodClient import RobinhoodClient

app = Flask(__name__)
client = RobinhoodClient()

headers = {"Content-Type": "application/json"}

@app.route("/login")
def login():
  client.login()

@app.route("/currencies")
def get_currency_pairs():
  currency_pairs_json = json.dumps(client.get_currency_pairs())
  return make_response(
    currency_pairs_json,
    200,
    headers=headers
  )

@app.route("/price/<symbol>")
def get_price(symbol):
  client.get_currency_price_data(symbol)

if __name__ == "__main__":
  app.run()
  client.login()
    
  