import configparser
import ccxt
import time
import pandas as pd

# Initialize the Binance exchange object
binance = ccxt.binance()
binance.options = {'adjustForTimeDifference': True}
#'defaultType': 'future'#
config = configparser.ConfigParser()
config.read('APIKEYS.ini')

binance.apiKey = config['API']['BINANCE_USER']
binance.secret = config['API']['BINANCE_PASSWORD']

#Get balance
balance = binance.fetch_balance()

# Print the balance
print(balance)

