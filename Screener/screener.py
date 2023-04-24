import datetime
import backtrader as bt
from Data.DataFunctions import fetchData, fetch_all_token

class Screener_SMA(bt.Analyzer):
    params = (
        ('BB_period',20),
        ('BB_devfactor',2),
        ('RSI_period', 14))

    def start(self):
        
        self.indicator = {data: 
                                [bt.indicators.BollingerBands(data, period=self.params.BB_period, devfactor=self.params.BB_devfactor), #0
                                 bt.indicators.RelativeStrengthIndex(data, period=self.params.RSI_period), #1
                                 bt.indicators.MovingAverageSimple(data, period=15), #2
                                 bt.indicators.MovingAverageSimple(data, period=40), #3
                                 bt.indicators.MovingAverageSimple(data, period=60),] #4
                for data in self.datas}
        self.upward_condition=False
        self.indicators=dict()
    def stop(self):
        self.rets['over'] = list()
        self.rets['under'] = list()
        
        for data, indicator in self.indicator.items():
            
            indicatorsBB=round(indicator[0].lines.bot[0], 2)
            indicatorsRSI=round(indicator[1].lines.rsi[0], 2)
            indicatorsSMA15=indicator[2].lines.sma
            indicatorsSMA40= indicator[3].lines.sma
            indicatorsSMA60= indicator[4].lines.sma
                        
            condition1=(indicatorsSMA40[0]>indicatorsSMA60[0])
            condition2=(indicatorsSMA60[0]>indicatorsSMA60[-12])
            condition3=(indicatorsSMA15[0]>indicatorsSMA40[0])
            
            condition4=(data.close[0]>indicatorsSMA60[0])
            condition5=(data.close[0]>indicatorsSMA40[0])
            condition6=(data.close[0]>indicatorsSMA15[0])
            
            condition7=(data.close[0]<min(data.close)*1.50)
            
            condition8=(indicatorsRSI>70)
            
            condition=condition1 and condition2 and condition3 and condition4 and condition5 and condition6 and condition7 and condition8
            
            conditionInfo=condition1, condition2, condition3, condition4, condition5, condition6, condition7, condition8
            
            AnalyzisInfo = data._name, data.close[0], indicatorsBB, indicatorsRSI, indicatorsSMA15[0], indicatorsSMA40[0], indicatorsSMA60[0], condition7
            
            
            if condition:
                self.rets['over'].append(AnalyzisInfo)
                self.rets['over'].append(conditionInfo)
            else:
                self.rets['under'].append(AnalyzisInfo)
                self.rets['under'].append(conditionInfo)


token='USDT'

#Instantiate Cerebro engine
cerebro = bt.Cerebro()

#Add data to Cerebro
instruments = fetch_all_token(tradedWith=token, number=10)
for ticker in instruments:
    data=fetchData(ticker,barDuration='4h')
    dataBT=data['BT_DataFeed']
    cerebro.adddata(dataBT, name=ticker) 

#Add analyzer for screener
cerebro.addanalyzer(Screener_SMA)

if __name__ == '__main__':
    #Run Cerebro Engine
    cerebro.run(runonce=False, stdstats=False, writer=True)
