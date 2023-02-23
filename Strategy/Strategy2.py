import ccxt
import pandas as pd
import backtrader as bt

class Strategy2(bt.Strategy):
    params = (
        ("sma_period", 20),
        ('printlog', True),
        ('printPrice', False),)
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
        self.nbTrades=0
        self.succesfulTrades=0
        self.totalCom=0
        self.initialValuePort=self.broker.getvalue()

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
        self.nbTrades += 1
        if trade.pnlcomm > 0:
            self.succesfulTrades += 1
            
    def next(self):
        if self.params.printPrice:
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
#To optimize MA
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.sma_period, self.broker.getvalue()), doprint=True)
        self.log('Final Portfolio Value: %.2f' % 
                 (self.broker.getvalue()), doprint=True)
        if self.nbTrades>0:
            self.log('Number of trades: %.2f , Number of succesful trades: %.2f, Percent of succesful trades: %.2f' % 
                    (self.nbTrades, self.succesfulTrades, self.succesfulTrades/self.nbTrades*100), doprint=True)
        self.log('Total ROI on Portfolio: %.2f , Total commision spent: %.2f' % 
                    ((self.broker.getvalue()-self.initialValuePort)/self.initialValuePort*100, self.totalCom), doprint=True)     