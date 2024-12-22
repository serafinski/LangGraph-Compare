from langgraph_log_parser.analyze import (
    get_starts, print_starts,
    get_ends, print_ends,
    get_act_counts, print_act_counts,
    get_sequences, print_sequences,
    get_sequence_probs, print_sequence_probs,
    get_min_self_dists, print_min_self_dists,
    get_act_reworks, print_act_reworks,
    get_global_act_reworks, print_global_act_reworks,
    get_mean_act_times, print_mean_act_times,
    get_durations, print_durations,
    get_avg_duration, print_avg_duration,
    get_self_dist_witnesses, print_self_dist_witnesses,
    print_analysis)

def test_get_starts(sample_event_log):
    """
    Test the `get_starts` function to verify it correctly identifies and counts start activities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If the result is not a dictionary or doesn't contain '__start__'
    """
    result = get_starts(sample_event_log)
    assert isinstance(result, dict), "get_starts should return a dictionary"
    assert '__start__' in result, "get_starts result should contain '__start__' key"
    assert isinstance(result['__start__'], int), "get_starts count should be an integer"

def test_print_starts(sample_event_log, capsys):
    """
    Test the `print_starts` function to verify it correctly outputs start activities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected output strings are not present in stdout
    """
    print_starts(sample_event_log)
    captured = capsys.readouterr()
    assert "Start activities:" in captured.out, "print_starts output should contain 'Start activities:' header"
    assert "__start__" in captured.out, "print_starts output should contain '__start__' activity"

def test_get_ends(sample_event_log):
    """
    Test the `get_ends` function to verify it correctly identifies and counts end activities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If the result is not a dictionary or doesn't contain 'test_supervisor'
    """
    result = get_ends(sample_event_log)
    assert isinstance(result, dict), "get_ends should return a dictionary"
    assert 'test_supervisor' in result, "get_ends result should contain 'test_supervisor' key"
    assert isinstance(result['test_supervisor'], int), "get_ends count should be an integer"

def test_print_ends(sample_event_log, capsys):
    """
    Test the `print_ends` function to verify it correctly outputs end activities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected output strings are not present in stdout
    """
    print_ends(sample_event_log)
    captured = capsys.readouterr()
    assert "End activities:" in captured.out, "print_ends output should contain 'End activities:' header"
    assert "test_supervisor" in captured.out, "print_ends output should contain 'test_supervisor' activity"

def test_get_act_counts(sample_event_log):
    """
    Test the `get_act_counts` function to verify it correctly counts all activities in the event log.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If the result doesn't contain expected activities or if counts are not positive integers
    """
    result = get_act_counts(sample_event_log)
    assert isinstance(result, dict), "get_act_counts should return a dictionary"

    expected_activities = {'ag_supervisor', '__start__',
                           'test_supervisor', 'rg_supervisor', 'DocWriter',
                           'NoteTaker', 'ChartGenerator', 'Search', 'WebScraper'
    }
    assert expected_activities.issubset(set(result.keys())), f"Missing expected activities: {expected_activities - set(result.keys())}"

    # Verify counts are integers and positive
    assert all(isinstance(count, int) and count > 0 for count in result.values()), "All activity counts should be positive integers"

def test_print_act_counts(sample_event_log, capsys):
    """
    Test the `print_act_counts` function to verify it correctly outputs activity counts.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected activity names and count information are not in stdout
    """
    print_act_counts(sample_event_log)
    captured = capsys.readouterr()
    expected_outputs = ["Count of each activity:", "ag_supervisor", "__start__",
                       "test_supervisor", "rg_supervisor", "DocWriter", "NoteTaker",
                       "ChartGenerator", "Search", "WebScraper"]

    for expected in expected_outputs:
        assert expected in captured.out, f"print_act_counts output missing '{expected}'"

def test_get_sequences(sample_event_log):
    """
    Test the `get_sequences` function to verify it correctly extracts activity sequences for each case.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If sequences are not properly formatted or don't start with '__start__'
    """
    result = get_sequences(sample_event_log)
    assert isinstance(result, dict), "get_sequences should return a dictionary"

    # Verify case IDs
    for case_id in [1, 2, 3]:
        assert case_id in result, f"Missing case ID {case_id} in sequences"

    # Verify sequence structure
    for case_id, sequence in result.items():
        assert isinstance(sequence, list), f"Sequence for case {case_id} should be a list"
        assert all(isinstance(act, str) for act in sequence), \
            f"All activities in sequence for case {case_id} should be strings"

    # Verify first activity in each sequence is '__start__'
    assert all(seq[0] == '__start__' for seq in result.values()), f"First activity in sequence for case {case_id} should be '__start__'"

def test_print_sequences(sample_event_log, capsys):
    """
    Test the `print_sequences` function to verify it correctly outputs all activity sequences.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected sequence information is not present in stdout
    """
    print_sequences(sample_event_log)
    captured = capsys.readouterr()
    assert "All sequences:" in captured.out, "print_sequences output missing 'All sequences:' header"

    # Verify all case IDs are present in output
    for case_id in [1, 2, 3]:
        assert f"Case ID {case_id}:" in captured.out, f"print_sequences output missing Case ID {case_id}"

def test_get_sequence_probs(sample_event_log):
    """
    Test the `get_sequence_probs` function to verify it correctly calculates sequence probabilities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If probabilities are not valid floats between 0 and 1
    """
    result = get_sequence_probs(sample_event_log)
    assert isinstance(result, list), "get_sequence_probs should return a list"

    assert len(result) == 3, "get_sequence_probs should return 3 cases"

    for case_id, sequence, prob in result:
        assert isinstance(case_id, int), f"Case ID {case_id} should be an integer"
        assert isinstance(sequence, tuple), f"Sequence for case {case_id} should be a tuple"
        assert isinstance(prob, float), f"Probability for case {case_id} should be a float"
        assert 0 <= prob <= 1, f"Probability {prob} for case {case_id} should be between 0 and 1"

def test_print_sequence_probs(sample_event_log, capsys):
    """
    Test the `print_sequence_probs` function to verify it correctly outputs sequence probabilities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected probability information is not present in stdout
    """
    print_sequence_probs(sample_event_log)
    captured = capsys.readouterr()
    assert "ID of last sequence occurrence with probability of occurrence:" in captured.out, "print_sequence_probs output missing header"

    # Verify all case IDs are present in output
    for case_id in [1, 2, 3]:
        assert f"Case ID {case_id}:" in captured.out, f"print_sequence_probs output missing Case ID {case_id}"
        assert "," in captured.out, "print_sequence_probs output missing probability values"

def test_min_self_dists(sample_event_log):
    """
    Test the `get_min_self_dists` function to verify it correctly calculates minimal self-distances.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If the result structure is incorrect or missing case IDs
    """
    result = get_min_self_dists(sample_event_log)
    assert isinstance(result, dict), "get_min_self_dists should return a dictionary"

    # Check for all case IDs
    for case_id in [1, 2, 3]:
        assert case_id in result, f"Missing case ID {case_id} in min_self_dists"
        assert isinstance(result[case_id], dict), f"Result for case {case_id} should be a dictionary"

def test_print_min_self_dists(sample_event_log, capsys):
    """
    Test the `print_min_self_dists` function to verify it correctly outputs minimal self-distances.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected self-distance information is not present in stdout
    """
    print_min_self_dists(sample_event_log)
    captured = capsys.readouterr()
    assert "Minimal self-distances for every activity:" in captured.out, "print_min_self_dists output missing header"

    for case_id in [1, 2, 3]:
        assert f"Case ID {case_id}:" in captured.out, f"print_min_self_dists output missing Case ID {case_id}"

def test_get_act_reworks(sample_event_log):
    """
    Test the `get_act_reworks` function to verify it correctly identifies activity rework instances.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If the result structure is incorrect or missing case IDs
    """
    result = get_act_reworks(sample_event_log)
    assert isinstance(result, dict), "get_act_reworks should return a dictionary"

    for case_id in [1, 2, 3]:
        assert case_id in result, f"Missing case ID {case_id} in act_reworks"
        assert isinstance(result[case_id], dict), f"Result for case {case_id} should be a dictionary"

def test_print_act_reworks(sample_event_log, capsys):
    """
    Test the `print_act_reworks` function to verify it correctly outputs activity rework counts.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected rework information is not present in stdout
    """
    print_act_reworks(sample_event_log)
    captured = capsys.readouterr()
    assert "Count of activity rework:" in captured.out, "print_act_reworks output missing header"

    for case_id in [1, 2, 3]:
        assert f"Case ID {case_id}:" in captured.out, f"print_act_reworks output missing Case ID {case_id}"

def test_get_global_act_reworks(sample_event_log):
    """
    Test the `get_global_act_reworks` function to verify it correctly calculates global rework counts.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If counts are negative or essential activities are missing
    """
    result = get_global_act_reworks(sample_event_log)
    assert isinstance(result, dict), "get_global_act_reworks should return a dictionary"
    # Verify all values are integers
    assert all(isinstance(count, int) for count in result.values()), "All global rework counts should be integers"
    # Verify all counts are non-negative
    assert all(count >= 0 for count in result.values()), "All global rework counts should be non-negative"
    # Check essential activities are present
    expected_activities = ['__start__', 'test_supervisor', 'rg_supervisor',
                           'ag_supervisor', 'NoteTaker', 'ChartGenerator', 'DocWriter']
    for activity in expected_activities:
        assert activity in result, f"Missing activity '{activity}' in global reworks"

def test_print_global_act_reworks(sample_event_log, capsys):
    """
    Test the `print_global_act_reworks` function to verify it correctly outputs global rework statistics.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected global rework information is not present in stdout
    """
    print_global_act_reworks(sample_event_log)
    captured = capsys.readouterr()

    assert "Activity" in captured.out, "print_global_act_reworks output missing header"

    # Verify activities are present in output
    expected_activities = ['__start__', 'test_supervisor', 'rg_supervisor',
                         'ag_supervisor', 'NoteTaker', 'ChartGenerator', 'DocWriter']
    for activity in expected_activities:
        assert activity in captured.out, f"print_global_act_reworks output missing activity '{activity}'"


def test_get_mean_act_times(sample_event_log):
    """
    Test the `get_mean_act_times` function to verify it correctly calculates average activity durations.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If times are negative or expected activities are missing
    """
    result = get_mean_act_times(sample_event_log)
    assert isinstance(result, dict), "get_mean_act_times should return a dictionary"

    expected_activities = ["ag_supervisor", "__start__", "test_supervisor", "rg_supervisor",
                           "DocWriter", "NoteTaker", "ChartGenerator", "Search", "WebScraper"]

    for activity in expected_activities:
        assert activity in result, f"Missing activity '{activity}' in mean times"

    assert all(isinstance(time, float) for time in result.values()), "All mean activity times should be floats"

    # Times should be non-negative
    assert all(time >= 0 for time in result.values()), "All mean activity times should be non-negative"

def test_print_mean_act_times(sample_event_log, capsys):
    """
    Test the `print_mean_act_times` function to verify it correctly outputs mean activity durations.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected duration information is not present in stdout
    """
    print_mean_act_times(sample_event_log)
    captured = capsys.readouterr()
    assert "Mean duration of every activity:" in captured.out, "print_mean_act_times output missing header"

    expected_activities = ["ag_supervisor", "__start__", "test_supervisor", "rg_supervisor",
                           "DocWriter", "NoteTaker", "ChartGenerator", "Search", "WebScraper"]

    for activity in expected_activities:
        assert activity in captured.out, f"print_mean_act_times output missing activity '{activity}'"

def test_get_durations(sample_event_log):
    """
    Test the `get_durations` function to verify it correctly calculates case durations.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If durations are not positive floats or cases are missing
    """
    result = get_durations(sample_event_log)
    assert isinstance(result, dict), "get_durations should return a dictionary"
    # Verify all case IDs have durations
    for case_id in ['1', '2', '3']:
        assert case_id in result, f"Missing case ID {case_id} in durations"
        assert isinstance(result[case_id], float), f"Duration for case {case_id} should be a float"
        assert result[case_id] > 0, f"Duration for case {case_id} should be positive"

def test_print_durations(sample_event_log, capsys):
    """
    Test the `print_durations` function to verify it correctly outputs case durations.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected duration information is not present in stdout
    """
    print_durations(sample_event_log)
    captured = capsys.readouterr()
    assert "Duration of the case:" in captured.out, "print_durations output missing header"

    for case_id in [1, 2, 3]:
        assert f"Case ID {case_id}:" in captured.out, f"print_durations output missing Case ID {case_id}"
        assert "s" in captured.out, "print_durations output missing time units"

def test_get_avg_duration(sample_event_log):
    """
    Test the `get_avg_duration` function to verify it correctly calculates the average case duration.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If the average duration is not a positive float
    """
    result = get_avg_duration(sample_event_log)
    assert isinstance(result, float), "get_avg_duration should return a float"

    # Duration should be positive
    assert result > 0, "Average duration should be positive"


def test_print_avg_duration(sample_event_log, capsys):
    """
    Test the `print_avg_duration` function to verify it correctly outputs average case duration.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected average duration information is not present in stdout
    """
    print_avg_duration(sample_event_log)
    captured = capsys.readouterr()
    assert "Average case duration:" in captured.out, "print_avg_duration output missing header"
    assert "s." in captured.out, "print_avg_duration output missing time units"

    # Extract the number from the output and verify it's a valid float
    output_parts = captured.out.split(':')
    if len(output_parts) > 1:
        assert len(output_parts) > 1, "print_avg_duration output missing value"
        duration_str = output_parts[1].strip().replace(' s.', '')
        duration_float = float(duration_str)
        assert isinstance(duration_float, float), "Duration value should be convertible to float"
        assert duration_float > 0, "Duration value should be positive"


def test_get_self_dist_witnesses(sample_event_log):
    """
    Test the `get_self_dist_witnesses` function to verify it correctly identifies self-distance witnesses.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If the witness structure is incorrect or contains invalid types
    """
    result = get_self_dist_witnesses(sample_event_log)

    # Test return type
    assert isinstance(result, dict), "get_self_dist_witnesses should return a dictionary"

    # Test structure of returned dictionary
    for case_id, case_data in result.items():
        # Case ID should be integer
        assert isinstance(case_id, int), f"Case ID {case_id} should be an integer"
        # Case data should be dictionary
        assert isinstance(case_data, dict), f"Data for case {case_id} should be a dictionary"

        # Test structure of inner dictionary
        for activity, witnesses in case_data.items():
            # Activity should be string
            assert isinstance(activity, str), f"Activity '{activity}' in case {case_id} should be a string"
            # Witnesses should be list
            assert isinstance(witnesses, list), f"Witnesses for activity '{activity}' in case {case_id} should be a list"
            # Each witness sequence should be a list of strings
            for sequence in witnesses:
                assert isinstance(sequence, list), f"Witness sequence for activity '{activity}' in case {case_id} should be a list"
                assert all(isinstance(act, str) for act in sequence), f"All activities in witness sequence for '{activity}' in case {case_id} should be strings"


def test_print_self_dist_witnesses(sample_event_log, capsys):
    """
    Test the `print_self_dist_witnesses` function to verify it correctly outputs self-distance witnesses.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected witness information is not present in stdout
    """
    print_self_dist_witnesses(sample_event_log)
    captured = capsys.readouterr()

    # Check header
    assert "Witnesses of minimum self-distances:" in captured.out, "print_self_dist_witnesses output missing header"

    # Check format of case ID outputs
    assert "Case ID" in captured.out, "print_self_dist_witnesses output missing Case ID reference"

    # Verify output contains dictionary format
    assert "{" in captured.out and "}" in captured.out, "print_self_dist_witnesses output missing dictionary format"

    # Check for expected activity names in output
    expected_activities = {'__start__', 'test_supervisor', 'rg_supervisor',
                           'ag_supervisor', 'DocWriter', 'NoteTaker',
                           'ChartGenerator', 'Search', 'WebScraper'}
    for activity in expected_activities:
        assert activity in captured.out, f"print_self_dist_witnesses output missing activity '{activity}'"

def test_print_analysis(sample_event_log, capsys):
    """
    Test the `print_analysis` function to verify it correctly outputs the complete analysis report.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If any required section is missing from the output
    """
    print_analysis(sample_event_log)
    captured = capsys.readouterr()

    # Verify all sections are present
    required_sections = [
        "START",
        "Start activities:",
        "End activities:",
        "Count of each activity:",
        "All sequences:",
        "ID of last sequence occurrence with probability of occurrence:",
        "Minimal self-distances for every activity:",
        "Witnesses of minimum self-distances:",
        "Count of activity rework:",
        "Mean duration of every activity:",
        "Duration of the case:",
        "END"
    ]

    for section in required_sections:
        assert section in captured.out, f"print_analysis output missing required section: '{section}'"