import json
import csv

# Definiowanie input'u i output'u
log_filename = 'files/sql_to_log_output.log'
csv_filename = 'files/csv_output_skip.csv'
csv_fields = ['case_id', 'timestamp', 'cost', 'activity', 'org:resource']

# Czytanie danych z JSON'a z .log
with open(log_filename, 'r') as log_file:
    logs = json.load(log_file)

# Otwarcie .csv z zapisem
with open(csv_filename, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
    writer.writeheader()

    # Przechodzenie po log'u
    for log_entry in logs:
        case_id = log_entry.get('thread_ID')
        timestamp = log_entry['checkpoint'].get('ts')
        cost = 0

        metadata = log_entry.get('metadata', {})
        writes = metadata.get('writes', {})

        # Wyciągnięcie activity i org:resource (pierwszy klucz w 'writes')
        if writes:
            # Wyciągnięcie pierwszego klucza
            activity = list(writes.keys())[0]
            org_resource = list(writes.keys())[0]
        else:
            # Skip wiersza jak nie ma activity lub org:resource
            continue

        # Zapisywanie wyciągniętych danych do pliku CSV
        writer.writerow({
            'case_id': case_id,
            'timestamp': timestamp,
            'cost': cost,
            'activity': activity,
            'org:resource': org_resource
        })