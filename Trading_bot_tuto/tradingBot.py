import backtrader as bt
import pandas as pd
import datetime as dt

from Trading_bot_tuto.timeframes import Timeframes

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
        return results

