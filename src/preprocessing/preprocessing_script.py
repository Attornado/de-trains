import json
from typing import final
from pymongo import MongoClient
import numpy as np
from src.preprocessing.utils import PLOT_DIR, csv_to_json, load_json, clear_dataframe, json_to_dataframe, plot_stats, \
    change_values


DB_NAME: final = "TrainTickets"
COLLECTION_NAME: final = "Tickets"
ORIGINAL_DATASET_DIR: final = "D:\\datasets\\spanish_train\\renfe.csv"
ORIGINAL_DATASET_DIR_JSON: final = "D:\\datasets\\spanish_train\\renfe.json"
CLEANED_DATASET_DIR_JSON: final = "D:\\datasets\\spanish_train\\cleaned_renfe.json"
CONNECTION_STRING: final = "mongodb+srv://Attornado:andrea22@cluster0.t3es8fi.mongodb.net/?retryWrites=true&w=majority"
_MAX_ROWS: final = 50000


def main():
    convert = int(input("Convert csv to json (1: yes, 0: no)? "))

    # Load or create json dataset
    if convert != 0:
        csv_path = ORIGINAL_DATASET_DIR
        json_dict = csv_to_json(csv_path, export_path=ORIGINAL_DATASET_DIR_JSON, add_id=True, max_rows=_MAX_ROWS)
    else:
        json_dict = load_json(ORIGINAL_DATASET_DIR_JSON)

    # Convert json to dataframe
    df = json_to_dataframe(ORIGINAL_DATASET_DIR_JSON)
    df = clear_dataframe(df, undesired_columns=['insert_date'])

    # Convert price to float
    df['price'] = df['price'].astype(np.float32)

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
        client = MongoClient(CONNECTION_STRING)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Convert dataframe to json
        df_json = df.to_json(orient='records')

        # Insert values into db
        collection.insert_many(json.loads(df_json))


if __name__ == '__main__':
    main()
