from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from lib.config import AppConfig


def custom_train_test_split(data, group_by: str, test_size=0.2, random_state=None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Custom train-test split function that splits the data based on
    a specified grouping variable.

    Parameters:
        data (pandas.DataFrame): The input data to be split.
        group_by (str): The column name to group the data by.
        test_size (float): The proportion of the data to be used for testing.
        Default is 0.2.
        random_state (int): The random seed for reproducibility.
        Default is None.

    Returns:
        train_data (pandas.DataFrame): The training data.
        test_data (pandas.DataFrame): The testing data.

    Usage:
        ```python
        train_data, test_data = custom_train_test_split(
            final_df, test_size=0.2
        )
        ```
    """
    grouped = data.groupby(group_by)
    groups_keys = list(grouped.groups.keys())

    train_keys, test_keys = train_test_split(groups_keys, test_size=test_size, random_state=random_state)

    train_data = pd.concat([grouped.get_group(key) for key in train_keys])
    test_data = pd.concat([grouped.get_group(key) for key in test_keys])

    return train_data, test_data


def filter_data_by_compositional_range(data, compositional_range, oxide, oxide_ranges):
    """
    Filter the dataset for a given compositional range and oxide.

    Parameters:
    - data (pd.DataFrame): The dataset to filter.
    - compositional_range (str): The compositional range ('Full', 'Low', 'Mid', 'High').
    - oxide (str): The oxide to filter by.

    Returns:
    - pd.DataFrame: The filtered dataset.
    """
    # Access the global oxide_ranges dictionary
    # Get the lower and upper bounds for the specified compositional range and oxide
    lower_bound, upper_bound = oxide_ranges[oxide][compositional_range]

    data[oxide] = pd.to_numeric(data[oxide], errors="coerce")
    data = data.dropna(subset=[oxide])

    # Filter the dataset based on the oxide concentration within the specified range
    filtered_data = data[(data[oxide] >= lower_bound) & (data[oxide] <= upper_bound)]

    # Check if empty now
    if filtered_data.empty:
        print(f"WARNING: No data found for {compositional_range} {oxide} ({lower_bound}-{upper_bound})")

    return filtered_data


def get_train_test_split(split_loc: str | None = None) -> pd.DataFrame:
    """
    Reads the train-test split data from a CSV file.

    Args:
        split_loc (str | None): The path to the train-test split CSV file. If None, it will be read from the .env file.

    Returns:
        pd.DataFrame: The train-test split data as a pandas DataFrame.

    Raises:
        ValueError: If TRAIN_TEST_SPLIT_PATH is not set in the .env file.
        FileNotFoundError: If the specified file does not exist.
    """
    if split_loc is None:
        config = AppConfig()
        split_loc = config.train_test_split_path

    train_test_split_path = Path(split_loc)
    if not train_test_split_path.exists():
        raise FileNotFoundError(f"File {train_test_split_path} not found.")

    return pd.read_csv(train_test_split_path)
