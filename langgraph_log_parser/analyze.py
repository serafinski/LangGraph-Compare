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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    Event log loaded and formated from file: files/examples.csv
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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_start_activities(event_log))
    Event log loaded and formated from file: files/examples.csv
    {'__start__': 8}
    """
    start_activities = pm4py.get_start_activities(event_log)
    return start_activities


#3
def print_all_start_activities(event_log):
    """
    Print the start activities of the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_start_activities(event_log)
    Event log loaded and formated from file: files/examples.csv
    Start activities: {'__start__': 8}
    """
    start_activities = get_all_start_activities(event_log)
    print("Start activities:", start_activities)


#4
def get_all_end_activities(event_log):
    """
    Get the end activities of the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: End activities and their counts.
    :rtype: dict

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_end_activities(event_log))
    Event log loaded and formated from file: files/examples.csv
    {'chatbot_node': 2, 'supervisor': 3, 'call_tool': 1, 'chart_generator': 2}
    """
    end_activities = pm4py.get_end_activities(event_log)
    return end_activities


#5
def print_all_end_activities(event_log):
    """
    Print the end activities of the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_end_activities(event_log)
    Event log loaded and formated from file: files/examples.csv
    End activities: {'chatbot_node': 2, 'supervisor': 3, 'call_tool': 1, 'chart_generator': 2}
    """
    end_activities = get_all_end_activities(event_log)
    print("End activities:", end_activities)


#6
def get_all_activities_count(event_log):
    """
    Get the counts of every activity in the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Activity counts.
    :rtype: dict

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_activities_count(event_log))
    Event log loaded and formated from file: files/examples.csv
    {'__start__': 20, 'supervisor': 19, 'Researcher': 15, 'call_tool': 14, 'agent': 9, 'chart_generator': 6, 'tools': 4, 'chatbot_node': 3, 'ResearchTeam': 3, 'PaperWritingTeam': 2, 'ChartGenerator': 2, 'Coder': 1, 'Search': 1, 'WebScraper': 1}
    """
    activities = pm4py.get_event_attribute_values(event_log, 'concept:name')
    return activities


#7
def print_all_activities_count(event_log):
    """
    Print the counts of every activity in the event log.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_activities_count(event_log)
    Event log loaded and formated from file: files/examples.csv
    Count of each activity: {'__start__': 20, 'supervisor': 19, 'Researcher': 15, 'call_tool': 14, 'agent': 9, 'chart_generator': 6, 'tools': 4, 'chatbot_node': 3, 'ResearchTeam': 3, 'PaperWritingTeam': 2, 'ChartGenerator': 2, 'Coder': 1, 'Search': 1, 'WebScraper': 1}
    """
    activities = get_all_activities_count(event_log)
    print("Count of each activity:", activities)


#8
def get_all_sequences(event_log):
    """
    Return activity sequences for every case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Mapping of case IDs to their activity sequences.
    :rtype: dict

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_sequences(event_log))
    Event log loaded and formated from file: files/examples.csv
    {1: ['__start__', 'chatbot_node'], 2: ['__start__', 'chatbot_node', 'tools', 'chatbot_node'], 4: ['__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator', '__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool'], 5: ['__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator'], 6: ['__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator'], 9: ['__start__', 'supervisor', '__start__', 'agent', 'Researcher', 'supervisor'], 10: ['__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'Coder', 'supervisor'], 15: ['__start__', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'Search', 'supervisor', '__start__', 'agent', 'WebScraper', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor']}
    """
    # Tworzymy słownik, który będzie przechowywał sekwencje aktywności dla każdego case_id
    sequences_by_case = defaultdict(list)

    # Budujemy sekwencje dla każdego case_id
    for _, row in event_log.iterrows():
        # Upewnienie, że case_id jest int'em
        case_id = int(row['case_id'])
        activity = row['activity']
        sequences_by_case[case_id].append(activity)

        # Sortowanie po id
        sorted_sequences = dict(sorted(sequences_by_case.items()))
    return sorted_sequences


#9
def print_all_sequences(event_log):
    """
    Print sequences for every case ID in the event log, sorted numerically by case ID.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_sequences(event_log)
    Event log loaded and formated from file: files/examples.csv
    All sequences:
    Case ID 1: ['__start__', 'chatbot_node']
    Case ID 2: ['__start__', 'chatbot_node', 'tools', 'chatbot_node']
    Case ID 4: ['__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator', '__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool']
    Case ID 5: ['__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator']
    Case ID 6: ['__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator']
    Case ID 9: ['__start__', 'supervisor', '__start__', 'agent', 'Researcher', 'supervisor']
    Case ID 10: ['__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'Coder', 'supervisor']
    Case ID 15: ['__start__', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'Search', 'supervisor', '__start__', 'agent', 'WebScraper', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor']
    """
    # Sekwencja dla każdego case_id
    sequences_by_case = get_all_sequences(event_log)

    print("All sequences:")

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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_sequences_with_probabilities(event_log))
    Event log loaded and formated from file: files/examples.csv
    [(1, ('__start__', 'chatbot_node'), 0.125), (2, ('__start__', 'chatbot_node', 'tools', 'chatbot_node'), 0.125), (4, ('__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator', '__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool'), 0.125), (5, ('__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator'), 0.125), (6, ('__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator'), 0.125), (9, ('__start__', 'supervisor', '__start__', 'agent', 'Researcher', 'supervisor'), 0.125), (10, ('__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'Coder', 'supervisor'), 0.125), (15, ('__start__', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'Search', 'supervisor', '__start__', 'agent', 'WebScraper', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor'), 0.125)]
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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_sequences_with_probabilities(event_log)
    Event log loaded and formated from file: files/examples.csv
    ID of last sequence occurrence with probability of occurrence:
    Case ID 1: ('__start__', 'chatbot_node'), 0.125
    Case ID 2: ('__start__', 'chatbot_node', 'tools', 'chatbot_node'), 0.125
    Case ID 4: ('__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator', '__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool'), 0.125
    Case ID 5: ('__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator'), 0.125
    Case ID 6: ('__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator'), 0.125
    Case ID 9: ('__start__', 'supervisor', '__start__', 'agent', 'Researcher', 'supervisor'), 0.125
    Case ID 10: ('__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'Coder', 'supervisor'), 0.125
    Case ID 15: ('__start__', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'Search', 'supervisor', '__start__', 'agent', 'WebScraper', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor'), 0.125
    """
    sequences_with_probabilities = get_all_sequences_with_probabilities(event_log)

    print("ID of last sequence occurrence with probability of occurrence:")
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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_minimum_self_distances(event_log))
    Event log loaded and formated from file: files/examples.csv
    {'1': {}, '2': {'chatbot_node': 1}, '4': {'Researcher': 1, '__start__': 6, 'call_tool': 1, 'chart_generator': 1}, '5': {'Researcher': 1, 'call_tool': 1, 'chart_generator': 1}, '6': {'Researcher': 1, 'call_tool': 2, 'chart_generator': 1}, '9': {'__start__': 1, 'supervisor': 3}, '10': {'__start__': 1, 'agent': 1, 'supervisor': 5}, '15': {'ChartGenerator': 5, 'PaperWritingTeam': 15, 'ResearchTeam': 3, '__start__': 1, 'agent': 1, 'supervisor': 1, 'tools': 5}}
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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_minimum_self_distances(event_log)
    Event log loaded and formated from file: files/examples.csv
    Minimal self-distances for every activity:
    Case ID 1: {}
    Case ID 2: {'chatbot_node': 1}
    Case ID 4: {'Researcher': 1, '__start__': 6, 'call_tool': 1, 'chart_generator': 1}
    Case ID 5: {'Researcher': 1, 'call_tool': 1, 'chart_generator': 1}
    Case ID 6: {'Researcher': 1, 'call_tool': 2, 'chart_generator': 1}
    Case ID 9: {'__start__': 1, 'supervisor': 3}
    Case ID 10: {'__start__': 1, 'agent': 1, 'supervisor': 5}
    Case ID 15: {'ChartGenerator': 5, 'PaperWritingTeam': 15, 'ResearchTeam': 3, '__start__': 1, 'agent': 1, 'supervisor': 1, 'tools': 5}
    """
    min_self_distances = get_all_minimum_self_distances(event_log)

    print("Minimal self-distances for every activity:")
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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_rework_counts(event_log))
    Event log loaded and formated from file: files/examples.csv
    {'1': {}, '2': {'chatbot_node': 2}, '4': {'__start__': 2, 'Researcher': 9, 'call_tool': 9, 'chart_generator': 2}, '5': {'Researcher': 3, 'call_tool': 3, 'chart_generator': 2}, '6': {'Researcher': 2, 'call_tool': 2, 'chart_generator': 2}, '9': {'__start__': 2, 'supervisor': 2}, '10': {'__start__': 2, 'supervisor': 2, 'agent': 2}, '15': {'__start__': 10, 'supervisor': 15, 'agent': 6, 'ResearchTeam': 3, 'PaperWritingTeam': 2, 'tools': 2, 'ChartGenerator': 2}}
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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_rework_counts(event_log)
    Event log loaded and formated from file: files/examples.csv
    Count of activity rework:
    Case ID 1: {}
    Case ID 2: {'chatbot_node': 2}
    Case ID 4: {'__start__': 2, 'Researcher': 9, 'call_tool': 9, 'chart_generator': 2}
    Case ID 5: {'Researcher': 3, 'call_tool': 3, 'chart_generator': 2}
    Case ID 6: {'Researcher': 2, 'call_tool': 2, 'chart_generator': 2}
    Case ID 9: {'__start__': 2, 'supervisor': 2}
    Case ID 10: {'__start__': 2, 'supervisor': 2, 'agent': 2}
    Case ID 15: {'__start__': 10, 'supervisor': 15, 'agent': 6, 'ResearchTeam': 3, 'PaperWritingTeam': 2, 'tools': 2, 'ChartGenerator': 2}
    """
    rework_counts_by_case = get_all_rework_counts(event_log)

    print("Count of activity rework:")
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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_activities_mean_service_time(event_log))
    Event log loaded and formated from file: files/examples.csv
    {'ChartGenerator': 0.431036, 'Coder': 0.618058, 'PaperWritingTeam': 0.597055, 'ResearchTeam': 0.8091940000000001, 'Researcher': 3.5640768, 'Search': 0.598059, 'WebScraper': 0.8930849999999999, '__start__': 2.3303979999999997, 'agent': 0.030281333333333334, 'call_tool': 7.828810357142857, 'chart_generator': 56.312364, 'chatbot_node': 0.8704093333333334, 'supervisor': 0.03221426315789473, 'tools': 1.068717}
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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_activities_mean_service_time(event_log)
    Event log loaded and formated from file: files/examples.csv
    Mean duration of every activity (in sec): {'ChartGenerator': 0.431036, 'Coder': 0.618058, 'PaperWritingTeam': 0.597055, 'ResearchTeam': 0.8091940000000001, 'Researcher': 3.5640768, 'Search': 0.598059, 'WebScraper': 0.8930849999999999, '__start__': 2.3303979999999997, 'agent': 0.030281333333333334, 'call_tool': 7.828810357142857, 'chart_generator': 56.312364, 'chatbot_node': 0.8704093333333334, 'supervisor': 0.03221426315789473, 'tools': 1.068717}
    """
    mean_serv_time = get_all_activities_mean_service_time(event_log)
    print("Mean duration of every activity (in sec):", mean_serv_time)


#30
def get_all_cases_durations(event_log):
    """
    Calculate the duration of each case in seconds.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame
    :return: Case durations.
    :rtype: dict

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_cases_durations(event_log))
    Event log loaded and formated from file: files/examples.csv
    {'1': 0.7335699999999999, '2': 5.178459, '4': 471.634856, '5': 18.039546, '6': 15.052201, '9': 7.484676, '10': 3.326793, '15': 40.460205}
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
    Print the duration of each case in seconds.

    :param event_log: Event log data.
    :type event_log: pd.DataFrame

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_cases_durations(event_log)
    Event log loaded and formated from file: files/examples.csv
    Duration of the case:
    Case ID 1: 0.7335699999999999 s
    Case ID 2: 5.178459 s
    Case ID 4: 471.634856 s
    Case ID 5: 18.039546 s
    Case ID 6: 15.052201 s
    Case ID 9: 7.484676 s
    Case ID 10: 3.326793 s
    Case ID 15: 40.460205 s
    """
    case_durations = get_all_cases_durations(event_log)
    print("Duration of the case:")

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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print(get_all_self_distance_witnesses(event_log))
    Event log loaded and formated from file: files/examples.csv
    {1: {}, 2: {'chatbot_node': [['tools']]}, 4: {'__start__': [['Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator']], 'Researcher': [['call_tool']], 'call_tool': [['Researcher']], 'chart_generator': [['call_tool']]}, 5: {'Researcher': [['call_tool']], 'call_tool': [['Researcher']], 'chart_generator': [['call_tool']]}, 6: {'Researcher': [['call_tool']], 'call_tool': [['Researcher', 'chart_generator']], 'chart_generator': [['call_tool']]}, 9: {'__start__': [['supervisor']], 'supervisor': [['__start__', 'agent', 'Researcher']]}, 10: {'__start__': [['supervisor']], 'supervisor': [['__start__', 'agent', 'tools', 'agent', 'Coder']], 'agent': [['tools']]}, 15: {'__start__': [['supervisor']], 'supervisor': [['__start__'], ['PaperWritingTeam'], ['ResearchTeam']], 'agent': [['tools']], 'ResearchTeam': [['supervisor', '__start__', 'supervisor']], 'PaperWritingTeam': [['supervisor', '__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor']], 'tools': [['agent', 'ChartGenerator', 'supervisor', '__start__', 'agent']], 'ChartGenerator': [['supervisor', '__start__', 'agent', 'tools', 'agent']]}}
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
            activity_indices[activity] = filtered_event_log[
                filtered_event_log['concept:name'] == activity].index.tolist()

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

    **Example:**

    >>> csv_output = "files/examples.csv"
    >>> event_log = load_event_log(csv_output)
    >>> print_all_self_distance_witnesses(event_log)
    Event log loaded and formated from file: files/examples.csv
    Witnesses of minimum self-distances:
    Case ID 1: {}
    Case ID 2: {'chatbot_node': [['tools']]}
    Case ID 4: {'__start__': [['Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator']], 'Researcher': [['call_tool']], 'call_tool': [['Researcher']], 'chart_generator': [['call_tool']]}
    Case ID 5: {'Researcher': [['call_tool']], 'call_tool': [['Researcher']], 'chart_generator': [['call_tool']]}
    Case ID 6: {'Researcher': [['call_tool']], 'call_tool': [['Researcher', 'chart_generator']], 'chart_generator': [['call_tool']]}
    Case ID 9: {'__start__': [['supervisor']], 'supervisor': [['__start__', 'agent', 'Researcher']]}
    Case ID 10: {'__start__': [['supervisor']], 'supervisor': [['__start__', 'agent', 'tools', 'agent', 'Coder']], 'agent': [['tools']]}
    Case ID 15: {'__start__': [['supervisor']], 'supervisor': [['__start__'], ['ResearchTeam'], ['PaperWritingTeam']], 'agent': [['tools']], 'ResearchTeam': [['supervisor', '__start__', 'supervisor']], 'PaperWritingTeam': [['supervisor', '__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor']], 'tools': [['agent', 'ChartGenerator', 'supervisor', '__start__', 'agent']], 'ChartGenerator': [['supervisor', '__start__', 'agent', 'tools', 'agent']]}
    """
    all_msd_witnesses = get_all_self_distance_witnesses(event_log)

    print("Witnesses of minimum self-distances:")
    for case_id, witnesses in all_msd_witnesses.items():
        print(f"Case ID {case_id}: {witnesses}")


#42
def print_full_analysis(event_log):
    """
    Run multiple analyses on the event log and print the results.

    :param event_log: The event log data to analyze.
    :type event_log: pd.DataFrame

    **Example**:

    .. code-block:: python

        csv_output = "files/examples.csv"
        event_log = load_event_log(csv_output)
        print_all_self_distance_witnesses(event_log)
        # Event log loaded and formated from file: files/examples.csv
        #
        # ####################START###########################
        #
        # Start activities: {'__start__': 8}
        #
        # End activities: {'chatbot_node': 2, 'supervisor': 3, 'call_tool': 1, 'chart_generator': 2}
        #
        # Count of each activity: {'__start__': 20, 'supervisor': 19, 'Researcher': 15, 'call_tool': 14, 'agent': 9, 'chart_generator': 6, 'tools': 4, 'chatbot_node': 3, 'ResearchTeam': 3, 'PaperWritingTeam': 2, 'ChartGenerator': 2, 'Coder': 1, 'Search': 1, 'WebScraper': 1}
        #
        # All sequences:
        # Case ID 1: ['__start__', 'chatbot_node']
        # Case ID 2: ['__start__', 'chatbot_node', 'tools', 'chatbot_node']
        # Case ID 4: ['__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator', '__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool']
        # Case ID 5: ['__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator']
        # Case ID 6: ['__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator']
        # Case ID 9: ['__start__', 'supervisor', '__start__', 'agent', 'Researcher', 'supervisor']
        # Case ID 10: ['__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'Coder', 'supervisor']
        # Case ID 15: ['__start__', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'Search', 'supervisor', '__start__', 'agent', 'WebScraper', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor']
        #
        # ID of last sequence occurrence with probability of occurrence:
        # Case ID 1: ('__start__', 'chatbot_node'), 0.125
        # Case ID 2: ('__start__', 'chatbot_node', 'tools', 'chatbot_node'), 0.125
        # Case ID 4: ('__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator', '__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'call_tool'), 0.125
        # Case ID 5: ('__start__', 'Researcher', 'call_tool', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator'), 0.125
        # Case ID 6: ('__start__', 'Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator'), 0.125
        # Case ID 9: ('__start__', 'supervisor', '__start__', 'agent', 'Researcher', 'supervisor'), 0.125
        # Case ID 10: ('__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'Coder', 'supervisor'), 0.125
        # Case ID 15: ('__start__', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'Search', 'supervisor', '__start__', 'agent', 'WebScraper', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', 'PaperWritingTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor', '__start__', 'supervisor', 'ResearchTeam', 'supervisor'), 0.125
        #
        # Minimal self-distances for every activity:
        # Case ID 1: {}
        # Case ID 2: {'chatbot_node': 1}
        # Case ID 4: {'Researcher': 1, '__start__': 6, 'call_tool': 1, 'chart_generator': 1}
        # Case ID 5: {'Researcher': 1, 'call_tool': 1, 'chart_generator': 1}
        # Case ID 6: {'Researcher': 1, 'call_tool': 2, 'chart_generator': 1}
        # Case ID 9: {'__start__': 1, 'supervisor': 3}
        # Case ID 10: {'__start__': 1, 'agent': 1, 'supervisor': 5}
        # Case ID 15: {'ChartGenerator': 5, 'PaperWritingTeam': 15, 'ResearchTeam': 3, '__start__': 1, 'agent': 1, 'supervisor': 1, 'tools': 5}
        #
        # Witnesses of minimum self-distances:
        # Case ID 1: {}
        # Case ID 2: {'chatbot_node': [['tools']]}
        # Case ID 4: {'__start__': [['Researcher', 'call_tool', 'Researcher', 'chart_generator', 'call_tool', 'chart_generator']], 'Researcher': [['call_tool']], 'call_tool': [['Researcher']], 'chart_generator': [['call_tool']]}
        # Case ID 5: {'Researcher': [['call_tool']], 'call_tool': [['Researcher']], 'chart_generator': [['call_tool']]}
        # Case ID 6: {'Researcher': [['call_tool']], 'call_tool': [['Researcher', 'chart_generator']], 'chart_generator': [['call_tool']]}
        # Case ID 9: {'__start__': [['supervisor']], 'supervisor': [['__start__', 'agent', 'Researcher']]}
        # Case ID 10: {'__start__': [['supervisor']], 'supervisor': [['__start__', 'agent', 'tools', 'agent', 'Coder']], 'agent': [['tools']]}
        # Case ID 15: {'__start__': [['supervisor']], 'supervisor': [['__start__'], ['ResearchTeam'], ['PaperWritingTeam']], 'agent': [['tools']], 'ResearchTeam': [['supervisor', '__start__', 'supervisor']], 'PaperWritingTeam': [['supervisor', '__start__', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor', '__start__', 'agent', 'tools', 'agent', 'ChartGenerator', 'supervisor']], 'tools': [['agent', 'ChartGenerator', 'supervisor', '__start__', 'agent']], 'ChartGenerator': [['supervisor', '__start__', 'agent', 'tools', 'agent']]}
        #
        # Count of activity rework:
        # Case ID 1: {}
        # Case ID 2: {'chatbot_node': 2}
        # Case ID 4: {'__start__': 2, 'Researcher': 9, 'call_tool': 9, 'chart_generator': 2}
        # Case ID 5: {'Researcher': 3, 'call_tool': 3, 'chart_generator': 2}
        # Case ID 6: {'Researcher': 2, 'call_tool': 2, 'chart_generator': 2}
        # Case ID 9: {'__start__': 2, 'supervisor': 2}
        # Case ID 10: {'__start__': 2, 'supervisor': 2, 'agent': 2}
        # Case ID 15: {'__start__': 10, 'supervisor': 15, 'agent': 6, 'ResearchTeam': 3, 'PaperWritingTeam': 2, 'tools': 2, 'ChartGenerator': 2}
        #
        # Mean duration of every activity (in sec): {'ChartGenerator': 0.431036, 'Coder': 0.618058, 'PaperWritingTeam': 0.597055, 'ResearchTeam': 0.8091940000000001, 'Researcher': 3.5640768, 'Search': 0.598059, 'WebScraper': 0.8930849999999999, '__start__': 2.3303979999999997, 'agent': 0.030281333333333334, 'call_tool': 7.828810357142857, 'chart_generator': 56.312364, 'chatbot_node': 0.8704093333333334, 'supervisor': 0.03221426315789473, 'tools': 1.068717}
        #
        # Duration of the case:
        # Case ID 1: 0.7335699999999999 s
        # Case ID 2: 5.178459 s
        # Case ID 4: 471.634856 s
        # Case ID 5: 18.039546 s
        # Case ID 6: 15.052201 s
        # Case ID 9: 7.484676 s
        # Case ID 10: 3.326793 s
        # Case ID 15: 40.460205 s
        #
        # ######################END###########################
    """

    print("\n####################START###########################\n")

    print_all_start_activities(event_log)
    print()

    print_all_end_activities(event_log)
    print()

    print_all_activities_count(event_log)
    print()

    print_all_sequences(event_log)
    print()

    print_all_sequences_with_probabilities(event_log)
    print()

    print_all_minimum_self_distances(event_log)
    print()

    print_all_self_distance_witnesses(event_log)
    print()

    print_all_rework_counts(event_log)
    print()

    print_all_activities_mean_service_time(event_log)
    print()

    print_all_cases_durations(event_log)

    print("\n######################END###########################")
