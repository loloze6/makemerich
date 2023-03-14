from datetime import datetime, timedelta
import time
import backtrader as bt
from backtrader import Order

from ccxtbt import CCXTStore
from GetAPIKeys import GetAPIKeys


class TestStrategy(bt.Strategy):

    def __init__(self):

        self.bought = False
        # To keep track of pending orders and buy price/commission
        self.order = None

    def log(self, txt, dt=None, doprint=True):
        if doprint:
            dt= dt or self.data.datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(order)
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.price,
                     order.Info,
                     order.OrdType))
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None


    def next(self):

        for data in self.datas:
            print('Status: {} | {} - {} | O: {} H: {} L: {} C: {} V:{}'.format(self.live_data, data.datetime.datetime(),
                                                                  data._name, data.open[0], data.high[0], data.low[0],
                                                                  data.close[0], data.volume[0]))
            
            
            if self.live_data:
            # Buy
            # size x price should be >10 USDT at a minimum at Binance
            # make sure you use a price that is below the market price if you don't want to actually buy
                self.order = self.buy(size=0.01, exectype=Order.Market)
            # And immediately cancel the buy order
            # self.cancel(self.order)
                print('Buy attempt')
                self.stop()

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
        
    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.now()
        msg = 'Data Status: {}, Order Status: {}'.format(data._getstatusname(status), status)
        print(dt, dn, msg)
        if data._getstatusname(status) == 'LIVE':
            self.live_data = True
        else:
            self.live_data = False

    def stop(self):
        return


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

           'enableRateLimit': True,
           'nonce': lambda: str(int(time.time() * 1000)),
           'adjustForTimeDifference': True,
           'newOrderRespType': 'RESULT',
           'defaultTimeInForce': 'GTC',
        #    'recvWindow': 30000,
        #   'verbose': True,
          }

store = CCXTStore(exchange='binance', currency='USDT', config=config, retries=5, debug=True, sandbox=sandbox, 
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
data = store.getdata(dataname='BTC/USDT', name="BTCUSDT",
                     timeframe=bt.TimeFrame.Minutes, fromdate=hist_start_date,
                     compression=1, ohlcv_limit=50, drop_newest=True)  # , historical=True)

# Add the feed
cerebro.adddata(data)
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
# Run the strategy
# print('Starting Portfolio Value: %.2f' % initial_value)
# A=CCXTStore(exchange='binance', currency='BNB', config=config, retries=5, debug=True, sandbox=sandbox)
# params = {'type':'spot'} 
# A.create_order(symbol='BNB/USDT', order_type='limit', side='buy', amount=1, price=280, params=params)
# A.cancel_order(1092399, 'BNB/USDT')
result=cerebro.run()

# strat_result = result[0]
#     analysis = strat_result.analyzers.trade.get_analysis()
#     total_net_pnl = analysis.pnl.net.total
#     print(f"Parameters: {params} | Total Net PNL: {total_net_pnl}")
# # exchange.create_order('BNB/USDT', 'limit', 'buy', 1, price=270)

import ccxt
from Account_management.GetAPIKeys import GetAPIKeys
sandbox=True
credential = GetAPIKeys().getAPIkeys(sandbox)
binance_api_key = credential['User']
binance_api_secret = credential['Password']

exchange=ccxt.binance()
exchange.set_sandbox_mode(sandbox)
exchange.apiKey=binance_api_key
exchange.secret=binance_api_secret
exchange.options = {'adjustForTimeDifference': True,
                    'newOrderRespType': 'FULL',
                    'defaultTimeInForce': 'GTC'}
exchange.fetch_balance()
exchange.fetch_orders('BTC/USDT')
# exchange.create_order('BTC/USDT', type='Market', side='sell', amount=0.011)
# exchange.create_order('BTC/USDT', type='Market', side='buy', amount=0.01)
stopLossParams = {'trailingDelta': 25000}

exchange.create_order(symbol='BNB/USDT', type='STOP_MARKET', side='sell',
                                          amount=1, price=308.50000000)
exchange.create_order('BNB/USDT', 'STOP_LOSS_LIMIT', 'sell',
                                          1, 290.50000000, params={'trailpercent': 290.50000000})
# # exchange.create_order('BNB/USDT', 'limit', 'buy', 1, price=270)
# # exchange.cancel_order(5157256,'BTC/USDT')




# # requests.get('http://httpbin.org/')
# # debug_requests_off()
import requests
import json

url = "https://testnet.binance.vision/api/v3/order?timestamp=1676455265632&symbol=BNBUSDT&side=BUY&newOrderRespType=RESULT&type=S&quantity=1&price=270&timeInForce=GTC&signature=9848101af38a291ed048b93f6616cf11fcdf9fe4ce147bc09d7097fbfbb88779"
url = "https://testnet.binance.vision/api/v3/order?timestamp=1676455082855&symbol=BNBUSDT&side=BUY&newClientOrderId=x-R4BD3S826480cf92e5b68ea78001ae&newOrderRespType=FULL&type=LIMIT&quantity=1&price=270&timeInForce=GTC&created=1676451420000&recvWindow=60000&signature=9c67248238407a8c5d0784174bb41c065ea2cd70e42b83863661fcc304e9a428"
headers = {'X-MBX-APIKEY': 'KEb9xqCanquHWYSpdY2AZAtzu3du5xRFjg5SKDBo0ixwhldQIlEh4vn6hzJVeBer'}


# headers = {'X-MBX-APIKEY': 'KEb9xqCanquHWYSpdY2AZAtzu3du5xRFjg5SKDBo0ixwhldQIlEh4vn6hzJVeBer', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'python-requests/2.28.2', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
 
data = {'X-MBX-APIKEY': 'KEb9xqCanquHWYSpdY2AZAtzu3du5xRFjg5SKDBo0ixwhldQIlEh4vn6hzJVeBer', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'python-requests/2.28.2', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
 
response = requests.post(url, 
                        headers=headers

                         )
 
print("Status Code", response.status_code)

print("JSON Response ", response.json())


kargs = dict(data='data', price='1234', exectype=1,valid=1, tradeid=1)
kargs.update({})
#changed to not None instead of None
kargs['transmit'] = True is not None
kargs['size'] = o.size
#Debug
print(kargs)
exchange.create_order(**kargs)
kargs['params']['test'] = {}

def test(data=None, valid=None, tradeid=0, limitprice=None, limitexec=1, **kwargs):
    kargs = dict(data=data, price=limitprice, exectype=limitexec,valid=valid, tradeid=tradeid)
    kargs.update(kwargs)
    kargs['transmit'] = True
    #Debug
    return(kargs)

test123=test(price=1234, stopprice=5678, limitprice=99, params={'StopPrice': 1111})
test123