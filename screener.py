import datetime
import backtrader as bt
from DataFunctions import fetchData, fetch_all_token

class Screener_SMA(bt.Analyzer):
    params = (('period',20), ('devfactor',2),)

    def start(self):
        self.bband = {data: bt.indicators.BollingerBands(data,
                period=self.params.period, devfactor=self.params.devfactor)
                for data in self.datas}

    def stop(self):
        self.rets['over'] = list()
        self.rets['under'] = list()

        for data, band in self.bband.items():
            node = data._name, data.close[0], round(band.lines.bot[0], 2)
            if data > band.lines.bot:
                self.rets['over'].append(node)
            else:
                self.rets['under'].append(node)

#Instantiate Cerebro engine
cerebro = bt.Cerebro()

#Add data to Cerebro
instruments = fetch_all_token(number=10)
for ticker in instruments:
    data=fetchData(ticker,barDuration='1d')
    dataBT=data['BT_DataFeed']
    cerebro.adddata(dataBT, name=ticker) 

#Add analyzer for screener
cerebro.addanalyzer(Screener_SMA)

if __name__ == '__main__':
    #Run Cerebro Engine
    cerebro.run(runonce=False, stdstats=False, writer=True)