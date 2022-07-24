import csv
import json
from typing import Optional, final
from tqdm.auto import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
import pymongo
import numpy as np


MAX_ROWS: final = 50000
ORIGINAL_DATASET_DIR: final = "D:\\datasets\\spanish_train\\renfe.csv"
ORIGINAL_DATASET_DIR_JSON: final = "D:\\datasets\\spanish_train\\renfe.json"
CLEANED_DATASET_DIR_JSON: final = "D:\\datasets\\spanish_train\\cleaned_renfe.json"
CONNECTION_STRING: final = "mongodb+srv://Attornado:andrea22@cluster0.t3es8fi.mongodb.net/?retryWrites=true&w=majority"
PLOT_DIR: final = "plots/"
DB_NAME: final = "TrainTickets"
COLLECTION_NAME: final = "Tickets"
FONTSIZE_PLOT_CATEGORICAL: final = 8
ROTATION_PLOT_CATEGORICAL: final = 15
FONTSIZE_PLOT_NUMERICAL: final = 11
ROTATION_PLOT_NUMERICAL: final = 0
MODE: final = 'mode'
MEAN: final = 'mean'
MEDIAN: final = 'median'
QUANTILES: final = 'quantiles'


def csv_to_json(path: str, export_path: Optional[str] = None, add_id: bool = False):
    """
    Converts csv file to json format, adding an id and exporting it to file if required.

    :param path: path of the csv file to convert.
    :param export_path: optional export path for the generated json.
    :param add_id: a boolean indicating whethever or not to add an
        auto-increment id field to the csv.
    :return a json string representing the csv content.
    """
    data = []

    # Read the csv
    with open(path, encoding='utf-8') as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)
        print(csv_reader)

        # For each row
        auto_increment_id = 0
        for row in csv_reader:
            # Convert row to dictionary
            dict_row = dict(row)

            # Add an id field if required
            if add_id:
                dict_row['id'] = auto_increment_id

            # Add row to final collection
            data.append(dict_row)
            auto_increment_id += 1
            print(f"Done: {auto_increment_id}")

            if auto_increment_id > MAX_ROWS:
                print("Reached max row limit. Exiting from reading.")
                break

    # Convert generated data to json
    json_data = json.dumps(data, indent=4)

    # Export to json file if required
    if export_path is not None:
        with open(export_path, 'w', encoding='utf-8') as json_file_handler:
            # Step 4
            json_file_handler.write(json_data)
            print("JSON file exported.")

    return json_data


def load_json(path: str) -> dict:
    """
    Loads json file from given path, converting it to a dictionary.

    :param path: path to the json file from.
    :return: dictionary containing data matching the content of the given json file.
    """

    with open(path, 'r', encoding='utf-8') as json_file:
        json_dict = json.load(json_file)
    return json_dict


def clear_dataframe(df: pd.DataFrame, undesired_columns: Optional[list[str]] = None) -> pd.DataFrame:
    """
    Removes given undesired columns and any row having null/empty/nan values from the given dataframe.

    :param df: dataframe to remove the null/empty/nan values from.
    :param undesired_columns: list of columns to remove from the given dataframe (default: None).
    :return: a dataframe with rows having null/empty/nan values removed (although operation is done in-place).
    """

    # Remove undesired columns
    if undesired_columns is None:
        df.drop(columns=undesired_columns, inplace=True)

    # Remove null/empty/nan values
    for column in tqdm(df.columns, desc="Removing null/empty/nan values"):
        df[column].replace('', np.nan, inplace=True)
        df.dropna(subset=[column], inplace=True)

    return df


def json_to_dataframe(path: str) -> pd.DataFrame:
    """
    Loads json file from the given path and returns it as a dataframe.

    :param path: path to the json file from.
    :return: dataframe containing data matching the content of the given json file.
    """
    df = pd.read_json(path)
    return df


def plot_stats(df: pd.DataFrame, column: str, categorical: bool = False, save_path: Optional[str] = None,
               show_plot: bool = True):
    """
    Plots and returns stats for the given column of the given dataframe. For categorical data, only mode is computed as
    stat and only barplot is performed, while for numerical data, both boxplot and histogram are computed, alongside
    mode, mean, median and 4-quantiles.

    :param df: dataframe to plot stats for.
    :param column: column to plot stats for.
    :param categorical: whatever or not the given column is categorical.
    :param save_path: path to store the plots into.
    :param show_plot: whatever or not to show the plots of the given columns.
    :return:
    """
    stats = {}
    if categorical:
        # Barplot
        column_value_counts = df[column].value_counts()
        ax = column_value_counts.plot.bar(x=column, y='count', rot=0)
        plt.setp(ax.get_xticklabels(), fontsize=FONTSIZE_PLOT_CATEGORICAL, rotation=ROTATION_PLOT_CATEGORICAL)

        # Show and store plot if required
        if save_path is not None:
            plt.savefig(save_path, format='svg')
        if show_plot:
            plt.show()

    else:
        # Histogram
        ax = df[column].astype(np.float32).plot.hist(x=column, y='Frequency', rot=0, bins=10)
        plt.setp(ax.get_xticklabels(), fontsize=FONTSIZE_PLOT_CATEGORICAL, rotation=ROTATION_PLOT_CATEGORICAL)

        # Show and store plot if required
        if save_path is not None:
            plt.savefig(save_path, format='svg')
        if show_plot:
            plt.show()

        # Boxplot
        df[column].astype(np.float32).to_frame().boxplot(rot=0)

        # Show and store plot if required
        if save_path is not None:

            # Add "_boxplot" suffix to save path name
            if save_path.find("."):
                name = save_path.split('.')[0]
                extension = save_path.split('.')[1]
                save_path = f"{name}_boxplot.{extension}"
            else:
                save_path = save_path + "_boxplot"
            plt.savefig(save_path, format='svg')
        if show_plot:
            plt.show()

    # Store mode into stats dictionary
    stats[MODE] = df[column].mode().iloc[0]

    if not categorical:
        # Store mean into stats dictionary
        stats[MEAN] = df[column].astype(np.float32).mean()

        # Store median into stats dictionary
        stats[MEDIAN] = df[column].astype(np.float32).median()

        # Quantiles
        stats[QUANTILES] = df[column].astype(np.float32).quantile([0, 0.25, 0.5, 0.75, 1])

    return stats


def change_values(df: pd.DataFrame, column_alternatives: dict[str, list], n_changes: int = 0) -> pd.DataFrame:
    """
    Changes some (randomly selected, and up to n_changes) dataframe values in the given columns with the given values
    (chosen randomly) to improve the data variance.

    :param df: the dataframe to change values of.
    :param column_alternatives: a dictionary mapping each to-change column into a list of possible alternative values.
    :param n_changes: max number of columns to change values of.
    :return: a dataframe obtained from df changes up to n_changes row values in the columns corresponding to the given
        column_alternatives keys, and values corresponding to column_alternatives values.
    """
    if n_changes == 0:
        n_changes = int(len(df) / 2)

    # Setup loop variables
    change_count = 0
    already_changed = set()

    # Generate random indexes to change values of, while enough changes are done
    while change_count < n_changes:

        # Generate random index
        random_df_index = np.random.randint(low=0, high=len(df))

        # If generated index was not generated yet
        if random_df_index not in already_changed:

            # Change values for each given column with the given possible values
            for column in column_alternatives:
                random_value = np.random.choice(column_alternatives[column])
                df.loc[random_df_index, column] = random_value

            # Increment change count and add index to already changed ones
            already_changed.add(random_df_index)
            change_count += 1

    return df


def main():
    convert = int(input("Convert csv to json (1: yes, 0: no)? "))

    # Load or create json dataset
    if convert != 0:
        csv_path = ORIGINAL_DATASET_DIR
        json_dict = csv_to_json(csv_path, export_path=ORIGINAL_DATASET_DIR_JSON, add_id=True)
    else:
        json_dict = load_json(ORIGINAL_DATASET_DIR_JSON)

    # Convert json to dataframe
    df = json_to_dataframe(ORIGINAL_DATASET_DIR_JSON)
    df = clear_dataframe(df, undesired_columns=['insert_date'])

    # Convert price to float
    df['price'] = df['price'].astype(np.float32)

    # Change some values to improve variance
    change_values(df, column_alternatives={'origin': ["VALENCIA", "SEVILLA"], "destination": ["BARCELONA", "MADRID"]},
                  n_changes=0)

    print(df.info())
    print(df['origin'].value_counts())

    print(plot_stats(df, 'origin', categorical=True, save_path=PLOT_DIR + "origin.svg", show_plot=True))
    print(plot_stats(df, 'destination', categorical=True, save_path=PLOT_DIR + "destination.svg", show_plot=True))
    print(plot_stats(df, 'train_type', categorical=True, save_path=PLOT_DIR + "train_type.svg", show_plot=True))
    print(plot_stats(df, 'train_class', categorical=True, save_path=PLOT_DIR + "train_class.svg", show_plot=True))
    print(plot_stats(df, 'fare', categorical=True, save_path=PLOT_DIR + "fare.svg", show_plot=True))
    print(plot_stats(df, 'price', categorical=False, save_path=PLOT_DIR + "price.svg", show_plot=True))

    print(df['destination'].value_counts())
    print(df['train_type'].value_counts())
    print(df['train_class'].value_counts())
    print(df['fare'].value_counts())

    connect = int(input("Connect to database (1: yes, 0: no)? "))

    # Maybe do not delete price column because if wrong price is given then the ticket validator would check ticket
    # price on the contract and invalidate it?

    if connect != 0:
        # Create connection
        client = MongoClient(CONNECTION_STRING)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        collection.insert_one(json_dict[1])


if __name__ == '__main__':
    main()
