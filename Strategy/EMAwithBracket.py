from backtrader.indicators import MACD as MACD
from backtrader.indicators import CrossOver as CrossOver
from backtrader.indicators import ExponentialMovingAverage as EMA
from Indicator.Doji_indicator import Doji

from Strategy.Base_Bracket_Orders import BracketStrategy

class EMAStrategyExample(BracketStrategy):

    # First, you define some parameters
    params = (
        
        #For MACD
        ('period_me1', 12),
        ('period_me2', 26),
        ('period_signal', 9),
        
        #For EMA
        ('trend_ema_period', 100),
        ('movav', EMA),
        
        #For DOJI
        ('doji_threshold', 5),
        
        #Others
        ('logging', True),
    )

    # Then, you initialize indicators
    def _init_indicators(self):
        
        #For MACD
        self.macd = MACD(period_me1=self.p.period_me1, period_me2=self.p.period_me2, period_signal=self.p.period_signal,
                         movav=self.p.movav)
        self.cross = CrossOver(self.macd.macd, self.macd.signal)
        
        #For EMA
        self.ema = EMA(period=self.p.trend_ema_period)

        #For DOJI
        self.doji = Doji(threshold_percent=self.p.doji_threshold)

    # Finally, you implement your open conditions
    # Closing is done with stop loss or take profit
    def _open_long_condition(self) -> bool:
        
        #If Doji appearing (True) as condition
        if self.doji.is_doji[0]:
        
        #If EMA is below price
            if self.ema[0] < self.datas[0].close[0]:
        
        #If EMA cross up (1) as condition
        #if self.cross[0] == 1:
            
        ###
                return True
        return False
    
    def _open_short_condition(self) -> bool:
        if self.ema[0] > self.datas[0].close[0] and self.cross[0] == -1:
            return True
        return False
    
    def _close_long_condition(self):
        if self.cross[0] == -1:    
        ###
            return True
        return False
    
    # def _log(self, txt):
    #     if self.p.logging:
    #         try:
    #             print(f"{self.datas[0].datetime.datetime(0)}: {txt}")
    #         except:
    #             print(f"{datetime.now()}: {txt}")