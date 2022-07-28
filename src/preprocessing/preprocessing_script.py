import json
from typing import final
import numpy as np
import pandas as pd
from src.db_utils import DB_NAME, COLLECTION_NAME, CONNECTION_STRING, get_db_connection
from src.preprocessing.utils import PLOT_DIR, csv_to_json, load_json, remove_columns, json_to_dataframe, plot_stats, \
    change_values, drop_null_values


# Load dataset path
with open("src/configurations.json") as file:
    config = json.load(file)
    ORIGINAL_DATASET_DIR: final = config['dataset_path']  # load dataset path
    ORIGINAL_DATASET_DIR_JSON: final = config['dataset_json_original']
    CLEANED_DATASET_DIR_JSON: final = config["dataset_json_cleaned"]

# ORIGINAL_DATASET_DIR: final = "D:\\datasets\\spanish_train\\renfe.csv"
# ORIGINAL_DATASET_DIR_JSON: final = "D:\\datasets\\spanish_train\\renfe.json"
# CLEANED_DATASET_DIR_JSON: final = "D:\\datasets\\spanish_train\\cleaned_renfe.json"
_MAX_ROWS: final = 50000


def main():
    convert = int(input("Convert csv to json (1: yes, 0: no)? "))
    csv_path = ORIGINAL_DATASET_DIR

    # Load or create json dataset
    if convert != 0:
        json_dict = csv_to_json(csv_path, export_path=ORIGINAL_DATASET_DIR_JSON, add_id=True, max_rows=_MAX_ROWS)
    else:
        json_dict = load_json(ORIGINAL_DATASET_DIR_JSON)

    load_from_csv = int(input("Load dataframe directly from csv (1: yes, 0: no)? "))
    if load_from_csv != 0:
        # Load dataframe from csv
        df = pd.read_csv(ORIGINAL_DATASET_DIR)
    else:
        # Convert json to dataframe
        df = json_to_dataframe(ORIGINAL_DATASET_DIR_JSON)

    # Clean-up the dataset and add id column
    df['id'] = np.arange(start=0, stop=len(df))
    df = remove_columns(df, undesired_columns=['insert_date'])
    df = drop_null_values(
        df,
        columns=['origin', 'destination', 'train_type', 'train_class', 'fare', 'start_date', 'end_date', 'price']
    )
    # df = estimate_null_values(df, columns=['price'])

    # Convert price to float
    df['price'] = df['price'].astype(np.float32)

    # Change year in the date column to next year
    df['start_date'] = df['start_date'].replace(to_replace="2019", value="2023", regex=True)
    df['end_date'] = df['end_date'].replace(to_replace="2019", value="2023", regex=True)

    change = int(input("Change values to improve variance (1: yes, 0: no)? "))
    if change != 0:
        # Change some values to improve variance
        change_values(
            df=df,
            column_alternatives={'origin': ["VALENCIA", "SEVILLA"], "destination": ["BARCELONA", "MADRID"]},
            n_changes=0
        )

    # Plot stats
    print(df.info())
    print(plot_stats(df, 'origin', categorical=True, save_path=PLOT_DIR + "origin.svg", show_plot=True))
    print(plot_stats(df, 'destination', categorical=True, save_path=PLOT_DIR + "destination.svg", show_plot=True))
    print(plot_stats(df, 'train_type', categorical=True, save_path=PLOT_DIR + "train_type.svg", show_plot=True))
    print(plot_stats(df, 'train_class', categorical=True, save_path=PLOT_DIR + "train_class.svg", show_plot=True))
    print(plot_stats(df, 'fare', categorical=True, save_path=PLOT_DIR + "fare.svg", show_plot=True))
    print(plot_stats(df, 'price', categorical=False, save_path=PLOT_DIR + "price.svg", show_plot=True))

    # Connection handling
    connect = int(input("Connect to database (1: yes, 0: no)? "))

    # Maybe do not delete price column because if wrong price is given then the ticket validator would check ticket
    # price on the contract and invalidate it?

    if connect != 0:
        # Create connection
        collection = get_db_connection(CONNECTION_STRING, DB_NAME, COLLECTION_NAME)

        # Convert dataframe to json
        df_json = df.sample(n=_MAX_ROWS, axis=0).to_json(orient='records')

        # Insert values into db
        collection.insert_many(json.loads(df_json))


if __name__ == '__main__':
    main()
