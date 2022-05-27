from pathlib import Path
import logging
from numpy import sort
import sqlalchemy
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# logging.basicConfig(filename='helper_log.txt', level=logging.DEBUG)
# logging.captureWarnings(capture=True)

shelf_path = "data"
shelf_name = "shelf"
shelf = shelf_path + "/" + shelf_name

database_connection_string = 'sqlite:///market_db.db'
engine = sqlalchemy.create_engine(database_connection_string)
exchange_list = sort(sqlalchemy.inspect(engine).get_table_names())

def create_directory(filepath):
    if not Path(filepath).is_dir():
        logging.info(f"Creating shelf directory {filepath}")
        Path(filepath).mkdir(parents=True, exist_ok=True)

def stringify_table_headers(table):
    features = []
    for feature in list(table.columns):
        features.append(str(feature))
    table.columns = features
    return table

def scale_data(table):
    scaled_data = StandardScaler().fit_transform(table)
    scaled_df = pd.DataFrame(
        scaled_data,
        columns=table.columns,
    )
    scaled_df['ticker'] = table.index
    scaled_df = scaled_df.set_index('ticker')
    return scaled_df    

def clean_table(table):
    # Fix FutureWarning by converting column headers to strings
    # FutureWarning: Feature names only support names that are all strings. Got feature names with dtypes: ['quoted_name']. An error will be raised in 1.2.
    features = []
    for feature in list(table.columns):
        features.append(str(feature))
    table.columns = features
    # Scale data
    scaled_data = StandardScaler().fit_transform(table)
    # Create DataFrame
    scaled_df = pd.DataFrame(
        scaled_data,
        columns=features,
    )
    scaled_df['ticker'] = table.index
    scaled_df = scaled_df.set_index('ticker')
    return scaled_df

def run_k(df, k):
    model = KMeans(n_clusters=k, random_state=0)
    model.fit(df)
    k_dict = {
        'k': k,
        'inertia': model.inertia_,
        'clusters': model.predict(df),
        'col_name': f"cluster_k{k}"
    }
    return k_dict
