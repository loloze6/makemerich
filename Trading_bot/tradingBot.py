import backtrader as bt

from datetime import datetime, timedelta
class TradingBot:
    def backtest(self, strategy, backtest_parameters, data_source, sizer=bt.sizers.FixedSize, strategy_parameters=None,
                sizer_parameters=None, analyzers=None):
        cerebro = bt.Cerebro()

        data = data_source.get_data(backtest_parameters)
        datafeed = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(datafeed)

        initial_cash = backtest_parameters.get('initial_cash', 10000)
        commission = backtest_parameters.get('commission', 0.001)
        slippage = backtest_parameters.get('slippage', 0.001)

        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission)
        cerebro.broker.set_slippage_perc(slippage)

        if not strategy_parameters:
            strategy_parameters = {}
        cerebro.optstrategy(strategy, **strategy_parameters)

        if not sizer_parameters:
            sizer_parameters = {}
        cerebro.addsizer(sizer, **sizer_parameters)

        if analyzers:
            for analyzer in analyzers:
                cerebro.addanalyzer(analyzer)

        results = cerebro.run(maxcpus=1)
        return results, cerebro

    def live(self, strategy, live_parameters, store, sizer=bt.sizers.FixedSize, strategy_parameters=None,
             sizer_parameters=None, analyzers=None): 
        timeDeltaMin=live_parameters.get('timeDeltaMin')
        if timeDeltaMin:
            hist_start_date = datetime.utcnow() - timedelta(minutes=timeDeltaMin)
        else: hist_start_date=None
 #Retsrat here! good luck
        name=live_parameters.get('name')
        timeframe=live_parameters.get('timeframe','')
        compression=live_parameters.get('compression')
        ohlcv_limit=live_parameters.get('ohlcv_limit')
        drop_newest=live_parameters.get('drop_newest')
        data = store.getdata(dataname=live_parameters.get('dataname'),
                             name=name,
                             timeframe=timeframe, 
                             fromdate=hist_start_date,
                             compression=compression,
                             ohlcv_limit=ohlcv_limit,
                             drop_newest=drop_newest
                             )
        # timeframe=live_parameters.get('timeframe')
        # data = store.getdata(dataname=live_parameters.get('dataname'), timeframe=timeframe)
        broker = store.getbroker()

        cerebro = bt.Cerebro(quicknotify=True)
        cerebro.adddata(data)
        cerebro.setbroker(broker)

        self.configure_cerebro(cerebro, strategy, strategy_parameters, sizer, sizer_parameters, analyzers, live=True)

        result = cerebro.run()
        return result, cerebro

    @staticmethod
    def configure_cerebro(cerebro, strategy, strategy_parameters, sizer, sizer_parameters, analyzers, live=False):
        if not strategy_parameters:
            strategy_parameters = {}
        if live:
            cerebro.addstrategy(strategy, **strategy_parameters)
        else:
            cerebro.optstrategy(strategy, **strategy_parameters)

        if not sizer_parameters:
            sizer_parameters = {}
        cerebro.addsizer(sizer, **sizer_parameters)

        if analyzers:
            for analyzer in analyzers:
                cerebro.addanalyzer(analyzer, _name=analyzer.__name__),