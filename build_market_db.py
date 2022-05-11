import datetime as dt
from time import sleep

import pandas as pd
import sqlalchemy

from utils.alpaca import alpaca as alp

database_connection_string = 'sqlite:///test_db.db'
engine = sqlalchemy.create_engine(database_connection_string)

active_assets = alp.list_assets(status='active')
active_assets_df = pd.DataFrame([asset._raw for asset in active_assets if asset._raw['tradable'] == True])
active_assets_df = active_assets_df.loc[lambda df: (df['class'] == 'us_equity')]
active_assets_df.drop(columns=['id', 'name', 'class', 'status', 'tradable', 'min_order_size', 'min_trade_increment', 'price_increment'], inplace=True)
active_assets_df.drop(columns=['marginable', 'shortable', 'easy_to_borrow', 'fractionable'], inplace=True)

exchange_list = active_assets_df['exchange'].unique().tolist()

today = dt.datetime.now()
offset = max(1, (today.weekday() + 6) % 7 -3)
timedelta = dt.timedelta(offset)
most_recent = today - timedelta
numdays=365
oldest_date = most_recent - dt.timedelta(days=numdays)

def get_last_price(symbol):
    return alp.get_bars(
        symbol=symbol,
        timeframe='1D', 
        # limit=100, 
        end=str(most_recent.date()),
        start=str(oldest_date.date()),
    ).df

stock_dict = {}
pop_set = {'OTC','BATS', 'ARCA'}
exchange_set = set(exchange_list)
exchange_set = exchange_set.difference(pop_set)
exchange_list = list(exchange_set)
periods_dict = {
    "pct_chg_24_hour": 1, 
    "pct_chg_1_week": 5,
    "pct_chg_1_month": 21,
    "pct_chg_3_months": 63,
    "pct_chg_6_months": 126,
    "pct_chg_1_year": 252,
    }

for exchange in exchange_list:
    stock_list = list(active_assets_df.loc[lambda df: (df['exchange'] == exchange)]['symbol'])
    stock_dict[exchange] = pd.DataFrame()
    for i, symb in enumerate(stock_list[:]):
        sleep(.25)
        print(f"\r{i}/{len(stock_list)} {symb}", end='')
        bars_df = get_last_price(symb)
        drop_cols=['open', 'high', 'low', 'volume', 'trade_count', 'vwap']
        
        try:
            bars_df = pd.DataFrame(bars_df.loc[:, 'close'])
        except Exception as e:
            print(f"Exception {e} for {symb} bars_df")
        else:
            for k, v in periods_dict.items():
                temp_df = pd.DataFrame(bars_df.loc[:,'close'].pct_change(periods=v))
                temp_df.rename(columns={'close':k}, inplace=True)
                bars_df = bars_df.join(temp_df, how='outer')
            price_hist_row = pd.DataFrame(bars_df.iloc[-1])
            price_hist_row.rename(columns={bars_df.index[-1]: symb}, inplace=True)
            try:
                stock_dict[exchange] = stock_dict[exchange].join(price_hist_row.T, how='outer')
            except ValueError:
                try:
                    stock_dict[exchange] = pd.concat([stock_dict[exchange], price_hist_row.T], join='outer')
                except Exception as e:
                    print(f"Exception: {e}")

for exchange in exchange_list:
    stock_dict[exchange].to_sql(exchange, engine)