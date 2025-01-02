import os
import json
import glob
import pytest
import shutil
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock
from langgraph.graph.state import CompiledStateGraph

from langgraph_log_parser import load_event_log, SupervisorConfig, SubgraphConfig, GraphConfig


@pytest.fixture
def sample_event_log(project_root: Path):
    """
    Fixture to provide a sample event log DataFrame for testing.

    :return: A DataFrame containing the event log data
    :rtype: pandas.DataFrame
    """
    test_file_path = str(project_root / "tests/files/csv/csv_output.csv")
    return load_event_log(test_file_path)


@pytest.fixture
def log_file_paths(project_root: Path):
    """
    Fixture providing paths to all test JSON log files.

    :return: List of paths to the test JSON files
    :rtype: List[str]
    """
    json_pattern = str(project_root / "tests/files/json/thread_*.json")
    return sorted(glob.glob(json_pattern))


@pytest.fixture
def sample_db_path():
    """
    Fixture providing path to the test SQLite database.

    :return: Path to the test database file
    :rtype: str
    """
    return "tests/files/db/files.sqlite"


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


@pytest.fixture
def setup_cleanup(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Fixture to set up and clean up the test environment.
    """
    # Store original working directory
    original_dir = os.getcwd()

    # Change to temporary directory
    os.chdir(tmp_path)

    # Create experiments directory
    experiments_dir = tmp_path / "experiments"
    if not experiments_dir.exists():
        experiments_dir.mkdir()

    yield tmp_path

    # Clean up: change back to original directory
    os.chdir(original_dir)

    # Clean up: remove test directory
    if experiments_dir.exists():
        shutil.rmtree(experiments_dir)


@pytest.fixture
def project_root():
    """Fixture providing the project root path."""
    return Path(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def reference_metrics():
    """Fixture providing the reference metrics report data."""
    project_root = Path(os.path.dirname(os.path.dirname(__file__)))
    with open(project_root / "tests/files/reports/metrics_report.json", 'r') as f:
        return json.load(f)


@pytest.fixture
def reference_sequences():
    """Fixture providing the reference sequences report data."""
    project_root = Path(os.path.dirname(os.path.dirname(__file__)))
    with open(project_root / "tests/files/reports/sequences_report.json", 'r') as f:
        return json.load(f)


@pytest.fixture
def reference_html():
    """Fixture providing the reference HTML report content."""
    project_root = Path(os.path.dirname(os.path.dirname(__file__)))
    with open(project_root / "tests/files/files.html", 'r') as f:
        return f.read()


@pytest.fixture
def test_infrastructure(setup_cleanup, project_root):
    """Fixture to set up test infrastructure with reference files."""
    # Create test infrastructure directory
    test_dir = setup_cleanup / "experiments/test1"
    reports_dir = test_dir / "reports"
    img_dir = test_dir / "img"
    reports_dir.mkdir(parents=True)
    img_dir.mkdir(parents=True)

    # Copy reference reports
    ref_reports_dir = project_root / "tests/files/reports"
    for report_file in ["metrics_report.json", "sequences_report.json"]:
        shutil.copy2(ref_reports_dir / report_file, reports_dir / report_file)

    # Copy reference images
    ref_img_dir = project_root / "tests/files/img"
    for img_file in ref_img_dir.glob("*.png"):
        shutil.copy2(img_file, img_dir / img_file.name)

    return test_dir


@pytest.fixture
def graph_config():
    test_supervisor = SupervisorConfig(
        name="test_supervisor",
        supervisor_type="graph"
    )

    rg_supervisor = SupervisorConfig(
        name="rg_supervisor",
        supervisor_type="subgraph"
    )

    ag_supervisor = SupervisorConfig(
        name="ag_supervisor",
        supervisor_type="subgraph"
    )

    research_team = SubgraphConfig(
        name="ResearchTeam",
        nodes=["Search", "WebScraper"],
        supervisor=rg_supervisor
    )

    authoring_team = SubgraphConfig(
        name="PaperWritingTeam",
        nodes=["DocWriter", "NoteTaker", "ChartGenerator"],
        supervisor=ag_supervisor
    )

    return GraphConfig(
        supervisors=[test_supervisor],
        subgraphs=[research_team, authoring_team]
    )