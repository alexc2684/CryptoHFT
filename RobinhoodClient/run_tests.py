from RobinhoodClient import RobinhoodClient

client = RobinhoodClient()

#Test login
print(client.login())

#Test get prices
print(client.get_currency_price("BTC"))

# Test buy
#print(client.place_buy_order("BTC", ".00001", 11000.0))
