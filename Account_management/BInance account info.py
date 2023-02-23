import ccxt
from Account_management.GetAPIKeys import GetAPIKeys

def initiate_exchange(sandbox=True):
    credential = GetAPIKeys().getAPIkeys(sandbox)
    binance_api_key = credential['User']
    binance_api_secret = credential['Password']

    exchange=ccxt.binance()
    exchange.set_sandbox_mode(sandbox)
    exchange.apiKey=binance_api_key
    exchange.secret=binance_api_secret
    exchange.options = {'adjustForTimeDifference': True,
                        'newOrderRespType': 'FULL',
                        'defaultTimeInForce': 'GTC'}
    return exchange

#Not perfect, can fail due to limits
def convertAllToToken(sandbox=True, token='USDT'):
    exchange=initiate_exchange(sandbox)
    balance= exchange.fetch_balance()
    markets=exchange.loadMarkets()
    basecoin=token
    for key, value in balance['free'].items():
        if key!=basecoin and value > 0:
            market=key+'/'+basecoin
            try:
                for items in markets[market]['info']['filters']:
                    if items['filterType']=='MARKET_LOT_SIZE':
                        maxvalue=float(items['maxQty'])
                if value>maxvalue: value=maxvalue
                transaction=exchange.create_order(market, type='market', side='sell', amount=value)
                print ('For {} - Transaction {} of {} {} at {} {}'.format(market, transaction['status'], transaction['filled'],key,transaction['average'], basecoin))
            except Exception as e:
                print ('For {} - Transaction could not be completed due to error: {}'.format(market, e))
    newBalance= exchange.fetch_balance()
    print(newBalance['free'])
    

convertAllToToken(sandbox=True, token='USDT')




exchange=initiate_exchange(sandbox=True)
exchange.fetch_balance()
