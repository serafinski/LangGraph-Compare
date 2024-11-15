from langgraph_log_parser.sql_to_log import *


def test_export_sqlite_to_log(tmp_path):
    """
    Test the `export_sqlite_to_log` function by verifying it correctly exports
    SQLite database data to a JSON log file.

    This test ensures:
    - The function creates a JSON log file from the provided SQLite database.
    - The generated log file matches the expected output.

    :param tmp_path: A pytest fixture providing a temporary directory for test outputs.
    :type tmp_path: pathlib.Path
    :raises AssertionError: If the log file is not created or if the generated output does not match the expected data.
    """
    # Define paths to the test database and expected output log
    test_db_path = "files/tests/test_checkpoints.sqlite"
    expected_output_log_path = "files/tests/test_sql_to_log_output.log"

    # Define a temporary output path to store the generated log file
    output_log_path = tmp_path / "generated_log_output.log"

    # Run the function to export data from the SQLite database to the temporary log file
    export_sqlite_to_log(db_path=test_db_path, output_file=str(output_log_path))

    # Ensure the output file was created
    assert output_log_path.exists(), "The output log file was not created."

    # Load and compare the generated log file to the expected output log
    with open(output_log_path, 'r') as generated_file, open(expected_output_log_path, 'r') as expected_file:
        generated_data = json.load(generated_file)
        expected_data = json.load(expected_file)

        # Assert that the two data structures match
        assert generated_data == expected_data, "The generated log output does not match the expected output."

    print("Test for export_sqlite_to_log passed successfully.")
