import sqlite3
import json

conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("SELECT * FROM checkpoints")
rows = cursor.fetchall()

with open('output.log', 'w') as log_file:
    # Start the JSON array
    log_file.write('[\n')

    for i, row in enumerate(rows):
        # Start a new JSON object for each row
        json_object = {
            "thread_ID": row[0],
            "checkpoint": json.loads(row[5]),  # Assuming JSON is stored in the 6th column
            "metadata": json.loads(row[6])  # Assuming JSON is stored in the 7th column
        }

        # Pretty print the JSON object
        log_file.write(json.dumps(json_object, indent=4))

        # Add a comma and newline after each object, except for the last one
        if i < len(rows) - 1:
            log_file.write(',\n')

    # End the JSON array
    log_file.write('\n]')

conn.close()
