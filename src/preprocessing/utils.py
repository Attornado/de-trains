import csv
import json
from typing import final, Optional
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tqdm.auto import tqdm


PLOT_DIR: final = "plots/"
_FONTSIZE_PLOT_CATEGORICAL: final = 8
_ROTATION_PLOT_CATEGORICAL: final = 15
_FONTSIZE_PLOT_NUMERICAL: final = 11
_ROTATION_PLOT_NUMERICAL: final = 0
MODE: final = 'mode'
MEAN: final = 'mean'
MEDIAN: final = 'median'
QUANTILES: final = 'quantiles'
VARIANCE: final = 'var'
STANDARD_DEVIATION: final = 'sd'


def csv_to_json(path: str, export_path: Optional[str] = None, add_id: bool = False, max_rows: int = -1):
    """
    Converts csv file to json format, adding an id and exporting it to file if required.

    :param path: path of the csv file to convert.
    :param export_path: optional export path for the generated json.
    :param add_id: a boolean indicating whatever or not to add an
        auto-increment id field to the csv.
    :param max_rows: maximum number of rows to read from the csv file (default is -1, which means no limit).
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

            if (max_rows > -1) and (auto_increment_id > max_rows):
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


def remove_columns(df: pd.DataFrame, undesired_columns: Optional[list[str]]) -> pd.DataFrame:
    """
    Removes given undesired columns and any row having null/empty/nan values from the given dataframe.

    :param df: dataframe to remove the columns from.
    :param undesired_columns: list of columns to remove from the given dataframe (default: None).
    :return: a dataframe identical to the given one, but without the given columns.
    """

    # Remove undesired columnsì
    df.drop(columns=undesired_columns, inplace=True)

    return df


def drop_null_values(df: pd.DataFrame, columns=None):
    """
    Removes any row having null/empty/nan values in the given columns from the given dataframe.

    :param df: dataframe to remove the null/empty/nan values from.
    :param columns: list of columns to remove the null/empty/nan values from (default: None, which means all columns).
    :return: a dataframe with rows having null/empty/nan values in the given columns removed (although operation is done
        in-place).
    """
    if columns is None:
        columns = df.columns

    # Remove null/empty/nan values
    for column in tqdm(columns, desc="Removing null/empty/nan values"):
        df[column].replace('', np.nan, inplace=True)
        df.dropna(subset=[column], inplace=True)
    return df


'''
def estimate_null_values(df: pd.DataFrame, columns=None, metric: str = 'mode'):
    """
    Replaces null/empty/nan values from the given dataframe with metrics.

    :param df: dataframe to remove the null/empty/nan values from.
    :param columns: list of columns to remove the null/empty/nan values from (default: None, which means all columns).
    :param
    :return: a dataframe with rows having null/empty/nan values in the given columns removed (although operation is done
        in-place).
    """
    if columns is None:
        columns = df.columns

    # Remove null/empty/nan values
    for column in tqdm(columns, desc="Removing null/empty/nan values"):
        df[column].replace('', np.nan, inplace=True)
        df.dropna(subset=[column], inplace=True)
    return df
'''


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
    mode, mean, median, 4-quantiles, standard deviation and variance.

    :param df: dataframe to plot stats for.
    :param column: column to plot stats for.
    :param categorical: whatever or not the given column is categorical.
    :param save_path: path to store the plots into.
    :param show_plot: whatever or not to show the plots of the given columns.
    :return: a dictionary containing the different stats according to the given column type. If given column is
        categorical, then mode only is returned, otherwise mode, mean, median, 4-quantiles, standard deviation and
        variance are returned.
    """
    stats = {}
    if categorical:
        # Barplot
        column_value_counts = df[column].value_counts()
        ax = column_value_counts.plot.bar(x=column, y='count', rot=0)
        plt.setp(ax.get_xticklabels(), fontsize=_FONTSIZE_PLOT_CATEGORICAL, rotation=_ROTATION_PLOT_CATEGORICAL)

        # Show and store plot if required
        if save_path is not None:
            plt.savefig(save_path, format='svg')
        if show_plot:
            plt.show()

    else:
        # Histogram
        ax = df[column].astype(np.float32).plot.hist(x=column, y='Frequency', rot=0, bins=10)
        plt.setp(ax.get_xticklabels(), fontsize=_FONTSIZE_PLOT_CATEGORICAL, rotation=_ROTATION_PLOT_CATEGORICAL)

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

        # Variance
        stats[VARIANCE] = df[column].astype(np.float32).var()

        # Standard deviation
        stats[STANDARD_DEVIATION] = df[column].astype(np.float32).std()

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
