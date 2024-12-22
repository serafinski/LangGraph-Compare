import json
from langgraph_log_parser.analyze import *
import pandas as pd
from typing import Optional
import os

def _convert_keys_to_serializable(data):
    """Recursively convert all keys in dictionaries to serializable types."""
    if isinstance(data, dict):
        return {str(k) if not isinstance(k, (str, int, float, bool, type(None))) else k: _convert_keys_to_serializable(
            v)
                for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_keys_to_serializable(item) for item in data]
    else:
        return data


def write_report(event_log: pd.DataFrame, output_file: Optional[str] = None) -> None:
    """
    Generate and save a comprehensive analysis report of the entire event log in JSON format.

    The generated JSON report includes:
        - Count of activities and it distribution
        - Rework counts per activity
        - Mean service times per activity
        - Average graph duration

    :param event_log: Event log data containing process execution information
    :type event_log: pd.DataFrame
    :param output_file: Path to save the JSON report, defaults to './report.json'
    :type output_file: Optional[str]

    **Example:**

    >>> csv_output = "files/process_log.csv"
    >>> event_log = pd.read_csv(csv_output)
    >>> write_report(event_log)  # Will use default './report.json'
    >>> write_report(event_log,"analysis/custom_report.json")  # Custom path
    Report successfully generated at: ./report.json
    Report successfully generated at: analysis/report.json
    """
    event_log = event_log.copy()

    structured_data = {
        "activities_count": get_act_counts(event_log),
        "rework_counts": get_global_act_reworks(event_log),
        "activities_mean_service_time": get_mean_act_times(event_log),
        "avg_graph_duration": get_avg_duration(event_log),
    }

    if output_file is None or os.path.isdir(output_file):
        base_path = output_file or "."
        output_file = os.path.join(base_path, "report.json")

    # Convert all keys to serializable types
    structured_data = _convert_keys_to_serializable(structured_data)

    # Write the structured JSON to the output file
    with open(output_file, "w") as file:
        json.dump(structured_data, file, indent=4)

    print(f"Report successfully generated at: {output_file}")