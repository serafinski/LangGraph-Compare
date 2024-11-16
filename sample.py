from langgraph_log_parser import *

database = "checkpoints.sqlite"
output = "files/sql_to_log_output.log"
csv_output = "files/examples.csv"

export_sqlite_to_log(database, output)
#
export_log_to_csv(output, csv_output)

# 1
event_log = load_event_log(csv_output)

print_full_analysis(event_log)
generate_prefix_tree(event_log)

# 2,3 - 100% GIT
print(get_all_start_activities(event_log))
print_all_start_activities(event_log)
#
# 4,5 - 100% GIT
print(get_end_activities(event_log))
print_all_end_activities(event_log)
#
# 6,7 - 100% GIT
print(get_all_activities_count(event_log))
print_all_activities_count(event_log)
#
# 8,9 - 100% GIT
print(get_all_sequences_by_case_id(event_log))
print_all_sequences_by_case_id(event_log)
#
# 10, 11 - 100% GIT
print(get_all_sequences_with_probabilities(event_log))
print_all_sequences_with_probabilities(event_log)
#
# 12,13 - 100% GIT
print(get_sequence_by_case_id(event_log,15))
print_sequence_by_case_id(event_log,15)
#
# 14, 15 - 100% GIT
print(get_sequence_with_probability_by_case_id(event_log,15))
print_sequence_with_probability_by_case_id(event_log,15)
#
# 16, 17 - 100% GIT
print(get_all_minimum_self_distances(event_log))
print_all_minimum_self_distances(event_log)
#
# 18,19 - 100% GIT
print(get_minimum_self_distances_by_case_id(event_log,10))
print_minimum_self_distances_by_case_id(event_log,10)

#20,21 - REQUIRES FIX (NEED TO DIFF WHEN Hierarchical Agent Teams)?
print(get_all_self_distance_witnesses(event_log))
print_all_self_distance_witnesses(event_log)

#22,23 REQUIRES FIX (NEED TO DIFF WHEN Hierarchical Agent Teams)?
print(get_self_distance_witnesses_by_case_id(event_log, 10))
print_self_distance_witnesses_by_case_id(event_log, 10)

# 24, 25 - 100% GIT
print(get_all_rework_counts(event_log))
print_all_rework_counts(event_log)
#
# 26, 27 - 100% GIT
print(get_rework_by_case_id(event_log,4))
print_rework_by_case_id(event_log,4)
#
# 28, 29 - 100% GIT
print(get_all_activities_mean_service_time(event_log))
print_all_activities_mean_service_time(event_log)

# 30, 31 - 100% GIT
print(get_all_cases_durations(event_log))
print_all_cases_durations(event_log)

# 32,33 - 100% GIT
print(get_case_duration_by_id(event_log,4))
print_case_duration_by_id(event_log,4)

# 34, 35 - 100% GIT
print(get_start_activity(event_log,15))
print_start_activity(event_log,15)

# 36, 37 - 100% GIT
print(get_end_activity(event_log,15))
print_end_activity(event_log,15)

# 38, 39
print(get_activities_count_by_case_id(event_log,15))
print_activities_count_by_case_id(event_log,15)

# 40, 41

# 42,43
print_full_analysis(event_log)
print_full_analysis_by_id(event_log,10)