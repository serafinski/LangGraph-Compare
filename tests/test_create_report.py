import json
from langgraph_log_parser.create_report import write_metrics_report, write_sequences_report, generate_reports


def test_write_metrics_report(sample_event_log, reference_metrics, setup_cleanup):
    """Test the write_metrics_report function."""
    # Use the temporary test directory from setup_cleanup
    test_dir = setup_cleanup / "reports"
    test_dir.mkdir(exist_ok=True)

    # Write report to test directory
    write_metrics_report(sample_event_log, test_dir)

    # Check metrics report
    metrics_file = test_dir / "metrics_report.json"
    with open(metrics_file) as f:
        assert json.load(f) == reference_metrics


def test_write_sequences_report(sample_event_log, reference_sequences, setup_cleanup):
    """Test the write_sequences_report function."""
    # Use the temporary test directory from setup_cleanup
    test_dir = setup_cleanup / "reports"
    test_dir.mkdir(exist_ok=True)

    # Write report to test directory
    write_sequences_report(sample_event_log, test_dir)

    # Check sequences report
    sequences_file = test_dir / "sequences_report.json"
    with open(sequences_file) as f:
        assert json.load(f) == reference_sequences


def test_generate_reports(sample_event_log, reference_metrics, reference_sequences, setup_cleanup):
    """Test the generate_reports function."""
    # Use the temporary test directory from setup_cleanup
    test_dir = setup_cleanup / "reports"
    test_dir.mkdir(exist_ok=True)

    # Generate all reports
    generate_reports(sample_event_log, test_dir)

    # Check metrics report
    metrics_file = test_dir / "metrics_report.json"
    with open(metrics_file) as f:
        assert json.load(f) == reference_metrics

    # Check sequences report
    sequences_file = test_dir / "sequences_report.json"
    with open(sequences_file) as f:
        assert json.load(f) == reference_sequences