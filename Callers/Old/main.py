import backtrader as bt
from Strategy.Strategy1 import Strategy1
from Strategy.Strategy2 import Strategy2
from Data.DataFunctions import fetchData

#Parameters
initial_balance=100000
commission=0.001
asset_number=0.1

#Import data
data=fetchData(token='ETH/USDT',barDuration='1h',start='2018-01-01T00:00:00Z')
dataBT=data['BT_DataFeed']
dataDuration=data['Duration']
#Run multiple strategies one after each other
def testMultipleSTrategies(*args):
    for strategy in args:
        cerebro = bt.Cerebro()

        cerebro.adddata(dataBT)
        cerebro.broker.setcommission(commission)

        #   Optimize factor
        cerebro.broker.setcash(initial_balance)
        #    cerebro.addsizer(bt.sizers.FixedSize, stake=asset_number)
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.addstrategy(strategy, printlog= False, printPrice=False)
        print('BackTesting duration', dataDuration)

        #cerebro.optstrategy(*strategies)
        cerebro.run(maxcpus=1)
        cerebro.plot()


testMultipleSTrategies(Strategy1, Strategy2)

# Try to have a main strategy
# class MainStrategy(bt.Strategy):
#     def __init__(self):
#         self.strategy = None

#     def next(self):
#         self.strategy = strategies[0]()