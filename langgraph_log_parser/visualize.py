import os
import pandas as pd
import pm4py


def generate_prefix_tree(event_log, output_path='tree.png'):
    """
    Generate and save a prefix tree visualization.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param output_path: Path to save the prefix tree visualization.
    :type output_path: str

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> generate_prefix_tree(event_log, 'files/tree.png')
    Event log loaded and formated from file: files/examples.csv
    Prefix Tree saved as: test.png
    """

    # Jeżeli użytkownik nie podał ścieżki
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Wygeneruj prefix tree
    prefix_tree = pm4py.discover_prefix_tree(
        event_log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp'
    )

    # Zapisz wizualizacje prefix tree
    pm4py.save_vis_prefix_tree(prefix_tree, output_path)
    print("Prefix Tree saved as:", output_path)
