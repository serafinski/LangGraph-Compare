import os
import pandas as pd
import shutil
from langgraph_log_parser.jsons_to_csv import export_jsons_to_csv, SupervisorConfig, SubgraphConfig, GraphConfig

def compare_csv_files(file1: str, file2: str) -> bool:
    """
    Compare two CSV files for exact equality, including row order.

    :param file1: Path to first CSV file
    :param file2: Path to second CSV file
    :return: True if files are exactly equal, False otherwise
    """
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Direct comparison without sorting, maintaining exact row order
    return df1.equals(df2)

def test_export_jsons_to_csv(log_file_paths, sample_event_log, tmp_path):
    """
    Test that export_jsons_to_csv produces the expected CSV output.

    :param log_file_paths: Fixture providing paths to test JSON files
    :param sample_event_log: Fixture providing expected CSV content
    :param tmp_path: pytest fixture providing temporary directory
    """
    # Setup paths
    json_dir = str(tmp_path / "json_input")
    # Directory for the CSV output
    output_dir = str(tmp_path / "csv_output")
    os.makedirs(json_dir)
    # Create output directory
    os.makedirs(output_dir)

    # Copy test JSON files to temporary directory
    for src_path in log_file_paths:
        dst_path = os.path.join(json_dir, os.path.basename(src_path))
        shutil.copy2(src_path, dst_path)

    # Create graph configuration
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

    graph_config = GraphConfig(
        supervisors=[test_supervisor],
        subgraphs=[research_team, authoring_team]
    )

    # Execute the function
    export_jsons_to_csv(
        source=json_dir,
        graph_config=graph_config,
        output_dir=output_dir
    )

    # The output CSV will now be in the output directory with the name 'csv_output.csv'
    generated_csv = os.path.join(output_dir, 'csv_output.csv')

    # Assert that the output file exists
    assert os.path.exists(generated_csv), "Output CSV file was not created"

    # Get the path to the expected CSV
    expected_csv = "tests/files/csv/csv_output.csv"

    # Compare with expected CSV
    assert compare_csv_files(generated_csv, expected_csv), "Generated CSV does not match expected output"