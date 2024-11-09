import pandas as pd
import pm4py
import numpy as np
from collections import defaultdict

pd.set_option('display.max_columns', None)

def load_event_log(file_path):
    """Load CSV data into a formatted PM4Py DataFrame."""

    # Ładowanie CSV do pandas DataFrame
    df = pd.read_csv(file_path)

    # Formatowanie DataFrame dla PM4Py
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    print(f"Event log załadowany i sformatowany poprawnie z pliku: {file_path}")
    return pm4py.format_dataframe(df, case_id='case_id', activity_key='activity', timestamp_key='timestamp')

def get_start_activities(event_log):
    """Print and return the start activities of the event log."""
    start_activities = pm4py.get_start_activities(event_log)
    print("Początkowe aktywności:", start_activities)
    return start_activities

def get_end_activities(event_log):
    """Print and return the end activities of the event log."""
    end_activities = pm4py.get_end_activities(event_log)
    print("Końcowe aktywności:", end_activities)
    return end_activities

def get_activity_counts(event_log):
    """Print and return the counts of each activity in the event log."""
    activities = pm4py.get_event_attribute_values(event_log, 'concept:name')
    print("\nIlość wystąpień aktywności:", activities)
    return activities

def get_sequences_by_case(event_log):
    """Return activity sequences for each case ID."""

    # Tworzymy słownik, który będzie przechowywał sekwencje aktywności dla każdego case_id
    sequences_by_case = defaultdict(list)

    # Budujemy sekwencje dla każdego case_id
    for _, row in event_log.iterrows():
        case_id = row['case_id']
        activity = row['activity']
        sequences_by_case[case_id].append(activity)
    return sequences_by_case

def print_sequences_with_probabilities(event_log):
    """Print sequences with probabilities for each case ID."""
    sequences_by_case = get_sequences_by_case(event_log)

    # Generujemy probabilistyczny język
    language = pm4py.get_stochastic_language(event_log)
    # Tworzymy odwrotny słownik dla łatwego porównania
    case_by_sequence = {tuple(seq): case_id for case_id, seq in sequences_by_case.items()}

    print("\nSekwencje wraz z prawdopodobieństwem wystąpienia:")
    # Sortujemy sequences_by_case według numerycznych wartości case_id
    sorted_sequences = sorted(case_by_sequence.items(), key=lambda x: int(x[1]))

    for sequence, case_id in sorted_sequences:
        probability = language.get(sequence, 0)
        print(f"Case ID {case_id}: {sequence}, {probability}")

def print_minimum_self_distances(event_log):
    """Calculate and print the minimum self-distances for each activity in each case."""
    unique_case_ids = event_log['case:concept:name'].unique()
    sorted_case_ids = np.sort(unique_case_ids.astype(int)).astype(str)

    print("\nMinimalne odległości własne (self-distances) dla każdej aktywności:")
    # Iterujemy po każdym case_id i obliczamy minimalne odległości własne dla jego aktywności
    for case_id in sorted_case_ids:
        # Filtrowanie logu dla bieżącego case_id
        filtered_event_log = event_log[event_log['case:concept:name'] == case_id]

        # Obliczanie minimalnych odległości własnych dla wybranego case_id
        msd = pm4py.get_minimum_self_distances(
            filtered_event_log,
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
        print(f"Case ID {case_id}: {msd}")

def print_self_distance_witnesses(event_log):
    """Calculate and print the minimum self-distance witnesses for each activity in each case."""
    unique_case_ids = event_log['case:concept:name'].unique()
    sorted_case_ids = np.sort(unique_case_ids.astype(int)).astype(str)

    print("\nŚwiadkowie odległości własnych:")

    for case_id in sorted_case_ids:
        # Filtrowanie logu dla bieżącego case_id
        filtered_event_log = event_log[event_log['case:concept:name'] == case_id]

        # Obliczanie świadków minimalnych odległości własnych dla wybranego case_id
        msd_wit = pm4py.get_minimum_self_distance_witnesses(
            filtered_event_log,
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
        # Sortujemy świadków dla lepszej czytelności
        sorted_msd_wit = {activity: sorted(witnesses) for activity, witnesses in msd_wit.items()}
        print(f"Case ID {case_id}: {sorted_msd_wit}")


def get_rework_counts(event_log):
    """Print and return the rework counts for each activity in each case."""
    rework_counts_by_case = {}
    unique_case_ids = event_log['case:concept:name'].unique()
    sorted_case_ids = np.sort(unique_case_ids.astype(int)).astype(str)

    print("\nIlość wystąpień powtórzenia aktywności (rework):")

    for case_id in sorted_case_ids:
        # Filtrowanie logu dla bieżącego case_id
        filtered_event_log = event_log[event_log['case:concept:name'] == case_id]

        # Inicjalizacja licznika powtórzeń
        activity_counts = defaultdict(int)

        # Tworzymy listę aktywności w bieżącej ścieżce
        activities = filtered_event_log['concept:name'].tolist()

        # Zliczanie wystąpień każdej aktywności
        for activity in activities:
            activity_counts[activity] += 1

        # Usunięcie aktywności, które wystąpiły tylko raz (bo nie są "rework")
        rework_counts = {activity: count for activity, count in activity_counts.items() if count > 1}
        rework_counts_by_case[case_id] = rework_counts
        print(f"Case ID {case_id}: {rework_counts}")
    return rework_counts_by_case

def get_mean_service_time(event_log):
    """Calculate and print the mean service time for each activity."""
    mean_serv_time = pm4py.get_service_time(
        event_log, start_timestamp_key='timestamp', timestamp_key='end_timestamp', aggregation_measure='mean'
    )
    print("\nŚredni czas wykonania aktywności:", mean_serv_time)
    return mean_serv_time

def get_case_durations(event_log):
    """Calculate and print the duration of each case."""

    # Pobranie unikalnych identyfikatorów przypadków (case_id)
    unique_case_ids = event_log['case:concept:name'].unique()
    sorted_array = np.sort(unique_case_ids.astype(int)).astype(str)

    print("\nCzas trwania case'a:")

    # Iterowanie po każdym case_id i uzyskanie jego czasu trwania
    case_durations = {}
    for case_id in sorted_array:
        duration = pm4py.get_case_duration(event_log, case_id)
        case_durations[case_id] = duration
        print(f"Case ID {case_id}: {duration} s")
    return case_durations


def full_analysis(event_log):
    """
    Runs multiple analyses on the event log and prints the results in a structured format.

    Parameters:
        event_log: The event log data to analyze.
    """

    print("\n####################################################")

    get_start_activities(event_log)

    get_end_activities(event_log)

    get_activity_counts(event_log)

    print_sequences_with_probabilities(event_log)

    print_minimum_self_distances(event_log)

    print_self_distance_witnesses(event_log)

    get_rework_counts(event_log)

    get_mean_service_time(event_log)

    get_case_durations(event_log)

    print("####################################################")

### GRAPHS
def generate_prefix_tree(event_log, output_path='tree.png'):
    """Generate and save a prefix tree visualization."""
    prefix_tree = pm4py.discover_prefix_tree(
        event_log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp'
    )
    pm4py.save_vis_prefix_tree(prefix_tree, output_path)
    print("\nPrefix Tree zapisane jako:", output_path)