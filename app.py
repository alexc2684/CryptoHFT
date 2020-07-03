import json

from flask import Flask, make_response
from RobinhoodClient.RobinhoodClient import RobinhoodClient

app = Flask(__name__)
client = RobinhoodClient()

headers = {"Content-Type": "application/json"}

@app.route("/login")
def login():
  client.login()
  return make_success_response("Login Success")


@app.route("/currencies")
def get_currency_pairs():
  currency_pairs_json = json.dumps(client.get_currency_pairs())
  return make_success_response(currency_pairs_json)
  

@app.route("/price/<symbol>")
def get_price(symbol):
  price_data_json = json.dumps(client.get_currency_price_data(symbol))
  return make_success_response(price_data_json)

## Utils

def make_success_response(data="Success"):
  response = make_response(
      data,
      200
    )
  response.headers = headers
  return response

## Run app

if __name__ == "__main__":
  app.run()
    
  