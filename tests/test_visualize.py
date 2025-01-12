from unittest.mock import MagicMock
import os

from langgraph_compare import generate_mermaid, generate_prefix_tree, generate_performance_dfg, generate_visualizations

def test_generate_mermaid(mock_state_graph, setup_cleanup):
    """
    Test the `generate_mermaid` function to verify that a mermaid image is generated.

    :param mock_state_graph: Mock CompiledStateGraph object from fixture
    :type mock_state_graph: MagicMock
    :raises AssertionError: If the output file does not exist after the function is called.
    """
    mock_mermaid = MagicMock()
    mock_mermaid.draw_mermaid_png.return_value = b"mock png data"
    mock_state_graph.get_graph.return_value = mock_mermaid

    # Create output directory using the setup_cleanup fixture
    output_dir = setup_cleanup / "mermaid"
    os.makedirs(output_dir, exist_ok=True)

    generate_mermaid(mock_state_graph, str(output_dir))

    output_path = output_dir / "mermaid.png"
    assert output_path.exists(), f"Expected visualization file {output_path} was not generated"


def test_generate_prefix_tree(sample_event_log, setup_cleanup):
    """
    Test the `generate_prefix_tree` function to verify that a prefix tree image is generated.

    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :raises AssertionError: If the output file does not exist after the function is called.
    """
    # Create output directory using the setup_cleanup fixture
    output_dir = setup_cleanup / "tree"
    os.makedirs(output_dir, exist_ok=True)

    generate_prefix_tree(sample_event_log, str(output_dir))

    output_path = output_dir / "prefix_tree.png"
    assert output_path.exists(), f"Expected visualization file {output_path} was not generated"


def test_generate_performance_dfg(sample_event_log, setup_cleanup):
    """
    Test the `generate_performance_dfg` function to verify that a performance DFG image is generated.
    :param sample_event_log: The sample event log DataFrame provided by the fixture.
    :type sample_event_log: pd.DataFrame
    :raises AssertionError: If the output file does not exist after the function is called.
    """
    # Create output directory using the setup_cleanup fixture
    output_dir = setup_cleanup / "dfg"
    os.makedirs(output_dir, exist_ok=True)

    generate_performance_dfg(sample_event_log, str(output_dir))

    output_path = output_dir / "dfg_performance.png"
    assert output_path.exists(), f"Expected visualization file {output_path} was not generated"


def test_generate_visualizations(sample_event_log, mock_state_graph, setup_cleanup):
    """
    Test the `generate_visualizations` function to verify that all visualization files are generated.

    :param sample_event_log: The sample event log DataFrame provided by the fixture
    :type sample_event_log: pd.DataFrame
    :param mock_state_graph: Mock CompiledStateGraph object from fixture
    :type mock_state_graph: MagicMock
    :raises AssertionError: If any of the expected output files do not exist after the function is called
    """
    # Setup mock for mermaid graph generation
    mock_mermaid = MagicMock()
    mock_mermaid.draw_mermaid_png.return_value = b"mock png data"
    mock_state_graph.get_graph.return_value = mock_mermaid

    # Create output directory using the setup_cleanup fixture
    output_dir = setup_cleanup / "visualizations"
    os.makedirs(output_dir, exist_ok=True)

    # Generate all visualizations
    generate_visualizations(
        event_log=sample_event_log,
        graph=mock_state_graph,
        output_dir=str(output_dir)
    )

    # Check if all expected files were generated
    expected_files = [
        'mermaid.png',
        'prefix_tree.png',
        'dfg_performance.png'
    ]

    for file_name in expected_files:
        file_path = output_dir / file_name
        assert file_path.exists(), f"Expected visualization file {file_name} was not generated"