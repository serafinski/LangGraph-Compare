import sqlite3
import json
import msgpack

def convert_bytes(obj):
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="ignore")  # Convert bytes to string
    elif isinstance(obj, dict):
        return {key: convert_bytes(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_bytes(element) for element in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_bytes(element) for element in obj)
    else:
        return obj

conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("SELECT * FROM checkpoints")
rows = cursor.fetchall()

with open('output.log', 'w') as log_file:
    # Start the JSON array
    log_file.write('[\n')

    for i, row in enumerate(rows):
        try:
            # Deserialize with MessagePack
            checkpoint = msgpack.loads(row[5])
            checkpoint = convert_bytes(checkpoint)  # Convert bytes to strings recursively
        except Exception as e:
            print(f"Error deserializing checkpoint in row {i}: {e}")
            checkpoint = None

        try:
            metadata = json.loads(row[6])
            metadata = convert_bytes(metadata)  # Ensure metadata has no bytes as well
        except Exception as e:
            print(f"Error deserializing metadata in row {i}: {e}")
            metadata = None

        # Start a new JSON object for each row
        json_object = {
            "thread_ID": row[0],
            "checkpoint": checkpoint,
            "metadata": metadata
        }

        # Pretty print the JSON object
        try:
            log_file.write(json.dumps(json_object, indent=4))
        except TypeError as e:
            print(f"Error serializing JSON object in row {i}: {e}")

        # Add a comma and newline after each object, except for the last one
        if i < len(rows) - 1:
            log_file.write(',\n')

    # End the JSON array
    log_file.write('\n]')

conn.close()