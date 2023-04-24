import ccxt
from Account_management.GetAPIKeys import GetAPIKeys
def initiate_exchange(exchange='binance', sandbox=True):
    credential = GetAPIKeys().getAPIkeys(exchange, sandbox)
    api_key = credential['User']
    api_secret = credential['Password']
    if exchange=='binance':
        exchange=ccxt.binance()
    elif exchange=='bybit':
        exchange=ccxt.bybit()
    else:
        return('Exchange not supported')
    exchange.set_sandbox_mode(sandbox)
    exchange.apiKey=api_key
    exchange.secret=api_secret
    exchange.options = {'adjustForTimeDifference': True,
                        'newOrderRespType': 'FULL',
                        'defaultTimeInForce': 'GTC',
                        'timeDifference': 0,
                        'recvWindow': 5*1000
                        }
    return exchange

def convertAllToToken(exchange='binance', sandbox=True, token='USDT'):
    exchange=initiate_exchange(exchange, sandbox)
    balance= exchange.fetch_balance()
    markets=exchange.loadMarkets()
    basecoin=token
    for key, value in balance['free'].items():
        if key!=basecoin and value > 0:
            market=key+'/'+basecoin
            try:
                if exchange=='binance':
                    for items in markets[market]['info']['filters']:
                        if items['filterType']=='MARKET_LOT_SIZE':
                            maxvalue=float(items['maxQty'])
                            if value>maxvalue: value=maxvalue
                            transaction=exchange.create_order(market, type='market', side='sell', amount=value)
                            print ('For {} - Transaction {} of {} {} at {} {}'.format(market, transaction['status'], transaction['filled'],key,transaction['average'], basecoin))    
                
                else:
                    transaction=exchange.create_order(market, type='market', side='sell', amount=value)
                    print ('For {} - Transaction {} of {} {} at {} {}'.format(market, transaction['status'], transaction['filled'],key,transaction['average'], basecoin))
            
            except Exception as e:
                print ('For {} - Transaction could not be completed due to error: {}'.format(market, e))
    newBalance= exchange.fetch_balance()
    print(newBalance['free'])
    



exchange='binance'
sandbox=True
exchange=initiate_exchange(exchange, sandbox)

exchange.fetch_balance()

exchange.cancel_all_orders('BTC/USDT')
exchange.fetch_open_orders('BTC/USDT')


print(exchange.load_markets()['BTC/USDT'].keys())
print(exchange.load_markets()['BTC/USDT']['info'])

exchange.create_order(symbol='BTC/USDT', type='MARKET', side='buy',
                                          amount=0.190127)

exchange.create_order(symbol='BTC/USDT', type='LIMIT', side='sell',
                                          amount=0.190127, price=27374)

exchange.create_order(symbol='BTC/USDT', type='STOP_LOSS_LIMIT', side='sell',
                                          amount=0.190127, price=22374, params={'stopPrice': 22374})


exchange.create_order(symbol='BTC/USDT', type='LIMIT', side='sell', price=22000, amount=0.1)

exchange.private_post_order_oco({ "symbol": "BTCUSDT", "side": "buy", "quantity": 0.002, "price": 33374, "stopPrice": 21000, "stopLimitPrice": 21000, "stopLimitTimeInForce": "GTC"})

convertAllToToken('binance', sandbox, 'USDT')



