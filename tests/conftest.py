import pytest
import pandas as pd
import pm4py
from unittest.mock import MagicMock
from langgraph.graph import StateGraph

@pytest.fixture
def sample_event_log():
    """
    Fixture to provide a sample event log DataFrame for testing.

    This sample event log mimics a process mining dataset with multiple cases and events.
    It includes timestamps, costs, activities, and resources typical for process analysis.

    Returns:
        pd.DataFrame: A formatted DataFrame for pm4py analysis.
    """

    data = {
        'case_id': [1, 1, 6, 6, 6, 6, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        'timestamp': [
            "2024-11-09T22:11:49.365358+00:00", "2024-11-09T22:11:51.557145+00:00",
            "2024-11-09T22:12:19.517933+00:00", "2024-11-09T22:12:20.105412+00:00",
            "2024-11-09T22:12:23.095337+00:00", "2024-11-09T22:12:25.810723+00:00",
            "2024-11-09T22:25:36.084503+00:00", "2024-11-09T22:25:37.697116+00:00",
            "2024-11-09T22:25:40.578805+00:00", "2024-11-09T22:25:47.985329+00:00",
            "2024-11-09T22:25:47.988328+00:00", "2024-11-09T22:25:56.348276+00:00",
            "2024-11-09T22:26:01.204296+00:00", "2024-11-09T22:26:01.358526+00:00",
            "2024-11-09T22:26:02.985773+00:00"
        ],
        'end_timestamp': [
            "2024-11-09T22:11:51.557145+00:00", "2024-11-10T17:12:40.593330+00:00",
            "2024-11-09T22:12:20.105412+00:00", "2024-11-09T22:12:23.095337+00:00",
            "2024-11-09T22:12:25.810723+00:00", "2024-11-09T22:12:25.810723+00:00",
            "2024-11-09T22:25:37.697116+00:00", "2024-11-09T22:25:40.578805+00:00",
            "2024-11-09T22:25:47.985329+00:00", "2024-11-09T22:25:47.988328+00:00",
            "2024-11-09T22:25:56.348276+00:00", "2024-11-09T22:26:01.204296+00:00",
            "2024-11-09T22:26:01.358526+00:00", "2024-11-09T22:26:02.985773+00:00",
            "2024-11-09T22:26:02.985773+00:00"
        ],
        'cost': [0, 29, 0, 108, 0, 1243, 0, 240, 0, 2869, 0, 3130, 3297, 0, 3500],
        'activity': [
            "__start__", "chatbot_node", "__start__", "chatbot_node", "tools", "chatbot_node",
            "__start__", "Researcher", "call_tool", "Researcher", "call_tool" , "Researcher",
            "chart_generator", "call_tool", "chart_generator"
        ],
        'org:resource': [
            "__start__", "chatbot_node", "__start__", "chatbot_node", "tools", "chatbot_node",
            "__start__", "Researcher", "call_tool", "Researcher", "call_tool" , "Researcher",
            "chart_generator", "call_tool", "chart_generator"
        ]
    }

    # Creating the DataFrame and ensuring timestamps are datetime objects
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['end_timestamp'] = pd.to_datetime(df['end_timestamp'])

    # Formatting DataFrame for pm4py compatibility
    formatted_df = pm4py.format_dataframe(df, case_id='case_id', activity_key='activity', timestamp_key='timestamp')

    return formatted_df

@pytest.fixture
def log_file_path():
    """Fixture providing path to the test JSON log file."""
    return "files/tests/test_sql_to_log_output.log"

@pytest.fixture
def mock_state_graph():
    """
    Create a mock StateGraph object with a stream method that simulates a graph's output.
    """
    graph = MagicMock(spec=StateGraph)

    # Configure the mock stream to yield a list of dictionaries representing events
    graph.stream = MagicMock(return_value=[{"event_1": "output_1"}, {"event_2": "output_2"}, {"event_3": "__end__"}])

    return graph
