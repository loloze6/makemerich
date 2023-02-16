from datetime import datetime, timedelta

import backtrader as bt
from backtrader import Order

from ccxtbt import CCXTStore
from GetAPIKeys import GetAPIKeys


class TestStrategy(bt.Strategy):
    
    def __init__(self):

        self.bought = False
        # To keep track of pending orders and buy price/commission
        self.order = None

    def next(self):

        if self.live_data and not self.bought:
            # Buy
            # size x price should be >10 USDT at a minimum at Binance
            # make sure you use a price that is below the market price if you don't want to actually buy
            # A=CCXTStore(exchange='binance', currency='BNB', config=config, retries=5, debug=True, sandbox=sandbox)
            # params = {'type':'spot'} 
            # A.create_order('BNB/USDT', 'limit', 'buy', amount=1, price=280, params=params)
            
            self.order = self.buy(size=1, exectype=Order.Limit, price=270)
            # And immediately cancel the buy order
            self.bought = True

        for data in self.datas:
            print('{} - {} | O: {} H: {} L: {} C: {} V:{}'.format(data.datetime.datetime(),
                                                                  data._name, data.open[0], data.high[0], data.low[0],
                                                                  data.close[0], data.volume[0]))

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.now()
        msg = 'Data Status: {}, Order Status: {}'.format(data._getstatusname(status), status)
        print(dt, dn, msg)
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False


cerebro = bt.Cerebro(quicknotify=True)


# Add the strategy
cerebro.addstrategy(TestStrategy)

sandbox = True

credential = GetAPIKeys().getAPIkeys(sandbox)
binance_api_key = credential['User']
binance_api_secret = credential['Password']

# Create our store
config = {'apiKey': binance_api_key,
          'secret': binance_api_secret,

        #   'enableRateLimit': True,
        #   'nonce': lambda: str(int(time.time() * 1000)),
           'adjustForTimeDifference': True,
           'newOrderRespType': 'RESULT',
           'defaultTimeInForce': 'GTC'
          }

store = CCXTStore(exchange='binance', currency='BNB', config=config, retries=5, debug=True, sandbox=sandbox, 
)

# Get the broker and pass any kwargs if needed.
# ----------------------------------------------
# Broker mappings have been added since some exchanges expect different values
# to the defaults. Case in point, Kraken vs Bitmex. NOTE: Broker mappings are not
# required if the broker uses the same values as the defaults in CCXTBroker.
broker_mapping = {
    'order_types': {
        bt.Order.Market: 'market',
        bt.Order.Limit: 'limit',
        bt.Order.Stop: 'stop-loss',  # stop-loss for kraken, stop for bitmex
        bt.Order.StopLimit: 'stop limit'
    },
    'mappings': {
        'closed_order': {
            'key': 'status',
            'value': 'closed'
        },
        'canceled_order': {
            'key': 'status',
            'value': 'canceled'
        }
    }
}

broker = store.getbroker(broker_mapping=broker_mapping)
cerebro.broker.setcash(20000.0)

cerebro.setbroker(broker)

# Get our data
# Drop newest will prevent us from loading partial data from incomplete candles
hist_start_date = datetime.utcnow() - timedelta(minutes=50)
data = store.getdata(dataname='BNB/USDT', name="BNBUSDT",
                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                     compression=1, ohlcv_limit=50, drop_newest=True)  # , historical=True)

# Add the feed
cerebro.adddata(data)
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
# Run the strategy
initial_value = cerebro.broker.getvalue()
# print('Starting Portfolio Value: %.2f' % initial_value)
# A=CCXTStore(exchange='binance', currency='BNB', config=config, retries=5, debug=True, sandbox=sandbox)
# params = {'type':'spot'} 
# A.create_order(symbol='BNB/USDT', order_type='limit', side='buy', amount=1, price=280, params=params)
# A.cancel_order(1092399, 'BNB/USDT')
result=cerebro.run()
# exchange.create_order('BNB/USDT', 'limit', 'buy', 1, price=270)

# import ccxt
# from GetAPIKeys import GetAPIKeys
# sandbox=True
# credential = GetAPIKeys().getAPIkeys(sandbox)
# binance_api_key = credential['User']
# binance_api_secret = credential['Password']

# exchange=ccxt.binance()
# exchange.set_sandbox_mode(sandbox)
# exchange.apiKey=binance_api_key
# exchange.secret=binance_api_secret
# exchange.options = {'adjustForTimeDifference': True,
#                     'newOrderRespType': 'FULL',
#                     'defaultTimeInForce': 'GTC'}
# exchange.fetch_balance()
# exchange.fetch_my_trades('BTC/USDT')
# exchange.create_order('BNB/USDT', 'limit', 'buy', 1, price=270)
# exchange.fetch_orders('BTC/USDT')
# exchange.cancel_order(5157256,'BTC/USDT')


# import logging
# import contextlib
# try:
#     from http.client import HTTPConnection # py3
# except ImportError:
#     from httplib import HTTPConnection # py2

# def debug_requests_on():
#     '''Switches on logging of the requests module.'''
#     HTTPConnection.debuglevel = 1

#     logging.basicConfig()
#     logging.getLogger().setLevel(logging.ERROR)
#     requests_log = logging.getLogger("requests.packages.urllib3")
#     requests_log.setLevel(logging.ERROR)
#     requests_log.propagate = True

# def debug_requests_off():
#     '''Switches off logging of the requests module, might be some side-effects'''
#     HTTPConnection.debuglevel = 0

#     root_logger = logging.getLogger()
#     root_logger.setLevel(logging.ERROR)
#     root_logger.handlers = []
#     requests_log = logging.getLogger("requests.packages.urllib3")
#     requests_log.setLevel(logging.ERROR)
#     requests_log.propagate = False

# @contextlib.contextmanager
# def debug_requests():
#     '''Use with 'with'!'''
#     debug_requests_on()
#     yield
#     debug_requests_off()

# requests.get('http://httpbin.org/')
# debug_requests_off()
# import requests
# import json

# url = "https://testnet.binance.vision/api/v3/order?timestamp=1676455265632&symbol=BNBUSDT&side=BUY&newOrderRespType=RESULT&type=LIMIT&quantity=1&price=270&timeInForce=GTC&signature=9848101af38a291ed048b93f6616cf11fcdf9fe4ce147bc09d7097fbfbb88779"
# url = "https://testnet.binance.vision/api/v3/order?timestamp=1676455082855&symbol=BNBUSDT&side=BUY&newClientOrderId=x-R4BD3S826480cf92e5b68ea78001ae&newOrderRespType=FULL&type=LIMIT&quantity=1&price=270&timeInForce=GTC&created=1676451420000&recvWindow=60000&signature=9c67248238407a8c5d0784174bb41c065ea2cd70e42b83863661fcc304e9a428"
# headers = {'X-MBX-APIKEY': 'KEb9xqCanquHWYSpdY2AZAtzu3du5xRFjg5SKDBo0ixwhldQIlEh4vn6hzJVeBer'}


# # headers = {'X-MBX-APIKEY': 'KEb9xqCanquHWYSpdY2AZAtzu3du5xRFjg5SKDBo0ixwhldQIlEh4vn6hzJVeBer', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'python-requests/2.28.2', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
 
# data = {'X-MBX-APIKEY': 'KEb9xqCanquHWYSpdY2AZAtzu3du5xRFjg5SKDBo0ixwhldQIlEh4vn6hzJVeBer', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'python-requests/2.28.2', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
 
# response = requests.post(url, 
#                         headers=headers

#                          )
 
# print("Status Code", response.status_code)

# print("JSON Response ", response.json())