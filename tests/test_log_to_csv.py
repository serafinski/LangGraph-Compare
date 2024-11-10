from langgraph_log_parser.log_to_csv import *

def test_export_log_to_csv(log_file_path, tmp_path):
    """
    Test the export_log_to_csv function by verifying it correctly converts
    JSON log data to the specified CSV format.
    """
    # Path for the temporary CSV output
    csv_output_path = tmp_path / "csv_output_test.csv"

    # Define the CSV fields to be used in the test
    csv_fields = ['case_id', 'timestamp', 'end_timestamp', 'cost', 'activity', 'org:resource']

    # Run the function with the test JSON log and temporary CSV output
    export_log_to_csv(
        log_filename=log_file_path,
        csv_filename=str(csv_output_path),
        csv_fields=csv_fields
    )

    # Verify if the CSV file was created
    assert csv_output_path.exists(), "CSV output file was not created."

    # Open the CSV file and validate its contents
    with open(csv_output_path, mode="r") as csv_file:
        reader = csv.DictReader(csv_file)

        # Verify the header
        assert reader.fieldnames == csv_fields, "CSV header fields do not match expected fields."

        # Read and validate each row in the CSV
        rows = list(reader)
        for row in rows:
            # Check that required fields are populated
            assert row["case_id"] is not None, "Missing 'case_id' in CSV output."
            assert row["timestamp"] is not None, "Missing 'timestamp' in CSV output."
            assert row["end_timestamp"] is not None, "Missing 'end_timestamp' in CSV output."
            assert row["cost"] is not None, "Missing 'cost' in CSV output."
            assert row["activity"] is not None, "Missing 'activity' in CSV output."
            assert row["org:resource"] is not None, "Missing 'org:resource' in CSV output."


    print("Test for export_log_to_csv passed successfully.")