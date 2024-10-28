import json
import csv

# Definiowanie input'u i output'u
log_filename = 'files/sql_to_log_output.log'
csv_filename = 'files/csv_output.csv'
csv_fields = ['case_id', 'timestamp', 'end_timestamp', 'cost', 'activity', 'org:resource']

# Czytanie danych z JSON'a z .log
with open(log_filename, 'r') as log_file:
    logs = json.load(log_file)

# Otwarcie .csv z zapisem
with open(csv_filename, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
    writer.writeheader()

    # Przechodzenie po log'u
    for i, log_entry in enumerate(logs):
        case_id = log_entry.get('thread_ID')
        timestamp = log_entry['checkpoint'].get('ts')

        # Domyślna wartość jeśli nie znajdziemy total_tokens
        cost = 0

        metadata = log_entry.get('metadata', {})
        writes = metadata.get('writes', {})

        # Sprawdzenie, czy writes nie jest None i jest słownikiem
        if writes and isinstance(writes, dict):
            # Wyciągnięcie pierwszego klucza jako node'a (np. 'chatbot_node')
            node_name = list(writes.keys())[0]
            node_data = writes.get(node_name, {})

            # Sprawdzenie, czy node_data jest słownikiem
            if isinstance(node_data, dict):
                messages = node_data.get('messages', [])
                for message in messages:
                    # Sprawdzenie, czy message to słownik
                    if isinstance(message, dict) and 'kwargs' in message:
                        kwargs = message.get('kwargs', {})
                        usage_metadata = kwargs.get('usage_metadata', {})
                        # Wyciągnięcie total_tokens z usage_metadata
                        cost = usage_metadata.get('total_tokens', 0)
                        break  # Zatrzymanie po znalezieniu pierwszej wartości
                    elif isinstance(message, list) and len(message) > 1 and isinstance(message[1], dict):
                        # Obsługa przypadku, gdy message jest listą
                        kwargs = message[1].get('kwargs', {})
                        usage_metadata = kwargs.get('usage_metadata', {})
                        # Wyciągnięcie total_tokens z usage_metadata
                        cost = usage_metadata.get('total_tokens', 0)
                        break  # Zatrzymanie po znalezieniu pierwszej wartości

        # Wyciągnięcie activity i org:resource (pierwszy klucz w 'writes')
        if writes:
            # Wyciągnięcie pierwszego klucza
            activity = list(writes.keys())[0]
            org_resource = list(writes.keys())[0]
        else:
            # Jak nie ma activity lub org:resource to 'unknown'
            activity = 'unknown'
            org_resource = 'unknown'

        # Wyciągnięcie end_timestap'a z następnego log entry z tym samym case_id
        end_timestamp = None
        for j in range(i + 1, len(logs)):
            next_log_entry = logs[j]
            # To samo case_id!
            if next_log_entry.get('thread_ID') == case_id:
                if next_log_entry.get('metadata', {}).get('writes'):
                    end_timestamp = next_log_entry['checkpoint'].get('ts')
                    break

        # Zapisywanie wyciągniętych danych do pliku CSV
        writer.writerow({
            'case_id': case_id,
            'timestamp': timestamp,
            # Podmianka na timestamp - jeżeli nie ma wartości - długość 0 (workaround dla ostanich wierszy)
            'end_timestamp': end_timestamp if end_timestamp is not None else timestamp,
            'cost': cost,
            'activity': activity,
            'org:resource': org_resource
        })