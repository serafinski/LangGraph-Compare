import json
from langgraph_compare.sql_to_jsons import export_sqlite_to_jsons


def test_export_sqlite_to_jsons(sample_db_path, log_file_paths, tmp_path):
    """
    Test the export_sqlite_to_jsons function.

    This test:
    1. Creates a temporary output directory
    2. Runs the export function
    3. Verifies that all expected files are created
    4. Compares the content of created files with reference files

    :param sample_db_path: Path to the test SQLite database
    :param log_file_paths: List of paths to reference JSON files
    :param tmp_path: Pytest fixture providing temporary directory path
    """
    # Create output directory in temporary path
    output_dir = tmp_path / "json_output"
    output_dir.mkdir()

    # Run the export function
    export_sqlite_to_jsons(sample_db_path, str(output_dir))

    # Get list of created files
    created_files = sorted(list(output_dir.glob("thread_*.json")))

    # Check if number of files matches
    assert len(created_files) == len(log_file_paths), \
        f"Expected {len(log_file_paths)} files, but got {len(created_files)}"

    # Compare content of each file
    for ref_path, created_path in zip(sorted(log_file_paths), created_files):
        # Load and parse both files
        with open(ref_path, 'r') as f:
            expected_content = json.load(f)
        with open(created_path, 'r') as f:
            actual_content = json.load(f)

        # Compare each record
        assert len(actual_content) == len(expected_content), \
            f"Number of records mismatch in {created_path}"

        for actual_record, expected_record in zip(actual_content, expected_content):
            # Compare each key separately for better error messages
            for key in ['thread_ID', 'checkpoint', 'metadata']:
                assert actual_record[key] == expected_record[key], \
                    f"Mismatch in {key} for {created_path}"