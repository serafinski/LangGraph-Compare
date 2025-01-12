from pathlib import Path
import filecmp
import json
import glob
from unittest.mock import Mock, MagicMock
from typing import List, TypedDict, Annotated
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage, BaseMessage
import operator

from langgraph_compare.artifacts import prepare_data, generate_artifacts


def test_prepare_data_with_paths(
        setup_cleanup: Path,
        sample_db_path: str,
        log_file_paths: List[str],
        graph_config,
        # Add project_root fixture
        project_root: Path
):
    """Test prepare_data using direct paths and verify output matches reference files"""
    # Set up output paths in temporary directory
    output_folder = setup_cleanup / "json_output"
    # Ensure directory exists
    output_folder.mkdir(parents=True, exist_ok=True)

    # Create directory for CSV output
    csv_output_dir = setup_cleanup / "csv_output"
    csv_output_dir.mkdir(parents=True, exist_ok=True)

    # Get absolute path to the database
    db_path = project_root / sample_db_path

    # Run prepare_data with updated parameters
    prepare_data(
        # Convert Path to string
        str(db_path),
        graph_config,
        output_folder=str(output_folder),
        output_csv_dir=str(csv_output_dir)
    )

    # Compare generated JSON files with reference files
    generated_jsons = sorted(glob.glob(str(output_folder / "thread_*.json")))
    assert len(generated_jsons) == len(log_file_paths), "Number of generated JSON files doesn't match reference"

    for gen_path, ref_path in zip(generated_jsons, log_file_paths):
        with open(gen_path) as gen_file, open(ref_path) as ref_file:
            gen_json = json.load(gen_file)
            ref_json = json.load(ref_file)
            assert gen_json == ref_json, f"Generated JSON {gen_path} doesn't match reference {ref_path}"

    # Compare generated CSV with reference
    generated_csv = csv_output_dir / "csv_output.csv"
    ref_csv_path = project_root / "tests/files/csv/csv_output.csv"
    assert filecmp.cmp(generated_csv, ref_csv_path, shallow=False), "Generated CSV doesn't match reference"


class State(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next: str


def test_generate_artifacts_with_paths(
        setup_cleanup: Path,
        sample_event_log,
        project_root: Path,
        reference_metrics,
        reference_sequences
):
    """Test generate_artifacts using direct paths"""
    # Set up output directory
    output_dir = setup_cleanup / "analysis_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create mock CompiledStateGraph with similar structure to super_graph
    mock_graph = Mock(spec=CompiledStateGraph)

    # Mock internal graph representation
    mock_internal_graph = MagicMock()
    mock_internal_graph.draw_mermaid_png.return_value = b'mock_png_data'
    mock_graph.get_graph.return_value = mock_internal_graph

    # Mock the stream method to return similar data structure to the actual graph
    mock_graph.state_dict = {
        "ResearchTeam": {"messages": [], "next": ""},
        "PaperWritingTeam": {"messages": [], "next": ""},
        "test_supervisor": {"messages": [], "next": ""}
    }

    mock_graph.stream = Mock(return_value=[
        {
            "messages": [HumanMessage(content="Starting research...")],
            "next": "ResearchTeam"
        },
        {
            "messages": [HumanMessage(content="Research complete")],
            "next": "PaperWritingTeam"
        },
        {
            "messages": [HumanMessage(content="Paper written")],
            "next": "FINISH"
        }
    ])

    # Run generate_artifacts
    generate_artifacts(sample_event_log, mock_graph, str(output_dir))

    # Verify reports were generated correctly
    metrics_path = output_dir / "metrics_report.json"
    sequences_path = output_dir / "sequences_report.json"

    assert metrics_path.exists(), "Metrics report file not created"
    assert sequences_path.exists(), "Sequences report file not created"

    # Compare with reference reports
    with open(metrics_path) as f:
        generated_metrics = json.load(f)
    with open(sequences_path) as f:
        generated_sequences = json.load(f)

    assert generated_metrics == reference_metrics, "Generated metrics don't match reference"
    assert generated_sequences == reference_sequences, "Generated sequences don't match reference"

    # Verify visualizations were generated
    assert (output_dir / "mermaid.png").exists(), "Mermaid diagram not created"
    assert (output_dir / "prefix_tree.png").exists(), "Prefix tree not created"
    assert (output_dir / "dfg_performance.png").exists(), "Performance DFG not created"