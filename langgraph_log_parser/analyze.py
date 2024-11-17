import pandas as pd
import pm4py
import numpy as np
from collections import defaultdict

pd.set_option('display.max_columns', None)

#1
def load_event_log(file_path):
    """
    Load CSV data into a formatted PM4Py DataFrame.

    :param file_path: Path to the CSV file containing the event log.
    :type file_path: str
    :return: PM4Py formatted DataFrame.
    :rtype: pd.DataFrame
    """
    # Ładowanie CSV do pandas DataFrame
    df = pd.read_csv(file_path)

    # Formatowanie DataFrame dla PM4Py
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    print(f"Event log loaded and formated from file: {file_path}")
    return pm4py.format_dataframe(df, case_id='case_id', activity_key='activity', timestamp_key='timestamp')

#2
def get_all_start_activities(event_log):
    """
    Get the start activities of the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Start activities and their counts.
    :rtype: dict
    """
    start_activities = pm4py.get_start_activities(event_log)
    return start_activities

#3
def print_all_start_activities(event_log):
    """
    Print the start activities of the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    start_activities = get_all_start_activities(event_log)
    print("\nStart activities:", start_activities)


#4
def get_all_end_activities(event_log):
    """
    Get the end activities of the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: End activities and their counts.
    :rtype: dict
    """
    end_activities = pm4py.get_end_activities(event_log)
    return end_activities
#5
def print_all_end_activities(event_log):
    """
    Print the end activities of the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    end_activities = get_all_end_activities(event_log)
    print("\nEnd activities:", end_activities)

#6
def get_all_activities_count(event_log):
    """
    Get the counts of every activity in the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Activity counts.
    :rtype: dict
    """
    activities = pm4py.get_event_attribute_values(event_log, 'concept:name')
    return activities

#7
def print_all_activities_count(event_log):
    """
    Print the counts of every activity in the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    activities = get_all_activities_count(event_log)
    print("\nCount of each activity:", activities)

#8
def get_all_sequences(event_log):
    """
    Return activity sequences for every case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Mapping of case IDs to their activity sequences.
    :rtype: dict
    """
    # Tworzymy słownik, który będzie przechowywał sekwencje aktywności dla każdego case_id
    sequences_by_case = defaultdict(list)

    # Budujemy sekwencje dla każdego case_id
    for _, row in event_log.iterrows():
        case_id = row['case_id']
        activity = row['activity']
        sequences_by_case[case_id].append(activity)
    return dict(sequences_by_case)

#9
def print_all_sequences(event_log):
    """
    Print sequences for every case ID in the event log, sorted numerically by case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    # Sekwencja dla każdego case_id
    sequences_by_case = get_all_sequences(event_log)

    print("\nAll sequences:")

    # Sortowanie po case_id
    for case_id in sorted(sequences_by_case.keys(), key=lambda x: int(x)):
        sequence = sequences_by_case[case_id]
        print(f"Case ID {case_id}: {sequence}")

#10
def get_all_sequences_with_probabilities(event_log):
    """
    Return sequences with probabilities for each case ID.
    If sequence already occurred it only lists the ID of the latest occurrence.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: List of tuples containing (case ID, sequence, probability).
    :rtype: list
    """
    sequences_by_case = get_all_sequences(event_log)

    # Generujemy probabilistyczny język
    language = pm4py.get_stochastic_language(event_log)

    # Tworzymy odwrotny słownik dla łatwego porównania
    case_by_sequence = {tuple(seq): case_id for case_id, seq in sequences_by_case.items()}

    # Sortujemy sequences_by_case według numerycznych wartości case_id
    sorted_sequences = sorted(case_by_sequence.items(), key=lambda x: int(x[1]))

    # Generowanie listy rezultatów
    result = [(case_id, sequence, language.get(sequence, 0)) for sequence, case_id in sorted_sequences]
    return result

#11
def print_all_sequences_with_probabilities(event_log):
    """
    Print sequences with probabilities for each case ID.
    If sequence already occurred it only prints the ID of the latest occurrence.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    sequences_with_probabilities = get_all_sequences_with_probabilities(event_log)

    print("\nID of last sequence occurrence with probability of occurrence:")
    for case_id, sequence, probability in sequences_with_probabilities:
        print(f"Case ID {case_id}: {sequence}, {probability}")

# 16
def get_all_minimum_self_distances(event_log):
    """
    Calculate the minimum self-distances for each activity in each case.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Dictionary where keys are case IDs and values are dictionaries of activities with their minimum self-distances.
    :rtype: dict
    """
    unique_case_ids = event_log['case:concept:name'].unique()
    sorted_case_ids = np.sort(unique_case_ids.astype(int)).astype(str)

    # Słownik do przechowywania minimalnych odległości własnych dla każdego Case ID
    min_self_distances = {}

    # Iterujemy po każdym case_id i obliczamy minimalne odległości własne dla jego aktywności
    for case_id in sorted_case_ids:
        # Filtrowanie event logu dla danego case_id
        filtered_event_log = event_log[event_log['case:concept:name'] == case_id]

        # Kalkulowanie minimalnych odległości własnych dla danego case_id
        msd = pm4py.get_minimum_self_distances(
            filtered_event_log,
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
        min_self_distances[case_id] = msd

    return min_self_distances

#17
def print_all_minimum_self_distances(event_log):
    """
    Calculate and print the minimum self-distances for each activity in each case.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    min_self_distances = get_all_minimum_self_distances(event_log)

    print("\nMinimal self-distances for every activity:")
    for case_id, distances in min_self_distances.items():
        print(f"Case ID {case_id}: {distances}")

#24
def get_all_rework_counts(event_log):
    """
    Return the rework counts for each activity in each case.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Rework counts for each case ID.
    :rtype: dict
    """
    rework_counts_by_case = {}
    unique_case_ids = event_log['case:concept:name'].unique()
    sorted_case_ids = np.sort(unique_case_ids.astype(int)).astype(str)

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
    return rework_counts_by_case

#25
def print_all_rework_counts(event_log):
    """
    Print the rework counts for each activity in each case.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    rework_counts_by_case = get_all_rework_counts(event_log)

    print("\nCount of activity rework:")
    for case_id, rework_counts in rework_counts_by_case.items():
        print(f"Case ID {case_id}: {rework_counts}")

#28
def get_all_activities_mean_service_time(event_log):
    """
    Calculate the mean service time for each activity.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Mean service times for each activity.
    :rtype: dict
    """
    mean_serv_time = pm4py.get_service_time(
        event_log, start_timestamp_key='timestamp', timestamp_key='end_timestamp', aggregation_measure='mean'
    )
    return mean_serv_time
#29
def print_all_activities_mean_service_time(event_log):
    """
    Print the mean service time for each activity.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    mean_serv_time = get_all_activities_mean_service_time(event_log)
    print("\nMean duration of every activity (in sec):", mean_serv_time)

#30
def get_all_cases_durations(event_log):
    """
    Calculate the duration of each case.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Case durations.
    :rtype: dict
    """
    # Pobranie unikalnych identyfikatorów przypadków (case_id)
    unique_case_ids = event_log['case:concept:name'].unique()
    sorted_array = np.sort(unique_case_ids.astype(int)).astype(str)

    # Iterowanie po każdym case_id i uzyskanie jego czasu trwania
    case_durations = {}
    for case_id in sorted_array:
        duration = pm4py.get_case_duration(event_log, case_id)
        case_durations[case_id] = duration
    return case_durations

#31
def print_all_cases_durations(event_log):
    """
    Print the duration of each case.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    case_durations = get_all_cases_durations(event_log)
    print("\nDuration of the case:")

    for case_id, duration in case_durations.items():
        print(f"Case ID {case_id}: {duration} s")


def get_all_self_distance_witnesses(event_log):
    """
    Compute the minimum self-distance witnesses for each activity in each case of the event log.

    :param event_log: Event log data containing events with case IDs and activity names.
    :type event_log: pd.DataFrame
    :return: A dictionary where each key is a case ID, and each value is another dictionary mapping
             activities to lists of witness sequences.
    :rtype: dict
    """
    # Konwersja case_id do int'a
    event_log['case_id'] = event_log['case_id'].astype(int)
    unique_case_ids = event_log['case_id'].unique()

    # Sortowanie case_id
    sorted_case_ids = sorted(unique_case_ids)

    all_msd_witnesses = {}

    for case_id in sorted_case_ids:
        # Filtrowanie event log'u dla aktualnego case_id
        filtered_event_log = event_log[event_log['case_id'] == case_id].copy()

        if filtered_event_log.empty:
            continue

        # Reset index'u by zapewnić, że index'y zaczynają się od 0
        filtered_event_log.reset_index(drop=True, inplace=True)

        # Grupowanie event'ów po aktywności i kalkulacja indeksów
        activity_indices = {}
        for activity in filtered_event_log['concept:name'].unique():
            activity_indices[activity] = filtered_event_log[filtered_event_log['concept:name'] == activity].index.tolist()

        # Wylicz minimalne odległości własne i świadków
        min_self_distances = {}
        corrected_witnesses = {}
        for activity, indices in activity_indices.items():
            # Nie ma odległości własnej jak nie występuje przynajmniej 2 razy
            if len(indices) < 2:
                continue

            # Wylicz przerwy i znajdź minimalne odległości własne
            gaps = [indices[i + 1] - indices[i] - 1 for i in range(len(indices) - 1)]
            min_distance = min(gaps)
            min_self_distances[activity] = min_distance

            # Zidentyfikuj świadków dla minimalnych odległości własnych
            witness_sequences = []
            for i in range(len(indices) - 1):
                gap_size = indices[i + 1] - indices[i] - 1
                if gap_size == min_distance:
                    gap_events = filtered_event_log.iloc[indices[i] + 1:indices[i + 1]]['concept:name'].tolist()
                    # Wyłącz aktywność z listy
                    gap_events = [event for event in gap_events if event != activity]
                    # Dodaj tylko nie pustę przerwy
                    if gap_events:
                        witness_sequences.append(gap_events)

            # De duplikacja sekwencji z zachowaniem ich kolejności
            unique_sequences = list(map(list, {tuple(seq) for seq in witness_sequences}))
            corrected_witnesses[activity] = unique_sequences

        all_msd_witnesses[case_id] = corrected_witnesses

    return all_msd_witnesses


def print_all_self_distance_witnesses(event_log):
    """
    Print the minimum self-distance witnesses for each activity in each case.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    all_msd_witnesses = get_all_self_distance_witnesses(event_log)

    print("\nWitnesses of minimum self-distances:")
    for case_id, witnesses in all_msd_witnesses.items():
        print(f"Case ID {case_id}: {witnesses}")

#42
def print_full_analysis(event_log):
    """
    Run multiple analyses on the event log and print the results.

    :param event_log: The event log data to analyze.
    :type event_log: pd.DataFrame
    """

    print("\n####################START###########################")

    print_all_start_activities(event_log)

    print_all_end_activities(event_log)

    print_all_activities_count(event_log)

    print_all_sequences(event_log)

    print_all_sequences_with_probabilities(event_log)

    print_all_minimum_self_distances(event_log)

    print_all_self_distance_witnesses(event_log)

    print_all_rework_counts(event_log)

    print_all_activities_mean_service_time(event_log)

    print_all_cases_durations(event_log)

    print("\n######################END###########################")