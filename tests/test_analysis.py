import os
import pandas as pd

from langgraph_log_parser.analysis import (
    load_event_log, get_start_activities, get_end_activities,
    get_activity_counts, get_sequences_by_case, print_all_sequences,
    print_sequences_with_probabilities, print_minimum_self_distances,
    print_self_distance_witnesses, get_rework_counts, get_mean_service_time,
    get_case_durations, print_full_analysis, generate_prefix_tree
)


def test_load_event_log():
    # Define the path to the test CSV file
    test_file_path = "files/tests/test_csv_output.csv"

    # Ensure the file exists before proceeding
    assert os.path.exists(test_file_path), "The test CSV file does not exist at the specified path."

    # Call the load_event_log function
    event_log_df = load_event_log(test_file_path)

    # Check if the result is a DataFrame
    assert isinstance(event_log_df, pd.DataFrame), "The result should be a pandas DataFrame."

    # Check that essential columns for PM4Py are present in the formatted DataFrame
    required_columns = {"case:concept:name", "concept:name", "time:timestamp"}
    missing_columns = required_columns - set(event_log_df.columns)
    assert not missing_columns, f"Missing required columns in the DataFrame: {missing_columns}"

    # Check that 'time:timestamp' is of datetime type
    assert pd.api.types.is_datetime64_any_dtype(event_log_df['time:timestamp']), "The 'time:timestamp' column should be of datetime type."

    print("Test for load_event_log passed successfully.")

def test_get_start_activities(sample_event_log):
    # Test retrieving start activities
    start_activities = get_start_activities(sample_event_log)
    assert isinstance(start_activities, dict)

def test_get_end_activities(sample_event_log):
    # Test retrieving end activities
    end_activities = get_end_activities(sample_event_log)
    assert isinstance(end_activities, dict)

def test_get_activity_counts(sample_event_log):
    # Test retrieving activity counts
    activity_counts = get_activity_counts(sample_event_log)
    assert isinstance(activity_counts, dict)

def test_get_sequences_by_case(sample_event_log):
    # Test retrieving sequences by case ID
    sequences_by_case = get_sequences_by_case(sample_event_log)
    assert isinstance(sequences_by_case, dict)
    for case_id, sequence in sequences_by_case.items():
        assert isinstance(case_id, (int, str))
        assert isinstance(sequence, list)

def test_print_all_sequences(sample_event_log, capsys):
    # Test printing all sequences
    print_all_sequences(sample_event_log)
    captured = capsys.readouterr()
    assert "Wszystkie sekwencje" in captured.out

def test_print_sequences_with_probabilities(sample_event_log, capsys):
    # Test printing sequences with probabilities
    print_sequences_with_probabilities(sample_event_log)
    captured = capsys.readouterr()
    assert "ID ostatniego wystąpienia" in captured.out

def test_print_minimum_self_distances(sample_event_log, capsys):
    # Test printing minimum self-distances
    print_minimum_self_distances(sample_event_log)
    captured = capsys.readouterr()
    assert "Minimalne odległości własne" in captured.out

def test_print_self_distance_witnesses(sample_event_log, capsys):
    # Test printing self-distance witnesses
    print_self_distance_witnesses(sample_event_log)
    captured = capsys.readouterr()
    assert "Świadkowie odległości własnych" in captured.out

def test_get_rework_counts(sample_event_log):
    # Test retrieving rework counts
    rework_counts = get_rework_counts(sample_event_log)
    assert isinstance(rework_counts, dict)
    for case_id, counts in rework_counts.items():
        assert isinstance(counts, dict)

def test_get_mean_service_time(sample_event_log):
    # Test retrieving mean service time
    mean_service_time = get_mean_service_time(sample_event_log)
    assert isinstance(mean_service_time, dict)

def test_get_case_durations(sample_event_log):
    # Test retrieving case durations
    case_durations = get_case_durations(sample_event_log)
    assert isinstance(case_durations, dict)

def test_print_full_analysis(sample_event_log, capsys):
    # Test full analysis printout
    print_full_analysis(sample_event_log)
    captured = capsys.readouterr()
    assert "######################END###########################" in captured.out

def test_generate_prefix_tree(sample_event_log, tmp_path):
    # Test prefix tree generation
    output_path = tmp_path / "tree.png"
    generate_prefix_tree(sample_event_log, output_path)
    assert output_path.exists()