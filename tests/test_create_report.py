import json
import os
import shutil
from pathlib import Path
from langgraph_log_parser.create_report import write_metrics_report, write_sequences_report, generate_reports


def load_json_file(file_path: str | Path) -> dict:
    """Helper function to load and parse JSON file."""
    file_path = Path(file_path)
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find file at {file_path.absolute()}")


def test_write_metrics_report(sample_event_log, reference_metrics):
    """Test the write_metrics_report function."""
    test_output = "test_metrics_report.json"
    write_metrics_report(sample_event_log, test_output)

    with open(test_output) as f:
        assert json.load(f) == reference_metrics

    # Cleanup
    os.remove(test_output)

def test_write_sequences_report(sample_event_log, reference_sequences):
    """Test the write_metrics_report function."""
    test_output = "test_sequences_report.json"
    write_sequences_report(sample_event_log, test_output)

    with open(test_output) as f:
        assert json.load(f) == reference_sequences

    # Cleanup
    os.remove(test_output)


def test_generate_reports(sample_event_log, reference_metrics, reference_sequences):
    """Test the generate_reports function."""
    test_output_dir = "test_reports"
    os.makedirs(test_output_dir, exist_ok=True)

    # Generate both reports
    generate_reports(sample_event_log, test_output_dir)

    # Check metrics report
    metrics_file = os.path.join(test_output_dir, "metrics_report.json")
    with open(metrics_file) as f:
        assert json.load(f) == reference_metrics

    # Check sequences report
    sequences_file = os.path.join(test_output_dir, "sequences_report.json")
    with open(sequences_file) as f:
        assert json.load(f) == reference_sequences

    # Cleanup
    shutil.rmtree(test_output_dir)