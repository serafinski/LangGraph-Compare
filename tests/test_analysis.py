import os
import pandas as pd

from langgraph_log_parser.analysis import (
    load_event_log, get_all_start_activities, get_end_activities,
    get_each_activity_count, get_each_sequence_by_case_id, print_every_sequence_by_case_id,
    print_sequences_with_probabilities, print_all_minimum_self_distances,
    print_all_self_distance_witnesses, get_all_rework_counts, get_all_activities_mean_service_time,
    print_all_cases_durations, print_full_analysis, generate_prefix_tree
)


def test_load_event_log():
    """
    Test the `load_event_log` function to ensure it correctly loads and formats a CSV file as a PM4Py-compatible DataFrame.

    :raises AssertionError: If the test CSV file does not exist, the result is not a DataFrame, required columns are missing,
                            or the timestamp column is not of datetime type.
    """
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
    """
    Test the `get_start_activities` function to retrieve start activities.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :raises AssertionError: If the result is not a dictionary.
    """
    # Test retrieving start activities
    start_activities = get_all_start_activities(sample_event_log)
    assert isinstance(start_activities, dict)

def test_get_end_activities(sample_event_log):
    """
    Test the `get_end_activities` function to retrieve end activities.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :raises AssertionError: If the result is not a dictionary.
    """
    # Test retrieving end activities
    end_activities = get_end_activities(sample_event_log)
    assert isinstance(end_activities, dict)

def test_get_activity_counts(sample_event_log):
    """
    Test the `get_activity_counts` function to retrieve activity counts.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :raises AssertionError: If the result is not a dictionary.
    """
    # Test retrieving activity counts
    activity_counts = get_each_activity_count(sample_event_log)
    assert isinstance(activity_counts, dict)

def test_get_sequences_by_case(sample_event_log):
    """
    Test the `get_sequences_by_case` function to retrieve sequences by case ID.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :raises AssertionError: If the result is not a dictionary, or case IDs and sequences are not of valid types.
    """
    # Test retrieving sequences by case ID
    sequences_by_case = get_each_sequence_by_case_id(sample_event_log)
    assert isinstance(sequences_by_case, dict)
    for case_id, sequence in sequences_by_case.items():
        assert isinstance(case_id, (int, str))
        assert isinstance(sequence, list)

def test_print_all_sequences(sample_event_log, capsys):
    """
    Test the `print_all_sequences` function to verify that all sequences are printed correctly.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :param capsys: A pytest fixture to capture standard output.
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected output string is not in the captured output.
    """
    # Test printing all sequences
    print_every_sequence_by_case_id(sample_event_log)
    captured = capsys.readouterr()
    assert "Wszystkie sekwencje" in captured.out

def test_print_sequences_with_probabilities(sample_event_log, capsys):
    """
    Test the `print_sequences_with_probabilities` function to verify that probabilities are printed correctly.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :param capsys: A pytest fixture to capture standard output.
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected output string is not in the captured output.
    """
    # Test printing sequences with probabilities
    print_sequences_with_probabilities(sample_event_log)
    captured = capsys.readouterr()
    assert "ID ostatniego wystąpienia" in captured.out

def test_print_minimum_self_distances(sample_event_log, capsys):
    """
    Test the `print_minimum_self_distances` function to verify that minimum self-distances are printed correctly.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :param capsys: A pytest fixture to capture standard output.
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected output string is not in the captured output.
    """
    # Test printing minimum self-distances
    print_all_minimum_self_distances(sample_event_log)
    captured = capsys.readouterr()
    assert "Minimalne odległości własne" in captured.out

def test_print_self_distance_witnesses(sample_event_log, capsys):
    """
    Test the `print_self_distance_witnesses` function to verify that self-distance witnesses are printed correctly.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :param capsys: A pytest fixture to capture standard output.
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected output string is not in the captured output.
    """
    # Test printing self-distance witnesses
    print_all_self_distance_witnesses(sample_event_log)
    captured = capsys.readouterr()
    assert "Świadkowie odległości własnych" in captured.out

def test_get_rework_counts(sample_event_log):
    """
    Test the `get_rework_counts` function to retrieve rework counts for activities.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :raises AssertionError: If the result is not a dictionary or the counts are not valid.
    """
    # Test retrieving rework counts
    rework_counts = get_all_rework_counts(sample_event_log)
    assert isinstance(rework_counts, dict)
    for case_id, counts in rework_counts.items():
        assert isinstance(counts, dict)

def test_get_mean_service_time(sample_event_log):
    """
    Test the `get_mean_service_time` function to retrieve mean service times.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :raises AssertionError: If the result is not a dictionary.
    """
    # Test retrieving mean service time
    mean_service_time = get_all_activities_mean_service_time(sample_event_log)
    assert isinstance(mean_service_time, dict)

def test_get_case_durations(sample_event_log):
    """
    Test the `get_case_durations` function to retrieve case durations.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :raises AssertionError: If the result is not a dictionary.
    """
    # Test retrieving case durations
    case_durations = print_all_cases_durations(sample_event_log)
    assert isinstance(case_durations, dict)

def test_print_full_analysis(sample_event_log, capsys):
    """
    Test the `print_full_analysis` function to verify that the full analysis is printed correctly.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :param capsys: A pytest fixture to capture standard output.
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected output string is not in the captured output.
    """
    # Test full analysis printout
    print_full_analysis(sample_event_log)
    captured = capsys.readouterr()
    assert "######################END###########################" in captured.out

def test_generate_prefix_tree(sample_event_log, tmp_path):
    """
    Test the `generate_prefix_tree` function to verify that a prefix tree image is generated.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :param tmp_path: A pytest fixture providing a temporary directory.
    :type tmp_path: pathlib.Path
    :raises AssertionError: If the output file does not exist after the function is called.
    """
    # Test prefix tree generation
    output_path = tmp_path / "tree.png"
    generate_prefix_tree(sample_event_log, output_path)
    assert output_path.exists()