from langgraph_compare.analyze_case_id import (
    get_case_sequence, print_case_sequence,
    get_case_sequence_prob, print_case_sequence_prob,
    get_case_min_self_dists, print_case_min_self_dists,
    get_case_act_reworks, print_case_act_reworks,
    get_case_duration, print_case_duration,
    get_case_start, print_case_start,
    get_case_end, print_case_end,
    get_case_act_counts, print_case_act_counts,
    get_case_sum_act_times, print_case_sum_act_times,
    get_case_self_dist_witnesses, print_case_self_dist_witnesses,
    print_case_analysis
)


def test_get_case_sequence(sample_event_log):
    """
    Test the `get_case_sequence` function to verify it correctly retrieves activity sequences for specific cases.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If sequence is not properly formatted or contains unexpected activities
    """
    result = get_case_sequence(sample_event_log, 1)
    assert isinstance(result, list), "get_case_sequence should return a list"
    assert len(result) > 0, "get_case_sequence result should not be empty"
    assert all(isinstance(act, str) for act in result), "All activities in sequence should be strings"
    assert result[0] == '__start__', "First activity should be '__start__'"
    assert result[-1] == 'test_supervisor', "Last activity should be 'test_supervisor'"


def test_print_case_sequence(sample_event_log, capsys):
    """
    Test the `print_case_sequence` function to verify it correctly outputs case sequences.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If the expected output format is not correct
    """
    print_case_sequence(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "Activity sequence for case ID 1:" in captured.out
    assert "__start__" in captured.out
    assert "test_supervisor" in captured.out


def test_get_case_sequence_prob(sample_event_log):
    """
    Test the `get_case_sequence_prob` function to verify it correctly calculates sequence probabilities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If probability is not a valid float or sequence is malformed
    """
    sequence, prob = get_case_sequence_prob(sample_event_log, 1)
    assert isinstance(sequence, list), "Sequence should be a list"
    assert isinstance(prob, float), "Probability should be a float"
    assert 0 <= prob <= 1, "Probability should be between 0 and 1"
    assert len(sequence) > 0, "Sequence should not be empty"


def test_print_case_sequence_prob(sample_event_log, capsys):
    """
    Test the `print_case_sequence_prob` function to verify it correctly outputs sequence probabilities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If expected probability information is not in output
    """
    print_case_sequence_prob(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "Activity sequence for case ID 1:" in captured.out
    assert "Probability:" in captured.out


def test_get_case_min_self_dists(sample_event_log):
    """
    Test the `get_case_min_self_dists` function to verify it correctly calculates case-specific self-distances.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If distances are negative or missing expected activities
    """
    result = get_case_min_self_dists(sample_event_log, 1)
    assert isinstance(result, dict), "get_case_min_self_dists should return a dictionary"

    # Check essential activities are present
    expected_activities = {'__start__', 'test_supervisor', 'rg_supervisor', 'ag_supervisor'}
    assert expected_activities.issubset(set(result.keys())), "Missing expected activities"

    # Verify all distances are non-negative integers
    assert all(isinstance(dist, int) and dist >= 0 for dist in result.values()), "All distances should be non-negative integers"


def test_print_case_min_self_dists(sample_event_log, capsys):
    """
    Test the `print_case_min_self_dists` function to verify it correctly outputs self-distances.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If expected distance information is not in output
    """
    print_case_min_self_dists(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "Minimum self distances for case ID 1:" in captured.out
    assert "__start__" in captured.out
    assert "test_supervisor" in captured.out


def test_get_case_act_reworks(sample_event_log):
    """
    Test the `get_case_act_reworks` function to verify it correctly identifies case-specific rework.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If rework counts are negative or structure is incorrect
    """
    result = get_case_act_reworks(sample_event_log, 1)
    assert isinstance(result, dict), "get_case_act_reworks should return a dictionary"

    # Verify rework counts are positive integers
    assert all(isinstance(count, int) and count > 1 for count in result.values()), "All rework counts should be integers greater than 1"


def test_print_case_act_reworks(sample_event_log, capsys):
    """
    Test the `print_case_act_reworks` function to verify it correctly outputs rework counts.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If expected rework information is not in output
    """
    print_case_act_reworks(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "Rework counts for case ID 1:" in captured.out


def test_get_case_duration(sample_event_log):
    """
    Test the `get_case_duration` function to verify it correctly calculates case durations.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If duration is not a positive float
    """
    result = get_case_duration(sample_event_log, 1)
    assert isinstance(result, float), "get_case_duration should return a float"
    assert result > 0, "Duration should be positive"


def test_print_case_duration(sample_event_log, capsys):
    """
    Test the `print_case_duration` function to verify it correctly outputs case duration.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If expected duration information is not in output
    """
    print_case_duration(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "Duration for case ID 1:" in captured.out
    assert "s" in captured.out


def test_get_case_start(sample_event_log):
    """
    Test the `get_case_start` function to verify it correctly identifies case start activities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If start activity is not '__start__'
    """
    result = get_case_start(sample_event_log, 1)
    assert isinstance(result, str), "get_case_start should return a string"
    assert result == '__start__', "Start activity should be '__start__'"


def test_print_case_start(sample_event_log, capsys):
    """
    Test the `print_case_start` function to verify it correctly outputs start activities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If expected start activity information is not in output
    """
    print_case_start(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "Start activity for case ID 1:" in captured.out
    assert "__start__" in captured.out


def test_get_case_end(sample_event_log):
    """
    Test the `get_case_end` function to verify it correctly identifies case end activities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If end activity is not 'test_supervisor'
    """
    result = get_case_end(sample_event_log, 1)
    assert isinstance(result, str), "get_case_end should return a string"
    assert result == 'test_supervisor', "End activity should be 'test_supervisor'"

def test_print_case_end(sample_event_log, capsys):
    """
    Test the `print_case_end` function to verify it correctly outputs end activities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If expected end activity information is not in output
    """
    print_case_end(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "End activity for case ID 1:" in captured.out
    assert "test_supervisor" in captured.out


def test_get_case_act_counts(sample_event_log):
    """
    Test the `get_case_act_counts` function to verify it correctly counts case activities.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If counts are negative or missing expected activities
    """
    result = get_case_act_counts(sample_event_log, 1)
    assert isinstance(result, dict), "get_case_act_counts should return a dictionary"

    # Verify counts are positive integers
    assert all(isinstance(count, int) and count > 0 for count in result.values()), "All counts should be positive integers"


def test_print_case_act_counts(sample_event_log, capsys):
    """
    Test the `print_case_act_counts` function to verify it correctly outputs activity counts.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If expected count information is not in output
    """
    print_case_act_counts(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "Count of each activity for case ID 1:" in captured.out
    assert "__start__" in captured.out


def test_get_case_sum_act_times(sample_event_log):
    """
    Test the `get_case_sum_act_times` function to verify it correctly calculates activity times.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If times are negative or missing expected activities
    """
    result = get_case_sum_act_times(sample_event_log, 1)
    assert isinstance(result, dict), "get_case_sum_act_times should return a dictionary"

    # Verify times are positive floats
    assert all(isinstance(time, float) and time >= 0 for time in result.values()), "All times should be non-negative floats"


def test_print_case_sum_act_times(sample_event_log, capsys):
    """
    Test the `print_case_sum_act_times` function to verify it correctly outputs activity times.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If expected time information is not in output
    """
    print_case_sum_act_times(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "Sum service time of each activity for case ID 1" in captured.out


def test_get_case_self_dist_witnesses(sample_event_log):
    """
    Test the `get_case_self_dist_witnesses` function to verify it correctly identifies witnesses.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :raises AssertionError: If witness structure is incorrect or contains invalid types
    """
    result = get_case_self_dist_witnesses(sample_event_log, 1)
    assert isinstance(result, dict), "get_case_self_dist_witnesses should return a dictionary"

    # Check structure of witness lists
    for activity, witnesses in result.items():
        assert isinstance(activity, str), "Activity key should be string"
        assert isinstance(witnesses, list), "Witnesses should be a list"
        for witness in witnesses:
            assert isinstance(witness, list), "Each witness should be a list"
            assert all(isinstance(act, str) for act in witness), "All activities in witness should be strings"


def test_print_case_self_dist_witnesses(sample_event_log, capsys):
    """
    Test the `print_case_self_dist_witnesses` function to verify it correctly outputs witnesses.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If expected witness information is not in output
    """
    print_case_self_dist_witnesses(sample_event_log, 1)
    captured = capsys.readouterr()
    assert "Minimum self distance witnesses for case ID 1:" in captured.out

    # Check for key activities in output
    expected_activities = {'__start__', 'test_supervisor', 'rg_supervisor', 'ag_supervisor'}
    for activity in expected_activities:
        assert activity in captured.out, f"Output missing expected activity {activity}"


def test_print_case_analysis(sample_event_log, capsys):
    """
    Test the `print_case_analysis` function to verify it correctly outputs the complete case analysis.

    :param sample_event_log: Sample event log data for testing
    :type sample_event_log: pandas.DataFrame
    :param capsys: Pytest fixture to capture stdout and stderr
    :type capsys: pytest.CaptureFixture
    :raises AssertionError: If any required section is missing from the output
    """
    print_case_analysis(sample_event_log, 1)
    captured = capsys.readouterr()

    # Verify all sections are present
    required_sections = [
        "START",
        "Start activity for case ID",
        "End activity for case ID",
        "Count of each activity for case ID",
        "Activity sequence for case ID",
        "Minimum self distances for case ID",
        "Minimum self distance witnesses for case ID",
        "Rework counts for case ID",
        "Sum service time of each activity for case ID",
        "Duration for case ID",
        "END"
    ]

    for section in required_sections:
        assert section in captured.out, f"print_case_analysis output missing required section: '{section}'"

    # Test for specific case data
    assert "case ID 1" in captured.out
    assert "__start__" in captured.out
    assert "test_supervisor" in captured.out