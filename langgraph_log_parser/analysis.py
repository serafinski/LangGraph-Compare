import pandas as pd
import pm4py
import numpy as np
from collections import defaultdict
from collections import Counter

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
def get_end_activities(event_log):
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
    end_activities = get_end_activities(event_log)
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
def get_all_sequences_by_case_id(event_log):
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
def print_all_sequences_by_case_id(event_log):
    """
    Print sequences for every case ID in the event log, sorted numerically by case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    """
    # Sekwencja dla każdego case_id
    sequences_by_case = get_all_sequences_by_case_id(event_log)

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
    sequences_by_case = get_all_sequences_by_case_id(event_log)

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
# 12
def get_sequence_by_case_id(event_log, case_id):
    """
    Return the activity sequence for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the sequence for.
    :type case_id: int or str
    :return: The activity sequence for the specified case ID.
    :rtype: list
    :raises ValueError: If the case ID does not exist in the event log.
    """
    # Sprawdź, czy case_id istnieje
    if case_id not in event_log['case_id'].unique():
        raise ValueError(f"Case ID {case_id} does not exist in the event log.")

    # Filtrowanie event log'u pod dane case_id
    case_log = event_log[event_log['case_id'] == case_id]

    # Wyciągnięcie sekwencji
    sequence = case_log['activity'].tolist()

    return sequence

#13
def print_sequence_by_case_id(event_log, case_id):
    """
    Print the activity sequence for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the sequence for.
    :type case_id: int or str
    """
    sequence = get_sequence_by_case_id(event_log, case_id)
    print(f"\nActivity sequence for case ID {case_id}: {sequence}")

#14
def get_sequence_with_probability_by_case_id(event_log, case_id):
    """
    Return the activity sequence with its probability for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the sequence and probability for.
    :type case_id: int or str
    :return: A tuple containing (sequence, probability) for the specified case ID.
    :rtype: tuple
    :raises ValueError: If the case ID does not exist in the event log.
    """
    # Sprawdź, czy case_id istnieje
    if case_id not in event_log['case_id'].unique():
        raise ValueError(f"Case ID {case_id} does not exist in the event log.")

    # Pobierz sekwencje o specyficznym case_id
    sequence = get_sequence_by_case_id(event_log, case_id)

    # Generujemy probabilistyczny język
    language = pm4py.get_stochastic_language(event_log)

    probability = language.get(tuple(sequence), 0)

    return sequence, probability

#15
def print_sequence_with_probability_by_case_id(event_log, case_id):
    """
    Print the activity sequence with its probability for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the sequence and probability for.
    :type case_id: int or str
    """
    sequence, probability = get_sequence_with_probability_by_case_id(event_log, case_id)
    print(f"\nActivity sequence with probability for case ID {case_id}: Sequence: {sequence}, Probability: {probability}")

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

#18
def get_minimum_self_distances_by_case_id(event_log, case_id):
    """
    Return the minimum self-distances for all activities for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the minimum self-distances for.
    :type case_id: int or str
    :return: A dictionary of activities with their minimum self-distances for the specified case ID.
    :rtype: dict
    :raises ValueError: If the case ID does not exist in the event log.
    """
    # Sprawdź, czy case_id istnieje w event logu
    if case_id not in event_log['case_id'].unique():
        raise ValueError(f"Case ID {case_id} does not exist in the event log.")

    # Filtrowanie event logu do specyficznego case id
    filtered_event_log = event_log[event_log['case_id'] == case_id]

    # Obliczanie minimalnych odległości własnych dla wybranego case_id
    msd = pm4py.get_minimum_self_distances(
        filtered_event_log,
        activity_key='concept:name',
        case_id_key='case:concept:name',
        timestamp_key='time:timestamp'
    )
    return msd

#19
def print_minimum_self_distances_by_case_id(event_log, case_id):
    """
    Print the minimum self-distances for all activities for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the minimum self-distances for.
    :type case_id: int or str
    """

    min_self_distances = get_minimum_self_distances_by_case_id(event_log, case_id)
    print(f"\nMinimum self distances for case ID {case_id}: {min_self_distances}")

# TODO - FIX THIS
#20 REQUIRES FIX (NEED TO DIFF WHEN Hierarchical Agent Teams) - ISSUE WITH get_minimum_self_distance_witnesses
def get_all_self_distance_witnesses(event_log):
    """
    Calculate the minimum self-distance witnesses for each activity in each case.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Dictionary where keys are case IDs, and values are dictionaries with activities and their sorted witnesses.
    :rtype: dict
    """
    unique_case_ids = event_log['case_id'].unique()
    sorted_case_ids = np.sort(unique_case_ids.astype(int)).astype(str)

    # Słownik do przechowywania świadków dla każdego case ID
    all_msd_witnesses = {}

    for case_id in sorted_case_ids:
        # Filtruj event log dla aktualnego case_id
        filtered_event_log = event_log[event_log['case_id'] == case_id]

        # Wylicz świadków odległości własnych dla min. własnych dystansów
        msd_wit = pm4py.get_minimum_self_distance_witnesses(
            filtered_event_log,
            activity_key='concept:name',
            case_id_key='case:concept:name',
            timestamp_key='time:timestamp'
        )
        # Sortowanie świadków
        sorted_msd_wit = {activity: sorted(witnesses) for activity, witnesses in msd_wit.items()}
        all_msd_witnesses[case_id] = sorted_msd_wit

    return all_msd_witnesses

# TODO - FIX THIS
#21 REQUIRES FIX (NEED TO DIFF WHEN Hierarchical Agent Teams) - ISSUE WITH get_minimum_self_distance_witnesses
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

# TODO - FIX THIS
#22 REQUIRES FIX (NEED TO DIFF WHEN Hierarchical Agent Teams) - ISSUE WITH get_minimum_self_distance_witnesses
def get_self_distance_witnesses_by_case_id(event_log, case_id):
    """
    Return the minimum self-distance witnesses for all activities for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the witnesses for.
    :type case_id: int or str
    :return: A dictionary of activities with their sorted witnesses for the specified case ID.
    :rtype: dict
    :raises ValueError: If the case ID does not exist in the event log.
    """
    # Check if case_id exists in the event log
    if case_id not in event_log['case_id'].unique():
        raise ValueError(f"Case ID {case_id} does not exist in the event log.")

    # Filter event log for the specific case_id
    filtered_event_log = event_log[event_log['case_id'] == case_id]

    # Calculate witnesses for the minimum self-distances
    msd_wit = pm4py.get_minimum_self_distance_witnesses(
        filtered_event_log,
        activity_key='concept:name',
        case_id_key='case:concept:name',
        timestamp_key='time:timestamp'
    )


    # Sort witnesses for better readability
    sorted_msd_wit = {activity: sorted(witnesses) for activity, witnesses in msd_wit.items()}
    return sorted_msd_wit

# TODO - FIX THIS
#23 REQUIRES FIX (NEED TO DIFF WHEN Hierarchical Agent Teams) - ISSUE WITH get_minimum_self_distance_witnesses
def print_self_distance_witnesses_by_case_id(event_log, case_id):
    """
    Print the minimum self-distance witnesses for all activities for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the witnesses for.
    :type case_id: int or str
    """
    witnesses = get_self_distance_witnesses_by_case_id(event_log, case_id)
    print(f"\nMinimum self distance witnesses for case ID {case_id}: {witnesses}")

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

#26
def get_rework_by_case_id(event_log, case_id):
    """
    Return the rework counts for each activity for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the rework counts for.
    :type case_id: int or str
    :return: A dictionary of activities with their rework counts for the specified case ID.
    :rtype: dict
    :raises ValueError: If the case ID does not exist in the event log.
    """
    # Sprawdź, czy case_id istnieje w event_log'u
    if case_id not in event_log['case_id'].unique():
        raise ValueError(f"Case ID {case_id} does not exist in the event log.")

    # Filtrowanie dla specyficznego case_id
    filtered_event_log = event_log[event_log['case_id'] == case_id]

    # Inicjalizacja liczenia aktywności
    activity_counts = defaultdict(int)

    # Tworzenie listy aktywności
    activities = filtered_event_log['concept:name'].tolist()

    # Policz wystąpienia każdej aktywności
    for activity in activities:
        activity_counts[activity] += 1

    # Jeżeli zaistniało raz — usuń bo nie rework
    rework_counts = {activity: count for activity, count in activity_counts.items() if count > 1}

    return rework_counts

#27
def print_rework_by_case_id(event_log, case_id):
    """
    Print the rework counts for each activity for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the rework counts for.
    :type case_id: int or str
    """
    rework_counts = get_rework_by_case_id(event_log, case_id)
    print(f"\nRework counts for case ID {case_id}: {rework_counts}")

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

#32
def get_case_duration_by_id(event_log, case_id):
    """
    Calculate the duration time for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the duration time for.
    :type case_id: int or str
    :return: The duration time for the specified case ID.
    :rtype: float
    :raises ValueError: If the case ID does not exist in the event log.
    """
    # Konwersja na string'a - bo get_case_duration przyjmuje tylko stringi
    case_id_str = str(case_id)

    # Sprawdź, czy case_id istnieje w event_log'u
    if case_id_str not in event_log['case_id'].astype(str).unique():
        raise ValueError(f"Case ID {case_id} does not exist in the event log.")

    # Wylicz czas trwania dla danego case_id
    duration = pm4py.get_case_duration(event_log, case_id_str)
    return duration
#33
def print_case_duration_by_id(event_log, case_id):
    """
    Print the duration time for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the duration time for.
    :type case_id: int or str
    """
    duration = get_case_duration_by_id(event_log, case_id)
    print(f"\nDuration for case ID {case_id}: {duration} s")

#34
def get_start_activity(event_log, case_id):
    """
    Retrieve the first activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the start activity for.
    :type case_id: int or str
    :return: The first activity in the sequence.
    :rtype: str
    """
    sequence = get_sequence_by_case_id(event_log, case_id)
    return sequence[0]

#35
def print_start_activity(event_log, case_id):
    """
    Print the first activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the start activity for.
    :type case_id: int or str
    """
    start_activity = get_start_activity(event_log, case_id)
    print(f"\nStart activity for case ID {case_id}: {start_activity}")

#36
def get_end_activity(event_log, case_id):
    """
    Retrieve the last activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the end activity for.
    :type case_id: int or str
    :return: The last activity in the sequence.
    :rtype: str
    """
    sequence = get_sequence_by_case_id(event_log, case_id)
    return sequence[-1]

#37
def print_end_activity(event_log, case_id):
    """
    Print the last activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the end activity for.
    :type case_id: int or str
    """
    end_activity = get_end_activity(event_log, case_id)
    print(f"\nEnd activity for case ID {case_id}: {end_activity}")

#38
def get_activities_count_by_case_id(event_log, case_id):
    """
    Count how many times each activity occurred for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to count activities for.
    :type case_id: int or str
    :return: A dictionary with activities as keys and their counts as values.
    :rtype: dict
    """
    sequence = get_sequence_by_case_id(event_log, case_id)
    return dict(Counter(sequence))

#39
def print_activities_count_by_case_id(event_log, case_id):
    """
    Print the count of each activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to count and print activities for.
    :type case_id: int or str
    """
    activities_count = get_activities_count_by_case_id(event_log, case_id)
    print(f"\nCount of each activity for case ID {case_id}: {activities_count}")

#40

#41

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

    print_all_sequences_by_case_id(event_log)

    print_all_sequences_with_probabilities(event_log)

    print_all_minimum_self_distances(event_log)

    # TODO - FIX THIS
    print_all_self_distance_witnesses(event_log)

    print_all_rework_counts(event_log)

    print_all_activities_mean_service_time(event_log)

    print_all_cases_durations(event_log)

    print("\n######################END###########################")
#43
def print_full_analysis_by_id(event_log, case_id):
    """
    Run multiple analyses on single case_id and print the results.

    :param event_log: The event log data to analyze.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and analyze.
    :type case_id: int
    """

    print("\n####################START###########################")

    print_start_activity(event_log, case_id)

    print_end_activity(event_log, case_id)

    print_activities_count_by_case_id(event_log, case_id)

    print_sequence_by_case_id(event_log, case_id)

    print_sequence_with_probability_by_case_id(event_log, case_id)

    print_minimum_self_distances_by_case_id(event_log, case_id)

    # TODO - FIX THIS
    print_self_distance_witnesses_by_case_id(event_log, case_id)

    print_rework_by_case_id(event_log,case_id)

    # TODO - wersja dla pojedynczego ID
    print_all_activities_mean_service_time(event_log)

    print_case_duration_by_id(event_log,case_id)

    print("\n######################END###########################")

