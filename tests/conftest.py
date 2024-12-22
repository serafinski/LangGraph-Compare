import glob
import pytest
from unittest.mock import MagicMock
from langgraph.graph.state import CompiledStateGraph

from langgraph_log_parser import load_event_log

@pytest.fixture
def sample_event_log():
    """
    Fixture to provide a sample event log DataFrame for testing.

    :return: A DataFrame containing the event log data
    :rtype: pandas.DataFrame
    """
    test_file_path = "tests/files/csv/csv_output.csv"
    return load_event_log(test_file_path)

@pytest.fixture
def log_file_paths():
    """
    Fixture providing paths to all test JSON log files.

    :return: List of paths to the test JSON files
    :rtype: List[str]
    """
    json_pattern = "tests/files/jsons/thread_*.json"
    return sorted(glob.glob(json_pattern))


@pytest.fixture
def sample_db_path():
    """
    Fixture providing path to the test SQLite database.

    :return: Path to the test database file
    :rtype: str
    """
    return "tests/files/db/hierarchical.sqlite"

@pytest.fixture
def mock_state_graph():
    """
    Create a mock StateGraph object with a `stream` method simulating a graph's output.

    The `stream` method returns a list of dictionaries, each representing an event in the graph.

    :return: A mock StateGraph object with a pre-configured `stream` method.
    :rtype: MagicMock
    """
    graph = MagicMock(spec=CompiledStateGraph)

    # Configure the mock stream to yield a list of dictionaries representing events
    graph.stream = MagicMock(return_value=[{"event_1": "output_1"}, {"event_2": "output_2"}, {"event_3": "__end__"}])

    return graph
