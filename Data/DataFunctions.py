import backtrader as bt
import ccxt
import pandas as pd
#dateFormat '2018-01-01T00:00:00Z'
def fetchData(token,barDuration, start= None, duration= 1000):
# Step 1: Create an exchange object and load market data
    result=dict()
    exchange = ccxt.binance()
    startformat=exchange.parse8601(start)
    ohlcv = exchange.fetch_ohlcv(token, timeframe=barDuration, since=startformat, limit=duration)
# Step 2: Convert data to pandasa DataFrame
    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    durationData=data.index.max()-data.index.min()
    result['Duration']=durationData    
    data = bt.feeds.PandasData(dataname=data)
    result['BT_DataFeed']=data    
    return result

# STEP 2: FETCH THE CURRENT DATA WITH "fetch_ticker"
def fetch_current_data(ticker):
    exchange = ccxt.binance()
    bars,ticker_df = None, None
    try:
        bars = exchange.fetch_ticker(ticker)
    except:
        print(f"Error in fetching current data from the exchange:{ticker}")
    if bars is not None:
        ticker_df = bars
    return ticker_df


# STEP 3: FETCH THE CURRENT BALANCE IN BINANCE
def fetch_current_balance():
    exchange = ccxt.binance()
    balance, balance_df= None, dict()
    try:
        balance = exchange.fetch_balance()
    except:
        print(f"Error in fetching current balance from the exchange")
    if balance is not None:
        for key, value in balance['free'].items():
            if float(value)>0:
                balance_df[key]=value
    return balance_df

# STEP 4: GET ALL MARKETS"
def fetch_all_token(tradedWith='USDT', number=10):
    exchange = ccxt.binance()
    TradedWith='/'+tradedWith
    all_token=[]
    markets=exchange.load_markets()
    numb=0
    for item in markets:
        if numb == number:
            break
        if item.endswith(TradedWith):
            all_token.append(item)
            numb += 1
    return all_token
