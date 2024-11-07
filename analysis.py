import pandas as pd
import pm4py
import numpy as np
from collections import defaultdict

pd.set_option('display.max_columns', None)

# Ładowanie CSV do pandas DataFrame
file_path = 'files/examples.csv'
df = pd.read_csv(file_path)

# Formatowanie DataFrame dla PM4Py
df['timestamp'] = pd.to_datetime(df['timestamp'])
event_log = pm4py.format_dataframe(df, case_id='case_id', activity_key='activity', timestamp_key='timestamp')

######################
print("Początkowe aktywności:")
start_activities = pm4py.get_start_activities(event_log)
print(start_activities)

######################
print("Końcowe aktywności:")
end_activities = pm4py.get_end_activities(event_log)
print(end_activities)

######################
print("\nIlość wystąpień aktywności:")
activites = pm4py.get_event_attribute_values(event_log, 'concept:name')
print(activites)

######################
# Tworzymy słownik, który będzie przechowywał sekwencje aktywności dla każdego case_id
sequences_by_case = defaultdict(list)

# Budujemy sekwencje dla każdego case_id
for _, row in event_log.iterrows():
    case_id = row['case_id']
    activity = row['activity']
    sequences_by_case[case_id].append(activity)

# Generujemy probabilistyczny język
language = pm4py.get_stochastic_language(event_log)

# Tworzymy odwrotny słownik dla łatwego porównania
case_by_sequence = {tuple(seq): case_id for case_id, seq in sequences_by_case.items()}

print("\nSekwencje wraz z prawdopodobieństwem wystąpienia:")

# Sortujemy sequences_by_case według numerycznych wartości case_id
sorted_sequences = sorted(case_by_sequence.items(), key=lambda x: int(x[1]))

for sequence, case_id in sorted_sequences:
    probability = language[sequence]
    print(f"Case ID {case_id}: {sequence}, {probability}")

######################
print("\nMinimalne odległości własne (self-distances) dla każdej aktywności:")
unique_case_ids = event_log['case:concept:name'].unique()
sorted_case_ids = np.sort(unique_case_ids.astype(int)).astype(str)

# Iterujemy po każdym case_id i obliczamy minimalne odległości własne dla jego aktywności
for case_id in sorted_case_ids:
    # Filtrowanie logu dla bieżącego case_id
    filtered_event_log = event_log[event_log['case:concept:name'] == case_id]

    # Obliczanie minimalnych odległości własnych dla wybranego case_id
    msd = pm4py.get_minimum_self_distances(filtered_event_log,
                                           activity_key='concept:name',
                                           case_id_key='case:concept:name',
                                           timestamp_key='time:timestamp')

    print(f"Case ID {case_id}: {msd}")

######################
print("\nŚwiadkowie odległości własnych:")
unique_case_ids = event_log['case:concept:name'].unique()
sorted_case_ids = np.sort(unique_case_ids.astype(int)).astype(str)

for case_id in sorted_case_ids:
    # Filtrowanie logu dla bieżącego case_id
    filtered_event_log = event_log[event_log['case:concept:name'] == case_id]

    # Obliczanie świadków minimalnych odległości własnych dla wybranego case_id
    msd_wit = pm4py.get_minimum_self_distance_witnesses(filtered_event_log,
                                                        activity_key='concept:name',
                                                        case_id_key='case:concept:name',
                                                        timestamp_key='time:timestamp')

    # Wyświetlanie wyników dla bieżącego case_id na jednej linii
    # Sortujemy świadków dla lepszej czytelności
    sorted_msd_wit = {activity: sorted(witnesses) for activity, witnesses in msd_wit.items()}
    print(f"Case ID {case_id}: {sorted_msd_wit}")

######################
print("\nIlość wystąpień powtórzenia aktywności (rework):")
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

    # Wyświetlanie wyników dla bieżącego case_id na jednej linii
    print(f"Case ID {case_id}: {rework_counts}")

######################
print("\nŚredni czas wykonania aktywności:")
mean_serv_time = pm4py.get_service_time(event_log, start_timestamp_key='timestamp',timestamp_key='end_timestamp', aggregation_measure='mean')
print(mean_serv_time)

######################
print("\nCzas trwania case'a:")
# Pobranie unikalnych identyfikatorów przypadków (case_id)
unique_case_ids = event_log['case:concept:name'].unique()
sorted_array = np.sort(unique_case_ids.astype(int)).astype(str)

# Iterowanie po każdym case_id i uzyskanie jego czasu trwania
case_durations = {}
for case_id in sorted_array:
    duration = pm4py.get_case_duration(event_log, case_id)
    case_durations[case_id] = duration

# Wyświetlanie czasu trwania dla każdego case_id
for case_id in sorted_array:
    print(f"Case ID {case_id}: {case_durations[case_id]}")