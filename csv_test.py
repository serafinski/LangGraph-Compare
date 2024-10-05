import json
import csv

# Define the input and output file names
log_filename = 'output.log'
csv_filename = 'process_mining_output.csv'
csv_fields = ['case_id', 'timestamp', 'cost', 'activity', 'org:resource']

# Read the log data from the JSON file
with open(log_filename, 'r') as log_file:
    logs = json.load(log_file)

# Open the CSV file for writing
with open(csv_filename, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
    writer.writeheader()

    # Iterate over each log entry
    for log_entry in logs:
        case_id = log_entry.get('thread_ID')
        timestamp = log_entry['checkpoint'].get('ts')
        cost = 0

        metadata = log_entry.get('metadata', {})
        writes = metadata.get('writes', {})

        # Extract the activity and org:resource (which should be the first key in 'writes')
        if writes:
            activity = list(writes.keys())[0]  # Get the first key in writes
            org_resource = list(writes.keys())[0]
        else:
            activity = 'unknown'
            org_resource = 'unknown'

        # Write the extracted data into the CSV file
        writer.writerow({
            'case_id': case_id,
            'timestamp': timestamp,
            'cost': cost,
            'activity': activity,
            'org:resource': org_resource
        })

print(f"CSV file '{csv_filename}' has been created.")
