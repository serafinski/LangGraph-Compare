import json
from .analyze import (get_act_counts, get_global_act_reworks, get_mean_act_times, get_avg_duration,
                                          get_starts, get_ends, get_sequence_probs)
from .experiment import ExperimentPaths
import pandas as pd
from typing import Union
import os

def _convert_keys_to_serializable(data):
    """Recursively convert all keys in dictionaries to serializable types."""
    if isinstance(data, dict):
        return {str(k) if not isinstance(k, (str, int, float, bool, type(None))) else k:
                    _convert_keys_to_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_keys_to_serializable(item) for item in data]
    else:
        return data


def _validate_directory(directory_path: str) -> None:
    """
    Validate that the specified directory exists.

    :param directory_path: Path to the directory
    :type directory_path: str
    :raises FileNotFoundError: If the directory does not exist
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory does not exist: {directory_path}")


def write_metrics_report(event_log: pd.DataFrame, output_dir: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save a comprehensive analysis report of the entire event log in JSON format.

    The generated JSON report includes:
        - Count of activities
        - Rework counts per activity
        - Mean service times per activity
        - Average graph duration

    :param event_log: Event log data containing process execution information
    :type event_log: pd.DataFrame
    :param output_dir: ExperimentPaths instance or directory path where the report will be saved
    :type output_dir: Union[ExperimentPaths, str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> write_metrics_report(event_log, exp)
    Metrics report successfully generated at: experiments/my_experiment/reports/metrics_report.json

    >>> # Using direct path:
    >>> write_metrics_report(event_log, "analysis")
    Metrics report successfully generated at: analysis/metrics_report.json
    """
    event_log = event_log.copy()

    structured_data = {
        "activities_count": get_act_counts(event_log),
        "rework_counts": get_global_act_reworks(event_log),
        "activities_mean_service_time": get_mean_act_times(event_log),
        "avg_graph_duration": get_avg_duration(event_log)
    }

    # Determine output directory
    if isinstance(output_dir, ExperimentPaths):
        report_dir = output_dir.reports_dir
    else:
        report_dir = output_dir

    # Ensure the directory exists
    _validate_directory(report_dir)

    # Create the full file path
    output_file = os.path.join(report_dir, "metrics_report.json")

    # Convert all keys to serializable types
    structured_data = _convert_keys_to_serializable(structured_data)

    # Write the structured JSON to the output file
    with open(output_file, "w") as file:
        json.dump(structured_data, file, indent=4)

    print(f"Metrics report successfully generated at: {output_file}")


def write_sequences_report(event_log: pd.DataFrame, output_dir: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save a comprehensive sequences report in JSON format.

    The generated JSON report includes:
        - Start activities
        - End activities
        - Last occurrence of the sequences with probabilities

    :param event_log: Event log data containing process execution information
    :type event_log: pd.DataFrame
    :param output_dir: ExperimentPaths instance or directory path where the report will be saved
    :type output_dir: Union[ExperimentPaths, str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> write_sequences_report(event_log, exp)
    Sequences report successfully generated at: experiments/my_experiment/reports/sequences_report.json

    >>> # Using direct path:
    >>> write_sequences_report(event_log, "analysis")
    Sequences report successfully generated at: analysis/sequences_report.json
    """
    event_log = event_log.copy()

    structured_data = {
        "start_activities": get_starts(event_log),
        "end_activities": get_ends(event_log),
        "sequence_probabilities": get_sequence_probs(event_log),
    }

    # Determine output directory
    if isinstance(output_dir, ExperimentPaths):
        report_dir = output_dir.reports_dir
    else:
        report_dir = output_dir

    # Ensure the directory exists
    _validate_directory(report_dir)

    # Create the full file path
    output_file = os.path.join(report_dir, "sequences_report.json")

    # Convert all keys to serializable types
    structured_data = _convert_keys_to_serializable(structured_data)

    # Write the structured JSON to the output file
    with open(output_file, "w") as file:
        json.dump(structured_data, file, indent=4)

    print(f"Sequences report successfully generated at: {output_file}")


def generate_reports(event_log: pd.DataFrame, output_dir: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save all analysis reports in JSON format.

    The generated JSON reports include:
        - Count of activities
        - Rework counts per activity
        - Mean service times per activity
        - Average graph duration
        - Start activities
        - End activities
        - Last occurrence of the sequences with probabilities

    :param event_log: Event log data containing process execution information
    :type event_log: pd.DataFrame
    :param output_dir: ExperimentPaths instance or directory path where the reports will be saved
    :type output_dir: Union[ExperimentPaths, str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> generate_reports(event_log, exp)
    Metrics report successfully generated at: experiments/my_experiment/reports/metrics_report.json
    Sequences report successfully generated at: experiments/my_experiment/reports/sequences_report.json
    All reports successfully generated.

    >>> # Using direct path:
    >>> generate_reports(event_log, "analysis")
    Metrics report successfully generated at: analysis/metrics_report.json
    Sequences report successfully generated at: analysis/sequences_report.json
    All reports successfully generated.
    """
    write_metrics_report(event_log, output_dir)
    write_sequences_report(event_log, output_dir)
    print("All reports successfully generated.")