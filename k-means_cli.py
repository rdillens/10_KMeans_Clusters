# Python native libraries
from statistics import mean
from time import sleep
from numpy import sort
import logging

# Conda libraries
import pandas as pd
# from sklearn.cluster import KMeans
# from sklearn.decomposition import PCA

# External libraries
from fire import Fire
import questionary

# Local libraries
from utils.alpaca import alpaca as alp
import utils.helpers as hf

def run(exchange=None, max_k=None):
    # Choose Exchange if not given from command line
    if exchange is None:
        exchange = questionary.select(
            message="Exchange",
            choices=hf.exchange_list,
        ).ask()
    logging.debug(exchange)
    # Convert column names to strings
    table = hf.stringify_table_headers(
        pd.read_sql_table(
            table_name=exchange, 
            con=hf.engine, 
            index_col='index',
        ).dropna()
    )
    # Choose columns to remove from process
    cols_to_drop = questionary.checkbox(
        message="Select columns to drop",
        choices=list(table.columns),
    ).ask()
    logging.debug(f"dropping columns: {cols_to_drop}")
    # Drop columns and scale data
    scaled_df = hf.scale_data(table.drop(columns=cols_to_drop))
    logging.debug(f"columns: {list(scaled_df.columns)}")
    # Prompt for maximum k clusters if not given from command line
    if max_k is None:
        max_k = int(questionary.text(
            message="Max K Clusters",
            default="10",
            validate=lambda text: text.isdigit(),
        ).ask())
    k_range = list(range(2,max_k+1))
    logging.info(f"Calculate clusters from k={min(k_range)} to {max(k_range)}")
    k_list = []
    for i, j in enumerate(k_range):
        k_list.append(hf.run_k(scaled_df, j))
        print(f"k:{k_list[i]['k']} inertia:{k_list[i]['inertia']}")
        scaled_df[k_list[i]['col_name']] = k_list[i]['clusters']
        value_counts = scaled_df[k_list[i]['col_name']].value_counts().sort_index()
        value_counts.index.names = ['cluster']
        value_counts = pd.DataFrame(value_counts)
        value_counts.columns = ['count']

        print("Value Counts:\n", value_counts, value_counts.describe())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    Fire(run)
