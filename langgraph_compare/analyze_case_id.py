import pandas as pd
import pm4py
from collections import defaultdict
from collections import Counter

pd.set_option('display.max_columns', None)

# 12
def get_case_sequence(event_log: pd.DataFrame, case_id: int) -> list[str]:
    """
    Return the activity sequence for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the sequence for.
    :type case_id: int
    :return: The activity sequence for the specified case ID.
    :rtype: list
    :raises ValueError: If the case ID does not exist in the event log.

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_sequence(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    ['__start__', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'ChartGenerator', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor']
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
def print_case_sequence(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the activity sequence for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the sequence for.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_case_sequence(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    Activity sequence for case ID 19: ['__start__', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'ChartGenerator', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor']
    """
    sequence = get_case_sequence(event_log, case_id)
    print(f"Activity sequence for case ID {case_id}: {sequence}")

#14
def get_case_sequence_prob(event_log: pd.DataFrame, case_id: int) -> tuple[list[str], float]:
    """
    Return the activity sequence with its probability for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the sequence and probability for.
    :type case_id: int
    :return: A tuple containing (sequence, probability) for the specified case ID.
    :rtype: tuple
    :raises ValueError: If the case ID does not exist in the event log.

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_sequence_prob(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    (['__start__', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'ChartGenerator', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor'], 0.3333333333333333)
    """
    # Sprawdź, czy case_id istnieje
    if case_id not in event_log['case_id'].unique():
        raise ValueError(f"Case ID {case_id} does not exist in the event log.")

    # Pobierz sekwencje o specyficznym case_id
    sequence = get_case_sequence(event_log, case_id)

    # Generujemy probabilistyczny język
    language = pm4py.get_stochastic_language(event_log)

    probability = language.get(tuple(sequence), 0)

    return sequence, probability

#15
def print_case_sequence_prob(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the activity sequence with its probability for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the sequence and probability for.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_case_sequence_prob(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    Activity sequence for case ID 19: ['__start__', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'ChartGenerator', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor']
    Probability: 0.333
    """
    sequence, probability = get_case_sequence_prob(event_log, case_id)
    print(f"Activity sequence for case ID {case_id}: {sequence}")
    print(f"Probability: {round(probability,3)}")

#18
def get_case_min_self_dists(event_log: pd.DataFrame, case_id: int) -> dict[str, int]:
    """
    Return the minimum self-distances for all activities for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the minimum self-distances for.
    :type case_id: int
    :return: A dictionary of activities with their minimum self-distances for the specified case ID.
    :rtype: dict
    :raises ValueError: If the case ID does not exist in the event log.

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_min_self_dists(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    {'DocWriter': 1, 'Search': 6, 'WebScraper': 4, '__start__': 1, 'ag_supervisor': 1, 'rg_supervisor': 1, 'test_supervisor': 2}
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
def print_case_min_self_dists(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the minimum self-distances for all activities for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the minimum self-distances for.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_case_min_self_dists(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    Minimum self distances for case ID 19: {'DocWriter': 1, 'Search': 6, 'WebScraper': 4, '__start__': 1, 'ag_supervisor': 1, 'rg_supervisor': 1, 'test_supervisor': 2}
    """

    min_self_distances = get_case_min_self_dists(event_log, case_id)
    print(f"Minimum self distances for case ID {case_id}: {min_self_distances}")

#26
def get_case_act_reworks(event_log: pd.DataFrame, case_id: int) -> dict[str, int]:
    """
    Return the rework counts for each activity for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the rework counts for.
    :type case_id: int
    :return: A dictionary of activities with their rework counts for the specified case ID.
    :rtype: dict
    :raises ValueError: If the case ID does not exist in the event log.

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_act_reworks(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    {'__start__': 18, 'test_supervisor': 18, 'rg_supervisor': 15, 'Search': 3, 'WebScraper': 4, 'ag_supervisor': 14, 'DocWriter': 4}
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
def print_case_act_reworks(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the rework counts for each activity for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the rework counts for.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_case_act_reworks(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    Rework counts for case ID 19: {'__start__': 18, 'test_supervisor': 18, 'rg_supervisor': 15, 'Search': 3, 'WebScraper': 4, 'ag_supervisor': 14, 'DocWriter': 4}
    """
    rework_counts = get_case_act_reworks(event_log, case_id)
    print(f"Rework counts for case ID {case_id}: {rework_counts}")

#32
def get_case_duration(event_log: pd.DataFrame, case_id: int) -> float:
    """
    Calculate the duration time for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the duration time for.
    :type case_id: int
    :return: The duration time for the specified case ID.
    :rtype: float
    :raises ValueError: If the case ID does not exist in the event log.

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_duration(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    120.730501
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
def print_case_duration(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the duration time for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the duration time for.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_case_duration(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    Duration for case ID 19: 120.731 s
    """
    duration = get_case_duration(event_log, case_id)
    print(f"Duration for case ID {case_id}: {round(duration,3)} s")

#34
def get_case_start(event_log: pd.DataFrame, case_id: int) -> str:
    """
    Retrieve the first activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the start activity for.
    :type case_id: int
    :return: The first activity in the sequence.
    :rtype: str

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_start(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    __start__
    """
    sequence = get_case_sequence(event_log, case_id)
    return sequence[0]

#35
def print_case_start(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the first activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the start activity for.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_case_start(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    Start activity for case ID 19: __start__
    """
    start_activity = get_case_start(event_log, case_id)
    print(f"Start activity for case ID {case_id}: {start_activity}")

#36
def get_case_end(event_log: pd.DataFrame, case_id: int) -> str:
    """
    Retrieve the last activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the end activity for.
    :type case_id: int
    :return: The last activity in the sequence.
    :rtype: str

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_end(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    test_supervisor
    """
    sequence = get_case_sequence(event_log, case_id)
    return sequence[-1]

#37
def print_case_end(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the last activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the end activity for.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_case_end(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    End activity for case ID 19: test_supervisor
    """
    end_activity = get_case_end(event_log, case_id)
    print(f"End activity for case ID {case_id}: {end_activity}")

#38
def get_case_act_counts(event_log: pd.DataFrame, case_id: int) -> dict[str, int]:
    """
    Count how many times each activity occurred for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to count activities for.
    :type case_id: int
    :return: A dictionary with activities as keys and their counts as values.
    :rtype: dict

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_act_counts(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    {'__start__': 18, 'test_supervisor': 18, 'rg_supervisor': 15, 'Search': 3, 'WebScraper': 4, 'ag_supervisor': 14, 'ChartGenerator': 1, 'DocWriter': 4}
    """
    sequence = get_case_sequence(event_log, case_id)
    return dict(Counter(sequence))

#39
def print_case_act_counts(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the count of each activity for the specified case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to count and print activities for.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_case_act_counts(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    Count of each activity for case ID 19:
    Activity '__start__': 18
    Activity 'test_supervisor': 18
    Activity 'rg_supervisor': 15
    Activity 'Search': 3
    Activity 'WebScraper': 4
    Activity 'ag_supervisor': 14
    Activity 'ChartGenerator': 1
    Activity 'DocWriter': 4
    """
    activities_count = get_case_act_counts(event_log, case_id)
    print(f"Count of each activity for case ID {case_id}:")
    for activity, count in activities_count.items():
        print(f"Activity '{activity}': {count}")

#40
def get_case_sum_act_times(event_log: pd.DataFrame, case_id: int) -> dict[str, float]:
    """
    Calculate the sum service time in seconds for each activity for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID for which to calculate service times.
    :type case_id: int
    :return: Sum service times for each activity in the specified case.
    :rtype: dict

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_sum_act_times(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    {'ChartGenerator': 0.608224, 'DocWriter': 2.0285469999999997, 'Search': 1.7249849999999998, 'WebScraper': 2.4464859999999997, '__start__': 0.603216, 'ag_supervisor': 0.10220199999999999, 'rg_supervisor': 23.0226, 'test_supervisor': 0.747701}
    """

    # Konwersja na string'a - bo get_service_time przyjmuje tylko stringi
    case_id_str = str(case_id)

    # Usuń potencjalne spacje z case_id w logu
    event_log["case_id"] = event_log["case_id"].astype(str).str.strip()

    # Sprawdź, czy case_id istnieje w event_log'u
    if case_id_str not in event_log['case_id'].astype(str).unique():
        raise ValueError(f"Case ID {case_id} does not exist in the event log.")

    # Filtrowanie
    filtered_log = event_log[event_log["case_id"] == case_id_str].copy()

    # Wyliczenie średnich czasów wykonania aktywności w danym przypadku
    sum_serv_time = pm4py.get_service_time(
        filtered_log,
        start_timestamp_key="timestamp",
        timestamp_key="end_timestamp",
        aggregation_measure="sum"
    )

    return sum_serv_time

#41
def print_case_sum_act_times(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the sum service time in seconds for each activity for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID for which to calculate service times.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_sum_service_time_by_case_id(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    Sum service time of each activity for case ID 19:
    Activity 'ChartGenerator': 0.608 s
    Activity 'DocWriter': 2.0285 s
    Activity 'Search': 1.725 s
    Activity 'WebScraper': 2.446 s
    Activity '__start__': 0.603 s
    Activity 'ag_supervisor': 0.102 s
    Activity 'rg_supervisor': 23.023 s
    Activity 'test_supervisor': 0.748 s
    """
    sum_time = get_case_sum_act_times(event_log, case_id)
    print(f"Sum service time of each activity for case ID {case_id}:")
    for activity, time in sum_time.items():
        print(f"Activity '{activity}': {round(time,3)} s")


def get_case_self_dist_witnesses(event_log: pd.DataFrame, case_id: int) -> dict[str, list[list[str]]]:
    """
    Return the minimum self-distance witnesses for all activities for a specific case ID,
    considering both activity name and resource.

    :param event_log: Event log data containing events with case IDs, activity names, and resources.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve the witnesses for.
    :type case_id: int
    :return: A dictionary of activities with their witnesses for the specified case ID.
    :rtype: dict
    :raises ValueError: If the case ID does not exist in the event log.

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_case_self_dist_witnesses(event_log,19))
    Event log loaded and formated from file: files/examples.csv
    {'__start__': [['test_supervisor']], 'test_supervisor': [['__start__', 'ag_supervisor'], ['__start__', 'rg_supervisor']], 'rg_supervisor': [['Search'], ['WebScraper']], 'Search': [['rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor']], 'WebScraper': [['rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor']], 'ag_supervisor': [['DocWriter'], ['ChartGenerator']], 'DocWriter': [['ag_supervisor']]}
    """
    # Konwersja case_id do int dla spójności
    event_log['case_id'] = event_log['case_id'].astype(int)
    case_id = int(case_id)

    # Sprawdź, czy case_id istnieje w dzienniku zdarzeń
    if case_id not in event_log['case_id'].unique():
        raise ValueError(f"Case ID {case_id} nie istnieje w dzienniku zdarzeń.")

    # Filtrowanie dziennika zdarzeń dla określonego case_id
    filtered_event_log = event_log[event_log['case_id'] == case_id].copy()

    # Sprawdzenie, czy po filtrowaniu dziennik zdarzeń nie jest pusty
    if filtered_event_log.empty:
        return {}

    # Resetowanie indeksu, aby zapewnić, że indeksy zaczynają się od 0
    filtered_event_log.reset_index(drop=True, inplace=True)

    # Znajdź unikalne kombinacje aktywność-zasób
    unique_pairs = []
    for _, row in filtered_event_log.iterrows():
        pair = (row['concept:name'], row['org:resource'])
        if pair not in unique_pairs:
            unique_pairs.append(pair)

    corrected_witnesses = {}

    # Dla każdej unikalnej pary aktywność-zasób
    for activity, resource in unique_pairs:
        # Znajdź indeksy dla tej konkretnej kombinacji aktywność-zasób
        activity_mask = (filtered_event_log['concept:name'] == activity) & (
                    filtered_event_log['org:resource'] == resource)
        indices = filtered_event_log[activity_mask].index.tolist()

        # Pomiń jeśli nie ma przynajmniej dwóch wystąpień
        if len(indices) < 2:
            continue

        # Wylicz przerwy między kolejnymi wystąpieniami
        gaps = []
        consecutive_indices = []

        for i in range(len(indices) - 1):
            gap = indices[i + 1] - indices[i] - 1

            # Sprawdź czy między wystąpieniami nie ma tej samej aktywności z innym zasobem
            events_between = filtered_event_log.iloc[indices[i] + 1:indices[i + 1]]
            if not any((events_between['concept:name'] == activity) & (events_between['org:resource'] != resource)):
                gaps.append(gap)
                consecutive_indices.append((indices[i], indices[i + 1]))

        # Jeśli nie ma żadnych właściwych przerw, pomiń tę aktywność
        if not gaps:
            continue

        min_distance = min(gaps)

        # Zidentyfikuj świadków dla minimalnych odległości własnych
        witness_sequences = []
        for start_idx, end_idx in consecutive_indices:
            gap_size = end_idx - start_idx - 1
            if gap_size == min_distance:
                # Wydobycie eventów pomiędzy
                gap_events = filtered_event_log.iloc[start_idx + 1:end_idx]['concept:name'].tolist()
                # Wyłącz aktywność z listy
                gap_events = [event for event in gap_events if event != activity]
                # Dodaj tylko nie pustę przerwy
                if gap_events:
                    witness_sequences.append(gap_events)

        # Deduplikacja sekwencji z zachowaniem ich kolejności
        unique_sequences = list(map(list, {tuple(seq) for seq in witness_sequences}))
        # Dodaj tylko jeśli są świadkowie
        if unique_sequences:
            corrected_witnesses[activity] = unique_sequences

    return corrected_witnesses

def print_case_self_dist_witnesses(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Print the minimum self-distance witnesses for all activities for a specific case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and print the witnesses for.
    :type case_id: int

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_case_self_dist_witnesses(event_log,19)
    Event log loaded and formated from file: files/examples.csv
    Minimum self distance witnesses for case ID 19: {'__start__': [['test_supervisor']], 'test_supervisor': [['__start__', 'ag_supervisor'], ['__start__', 'rg_supervisor']], 'rg_supervisor': [['Search'], ['WebScraper']], 'Search': [['rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor']], 'WebScraper': [['rg_supervisor', 'test_supervisor', '__start__', 'rg_supervisor']], 'ag_supervisor': [['DocWriter'], ['ChartGenerator']], 'DocWriter': [['ag_supervisor']]}
    """
    witnesses = get_case_self_dist_witnesses(event_log, case_id)
    print(f"Minimum self distance witnesses for case ID {case_id}: {witnesses}")

#43
def print_case_analysis(event_log: pd.DataFrame, case_id: int) -> None:
    """
    Run multiple analyses on single case_id and print the results.

    :param event_log: The event log data to analyze.
    :type event_log: pd.DataFrame
    :param case_id: The case ID to retrieve and analyze.
    :type case_id: int

    **Example:**

    .. code-block:: python

        csv_output = "files/examples.csv"
        event_log = load_event_log(csv_output)
        print_full_analysis_by_id(event_log,19)
        # Event log loaded and formated from file: files/examples.csv
        #
        # #########################START#########################
        #
        # Start activity for case ID 1: __start__
        #
        # End activity for case ID 1: test_supervisor
        #
        # Count of each activity for case ID 1:
        # Activity '__start__': 4
        # Activity 'test_supervisor': 4
        # Activity 'rg_supervisor': 4
        # Activity 'Search': 1
        # Activity 'WebScraper': 1
        # Activity 'ag_supervisor': 4
        # Activity 'DocWriter': 1
        # Activity 'NoteTaker': 1
        # Activity 'ChartGenerator': 1
        #
        # Activity sequence for case ID 1: ['__start__', 'test_supervisor', '__start__', 'rg_supervisor', 'Search', 'rg_supervisor', 'WebScraper', 'rg_supervisor', 'test_supervisor', '__start__', 'ag_supervisor', 'DocWriter', 'ag_supervisor', 'NoteTaker', 'ag_supervisor', 'ChartGenerator', 'ag_supervisor', 'test_supervisor', '__start__', 'rg_supervisor', 'test_supervisor']
        # Probability: 0.333
        #
        # Minimum self distances for case ID 1: {'__start__': 1, 'ag_supervisor': 1, 'rg_supervisor': 1, 'test_supervisor': 2}
        #
        # Minimum self distance witnesses for case ID 1: {'__start__': [['test_supervisor']], 'test_supervisor': [['__start__', 'rg_supervisor']], 'rg_supervisor': [['WebScraper'], ['Search']], 'ag_supervisor': [['NoteTaker'], ['DocWriter'], ['ChartGenerator']]}
        #
        # Rework counts for case ID 1: {'__start__': 4, 'test_supervisor': 4, 'rg_supervisor': 4, 'ag_supervisor': 4}
        #
        # Sum service time of each activity for case ID 1:
        # Activity 'ChartGenerator': 0.567 s
        # Activity 'DocWriter': 0.712 s
        # Activity 'NoteTaker': 0.616 s
        # Activity 'Search': 0.502 s
        # Activity 'WebScraper': 0.506 s
        # Activity '__start__': 3.137 s
        # Activity 'ag_supervisor': 0.018 s
        # Activity 'rg_supervisor': 3.446 s
        # Activity 'test_supervisor': 0.013 s
        #
        # Duration for case ID 1: 43.88 s
        #
        # #########################END#########################
    """

    print("\n"+"#"*25+"START"+"#"*25+"\n")

    print_case_start(event_log, case_id)
    print()

    print_case_end(event_log, case_id)
    print()

    print_case_act_counts(event_log, case_id)
    print()

    print_case_sequence_prob(event_log, case_id)
    print()

    print_case_min_self_dists(event_log, case_id)
    print()

    print_case_self_dist_witnesses(event_log, case_id)
    print()

    print_case_act_reworks(event_log, case_id)
    print()

    print_case_sum_act_times(event_log, case_id)
    print()

    print_case_duration(event_log, case_id)

    print("\n"+"#"*25+"END"+"#"*25)