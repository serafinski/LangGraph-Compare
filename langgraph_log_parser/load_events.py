import pandas as pd
import pm4py
from typing import Union
from .experiment import ExperimentPaths

#1
def load_event_log(source: Union[ExperimentPaths, str]) -> pd.DataFrame:
    """
    Load CSV data into a formatted PM4Py DataFrame. Can load either from an ExperimentPaths
    instance or directly from a file path.

    :param source: Either an ExperimentPaths instance or a direct file path
    :type source: Union[ExperimentPaths, str]
    :return: PM4Py formatted DataFrame
    :rtype: pd.DataFrame

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> event_log = load_event_log(exp)
    Event log loaded and formatted from file: experiments/my_experiment/csv/csv_output.csv

    >>> # Using direct file path:
    >>> event_log = load_event_log("files/examples.csv")
    Event log loaded and formatted from file: files/examples.csv
    """
    if isinstance(source, ExperimentPaths):
        file_path = source.get_csv_path()
    else:
        file_path = source

    # Ładowanie CSV do pandas DataFrame
    df = pd.read_csv(file_path)

    # Formatowanie DataFrame dla PM4Py
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['end_timestamp'] = pd.to_datetime(df['end_timestamp'])

    print(f"Event log loaded and formated from file: {file_path}")
    return pm4py.format_dataframe(df, case_id='case_id', activity_key='activity', timestamp_key='timestamp')