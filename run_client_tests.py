from RobinhoodClient.RobinhoodClient import RobinhoodClient

client = RobinhoodClient()

#Test login
print(client.login())
# print(client.refresh_login())

#Test get prices
print(client.get_currency_price_data("BTC"))

print(client.get_currency_pairs())

# Test buy
# print(client.place_buy_order("BTC", ".00001", 10110.0))
