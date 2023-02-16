import backtrader as bt
from ccxtbt import CCXTStore
import time

from Trading_bot_tuto.tradingBot import TradingBot
from Trading_bot_tuto.CustomStrategy import BracketStrategyExample
from GetAPIKeys import GetAPIKeys
from Trading_bot_tuto.Base_Strategy_simplified import TestStrategy



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
        'defaultTimeInForce': 'GTC'
    },
    retries=1,
    sandbox=sandbox,
    debug=True
)
# binance.options = {'adjustForTimeDifference': True}

bot = TradingBot()

strategy = TestStrategy
# strategy_parameters = {
#     'period_me1': 12, 'logging': False, 'stop_loss': 1, 'risk_reward': range(1, 5)
# }

strategy_parameters = {}

sizer = bt.sizers.PercentSizer
sizer_parameters = {
    'percents': 99
}

analyzers = [
    bt.analyzers.TradeAnalyzer
    ]

live_parameters = {
    'dataname': 'BTC/USDT',
}
bot.live(strategy, live_parameters, store=store2, strategy_parameters=strategy_parameters, sizer=sizer,
         sizer_parameters=sizer_parameters, analyzers=analyzers)
         