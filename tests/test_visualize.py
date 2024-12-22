from unittest.mock import MagicMock

from langgraph_log_parser import generate_mermaid, generate_prefix_tree, generate_performance_dfg, generate_visualizations


def test_generate_mermaid(mock_state_graph, tmp_path):
    """
    Test the `generate_mermaid` function to verify that a mermaid image is generated.

    :param mock_state_graph: Mock CompiledStateGraph object from fixture
    :type mock_state_graph: MagicMock
    :param tmp_path: A pytest fixture providing a temporary directory.
    :type tmp_path: pathlib.Path
    :raises AssertionError: If the output file does not exist after the function is called.
    """
    mock_mermaid = MagicMock()
    mock_mermaid.draw_mermaid_png.return_value = b"mock png data"
    mock_state_graph.get_graph.return_value = mock_mermaid

    output_path = tmp_path / "mermaid.png"
    generate_mermaid(mock_state_graph, output_path)
    assert output_path.exists(), f"Expected visualization file {output_path} was not generated"


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
    assert output_path.exists(), f"Expected visualization file {output_path} was not generated"

def test_generate_performance_dfg(sample_event_log, tmp_path):
    """
    Test the `generate_performance_dfg` function to verify that a performance DFG image is generated.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :param tmp_path: A pytest fixture providing a temporary directory.
    :type tmp_path: pathlib.Path
    :raises AssertionError: If the output file does not exist after the function is called.
    """
    # Test performance DFG generation
    output_path = tmp_path / "dfg_performance.png"
    generate_performance_dfg(sample_event_log, output_path)
    assert output_path.exists(), f"Expected visualization file {output_path} was not generated"

def test_generate_visualizations(sample_event_log, mock_state_graph, tmp_path):
    """
    Test the `generate_visualizations` function to verify that all visualization files are generated.

    :param sample_event_log: The sample event log DataFrame provided by the fixture
    :type sample_event_log: pd.DataFrame
    :param mock_state_graph: Mock CompiledStateGraph object from fixture
    :type mock_state_graph: MagicMock
    :param tmp_path: A pytest fixture providing a temporary directory
    :type tmp_path: pathlib.Path
    :raises AssertionError: If any of the expected output files do not exist after the function is called
    """
    # Setup mock for mermaid graph generation
    mock_mermaid = MagicMock()
    mock_mermaid.draw_mermaid_png.return_value = b"mock png data"
    mock_state_graph.get_graph.return_value = mock_mermaid

    # Create output directory path
    output_dir = tmp_path / "visualizations"

    # Generate all visualizations
    generate_visualizations(
        event_log=sample_event_log,
        graph=mock_state_graph,
        output_dir=str(output_dir)
    )

    # Check if output directory exists
    assert output_dir.exists()
    assert output_dir.is_dir()

    # Check if all expected files were generated
    expected_files = [
        'mermaid.png',
        'prefix_tree.png',
        'dfg_performance.png'
    ]

    for file_name in expected_files:
        file_path = output_dir / file_name
        assert file_path.exists(), f"Expected visualization file {file_name} was not generated"