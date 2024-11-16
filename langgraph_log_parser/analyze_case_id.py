import pandas as pd
import pm4py
from collections import defaultdict
from collections import Counter

pd.set_option('display.max_columns', None)

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
    # print_all_activities_mean_service_time(event_log)

    print_case_duration_by_id(event_log,case_id)

    print("\n######################END###########################")