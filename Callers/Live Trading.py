import backtrader as bt
from ccxtbt import CCXTStore
import time

from Trading_bot.tradingBot import TradingBot

from Account_management.GetAPIKeys import GetAPIKeys

from Strategy.BuyHoldwithBracket import BuyHoldStrategy
from Strategy.Base_Strategy_simplified import TestStrategy
from Strategy.EMAwithBracket import BracketStrategyExample


sandbox = True


credential = GetAPIKeys().getAPIkeys(sandbox)
binance_api_key = credential['User']
binance_api_secret = credential['Password']


store2 = CCXTStore(
    exchange='binance',
    currency='USDT',
    config={
        'apiKey': binance_api_key,
        'secret': binance_api_secret,
        'nonce': lambda: str(int(time.time() * 1000)),
        'enableRateLimit': True,
        'adjustForTimeDifference': True,
        'newOrderRespType': 'FULL',
        'defaultTimeInForce': 'GTC',
        'verbose': False
    },
    retries=1,
    sandbox=sandbox,
    debug=False
)

bot = TradingBot()

# strategy = TestStrategy
# strategy_parameters = {}


# strategy = BracketStrategyExample
# strategy_parameters = {
#     'period_me1': 12, 'logging': True, 'stop_loss': 1, 'risk_reward': range(1, 5)
# }

strategy = BuyHoldStrategy
strategy_parameters = {
    'logging': True, 'stop_loss': 0.1, 'risk_reward': 1
}

sizer = bt.sizers.PercentSizer
sizer_parameters = {
    'percents': 1
}

analyzers = [
    bt.analyzers.TradeAnalyzer
    ]


live_parameters = {
    'dataname': 'BNB/USDT',
    'name': "BNBUSDT",
    'timeframe': bt.TimeFrame.Minutes,
    'timeDeltaMin': 50,
    'compression':1,
    'ohlcv_limit':50,
    'drop_newest':True
}
result, cerebro =bot.live(strategy, live_parameters, store=store2, strategy_parameters=strategy_parameters, sizer=sizer,
         sizer_parameters=sizer_parameters, analyzers=analyzers)
         
strat_result = result[0]
analysis = strat_result.analyzers.TradeAnalyzer.get_analysis()
    # total_net_pnl = analysis.pnl.net.total
    # print(f"Parameters: {params} | Total Net PNL: {total_net_pnl}")        
    
cerebro.plot()