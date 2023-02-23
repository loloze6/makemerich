import configparser

class GetAPIKeys():
    def __init__(self) -> None:
        self.temp= None 
        self.config = dict()
    def getAPIkeys(self, sandbox=True):
        self.temp = configparser.ConfigParser()
        self.temp.read('Account_management/APIKEYS.ini')
        if sandbox==False:
            self.config['User']=self.temp['LIVE']['BINANCE_USER']
            self.config['Password']=self.temp['LIVE']['BINANCE_PASSWORD']
        elif sandbox==True:
            self.config['User']=self.temp['TEST']['BINANCE_USER']
            self.config['Password']=self.temp['TEST']['BINANCE_PASSWORD']
    # Print the balance
        return(self.config)
    
classAPI=GetAPIKeys()
classAPI.getAPIkeys(sandbox=True)