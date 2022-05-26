# Python native libraries
from statistics import mean
import datetime as dt
# from path import Path
from time import sleep
from numpy import sort
# import sqlalchemy
import logging

# Conda libraries
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
# from bokeh.models import HoverTool

# External libraries
# import mplfinance as mpf
# import hvplot.pandas
from fire import Fire
import questionary

# Local libraries
from utils.alpaca import alpaca as alp
import utils.helpers as hf


def run():
    exchange = questionary.select(
        message="Exchange",
        choices=hf.exchange_list,
    ).ask()
    logging.debug(exchange)
    table = hf.stringify_table_headers(
        pd.read_sql_table(
            table_name=exchange, 
            con=hf.engine, 
            index_col='index',
        ).dropna()
    )
    cols_to_drop = questionary.checkbox(
        message="Select columns to drop",
        choices=list(table.columns),
    ).ask()
    logging.debug(f"dropping columns: {cols_to_drop}")
    scaled_df = hf.scale_data(table.drop(columns=cols_to_drop))
    logging.debug(f"columns: {list(scaled_df.columns)}")
    max_k = int(questionary.text(
        message="Max K Clusters",
        default="10",
        validate=lambda text: text.isdigit(),
    ).ask())
    k_range = list(range(2,max_k))
    inertia=[]
    for i in k_range:
        model = KMeans(n_clusters=i, random_state=0)
        model.fit(scaled_df)
        inertia.append(model.inertia_)
    elbow_dict =         {
            'k': k_range,
            'inertia': inertia,
        }
    elbow_df = pd.DataFrame(elbow_dict)
    # print(elbow_df)
    # elbow_df = elbow_df.assign(choice_string=lambda df: str(df['k']) + str(df['inertia']))
    choice_list = []
    for i in elbow_df.index:
        choice_string = f"k: {elbow_df.iloc[i]['k']:.0f} inertia: {elbow_df.iloc[i]['inertia']}"
        choice_list.append(choice_string)
    selected_k = round(elbow_df.iloc[choice_list.index(questionary.select("Choose K", choices=choice_list).ask())]['k'])
    logging.debug(selected_k)
    model = KMeans(n_clusters=selected_k, random_state=0)
    model.fit(scaled_df)
    clusters = model.predict(scaled_df)
    scaled_df['cluster'] = clusters
    logging.info(scaled_df.columns.tolist())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    Fire(run)
