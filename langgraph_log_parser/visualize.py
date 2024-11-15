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
    """

    # Jeżeli użytkownik nie podał ścieżki
    if os.path.dirname(output_path) == '':
        # Upewnij się, że folder istnieje
        img_folder = 'img'
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
        # Zapisz obraz w docelowej ścieżce
        output_path = os.path.join(img_folder, output_path)

    # Wygeneruj prefix tree
    prefix_tree = pm4py.discover_prefix_tree(
        event_log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp'
    )

    # Zapisz wizualizacje prefix tree
    pm4py.save_vis_prefix_tree(prefix_tree, output_path)
    print("\nPrefix Tree saved as:", output_path)
