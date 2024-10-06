import sqlite3
import json
import msgpack

def convert(obj):
    # Konwersja byte'ów do string'ów
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="ignore")
    # Konwersja słowników do string'ów
    elif isinstance(obj, dict):
        return {key: convert(value) for key, value in obj.items()}
    # Konwersja listy do string'ów
    elif isinstance(obj, list):
        return [convert(element) for element in obj]
    # Konwersja tupli do string'ów
    elif isinstance(obj, tuple):
        return tuple(convert(element) for element in obj)
    else:
        return obj

conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("SELECT * FROM checkpoints")
rows = cursor.fetchall()

with open('files/sql_to_log_output.log', 'w') as log_file:
    # Początek JSON array
    log_file.write('[\n')

    for i, row in enumerate(rows):
        try:
            # Deserlializacjia z użyciem msgpack
            checkpoint = msgpack.loads(row[5])
            # Konwersja byte'ów do string'ów
            checkpoint = convert(checkpoint)
        except Exception as e:
            print(f"Error deserializing checkpoint in row {i}: {e}")
            checkpoint = None

        try:
            metadata = json.loads(row[6])
            # To samo dla metadata (na MacOS z jakiegoś powodu też w postaci byte'ów)
            metadata = convert(metadata)
        except Exception as e:
            print(f"Error deserializing metadata in row {i}: {e}")
            metadata = None

        # Nowy obiekt JSON dla każdego z wierszy
        json_object = {
            "thread_ID": row[0],
            "checkpoint": checkpoint,
            "metadata": metadata
        }

        # Wypisanie do pliku
        try:
            log_file.write(json.dumps(json_object, indent=4))
        except TypeError as e:
            print(f"Error serializing JSON object in row {i}: {e}")

        # Przecinek i new line, oprócz ostatniego
        if i < len(rows) - 1:
            log_file.write(',\n')

    # Koniec JSON array
    log_file.write('\n]')

conn.close()