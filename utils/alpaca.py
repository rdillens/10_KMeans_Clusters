import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
load_dotenv()


# Set the variables for the Alpaca API and secret keys
alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')
endpoint = "https://api.alpaca.markets"
# Create the Alpaca tradeapi.REST object
alpaca = tradeapi.REST(alpaca_api_key, alpaca_secret_key, base_url=endpoint, api_version='v2')

class Asset:
    def __init__(self):
        self.asset_class = None
        self.exchange = None
        self.fractionable = None
        self.id = None
        self.marginable = None
        self.min_order_size = None
        self. min_trade_increment = None
        self.name = None
        self.price_increment = None
        self.shortable = None
        self.status = None
        self.symbol = None
        self.tradable = None
        

def run():
    alpaca.list_assets()
    account = alpaca.get_account()
    # print(account)
    active_assets = alpaca.list_assets(status='active')
    print(active_assets[0])
    print(active_assets[0]._raw['exchange'])
    exchange_list = list(set([asset._raw['exchange'] for asset in active_assets]))
    asset_class_list = list(set([asset._raw['class'] for asset in active_assets]))
    print(exchange_list)
    print(asset_class_list)
    crypto_exchange_list = list(set([asset._raw['exchange'] for asset in active_assets if asset._raw['class'] == 'crypto']))
    print(crypto_exchange_list)
    us_equity_exchange_list = list(set([asset._raw['exchange'] for asset in active_assets if asset._raw['class'] == 'us_equity']))
    print(us_equity_exchange_list)
    # for i in active_assets[0]:
    #     print(i)
if __name__ == "__main__":
    run()