import ccxt
import pandas as pd
import backtrader as bt

# Step 1: Create an exchange object and load market data
exchange = ccxt.binance()
ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h')

# Step 2: Convert data to pandasa DataFrame
data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data.set_index('timestamp', inplace=True)


# Step 4: Set parameters for the strategy
initial_balance=10000
commission=0.001
asset_number=0.1

# Step 3: Define strategy and run backtest
class MyStrategy(bt.Strategy):
    params = (
        ("sma_period", 20),
        ('printlog', False),
        )
#Other params: ('exitbars', 1),    
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt= dt or self.data.datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        #SMA indicator initialization
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.sma_period
        )
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose=self.data.close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if not self.position:
            #SMA indicator for BUY
            if self.data.close[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
            else:
                self.close()
        else:
            # Already in the market ... we might sell
            #if len(self) >= (self.bar_executed + self.params.exitbars):
            
            #SMA indicator for SELL
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()            

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.sma_period, self.broker.getvalue()), doprint=True)


cerebro = bt.Cerebro()
#strats = cerebro.optstrategy(
#        MyStrategy,
#        sma_period=range(10, 31))
cerebro.broker.setcash(initial_balance)
cerebro.broker.setcommission(commission)
cerebro.addstrategy(MyStrategy)
data = bt.feeds.PandasData(dataname=data)
cerebro.adddata(data)    # Add a FixedSize sizer according to the stake
cerebro.addsizer(bt.sizers.FixedSize, stake=asset_number)
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
results=cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot()



#trade_analyzer = results[0].analyzers.trade_analyzer.get_analysis()
#df=pd.DataFrame(trade_analyzer)
#print(df)


