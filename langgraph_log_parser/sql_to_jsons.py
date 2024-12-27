import os
import sqlite3
import json
import msgpack
from typing import Dict, Any, Union, Optional
from .experiment import ExperimentPaths

def _convert(obj):
    """
    Convert bytes, dicts, lists, and tuples to strings recursively.

    :param obj: The object to convert (bytes, dict, list, or tuple).
    :type obj: Any
    :return: The converted object with strings instead of bytes.
    :rtype: Any
    """
    # Konwersja byte'ów do string'ów
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="ignore")
    # Konwersja słowników do string'ów
    elif isinstance(obj, dict):
        # Konwersja elementów słownika rekursywnie
        return {key: _convert(value) for key, value in obj.items()}
    # Konwersja listy do string'ów
    elif isinstance(obj, list):
        # Konwersja elementów listy rekursywnie
        return [_convert(element) for element in obj]
    # Konwersja tupli do string'ów
    elif isinstance(obj, tuple):
        # Konwersja elementów tupli rekursywnie
        return tuple(_convert(element) for element in obj)
    else:
        return obj


def export_sqlite_to_jsons(source: Union[ExperimentPaths, str], output_folder: Optional[str] = None) -> None:
    """
    Fetch data from the SQLite database and export it as JSON files.
    Can use either an ExperimentPaths instance or explicit database and output paths.

    :param source: Either an ExperimentPaths instance or a path to the SQLite database
    :type source: Union[ExperimentPaths, str]
    :param output_folder: Path to the output folder for JSON files (required if source is a str)
    :type output_folder: Optional[str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> export_sqlite_to_jsons(exp)
    JSON file created: experiments/my_experiment/json/thread_1.json
    JSON file created: experiments/my_experiment/json/thread_2.json
    JSON file created: experiments/my_experiment/json/thread_3.json

    >>> # Using direct paths:
    >>> export_sqlite_to_jsons("path/to/db.sqlite", "path/to/output")
    JSON file created: path/to/output/thread_1.json
    JSON file created: path/to/output/thread_2.json
    JSON file created: path/to/output/thread_3.json
    """

    # Determine paths based on input type
    if isinstance(source, ExperimentPaths):
        db_path = source.database
        json_dir = source.json_dir
    else:
        if output_folder is None:
            raise ValueError("output_folder must be provided when using a database path directly")
        db_path = source
        json_dir = output_folder

    # Połączenie do bazy danych
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    try:
        # Pobieramy dane z tabeli "checkpoints"
        cursor.execute("SELECT * FROM checkpoints")
        rows = cursor.fetchall()

        # Słownik do przechowywania danych pogrupowanych według thread_ID
        data_by_thread: Dict[int, list] = {}

        for row in rows:
            thread_id = row[0]

            try:
                # Deserializacja z użyciem msgpack
                checkpoint = msgpack.loads(row[5])
                # Konwersja byte'ów do string'ów
                checkpoint = _convert(checkpoint)
            except Exception as e:
                print(f"Error deserializing checkpoint in row with thread_ID {thread_id}: {e}")
                checkpoint = None

            try:
                # Deserializacja metadanych z użyciem JSON
                metadata = json.loads(row[6])
                # To samo dla metadata (na MacOS z jakiegoś powodu też w postaci byte'ów)
                metadata = _convert(metadata)
            except Exception as e:
                print(f"Error deserializing metadata in row with thread_ID {thread_id}: {e}")
                metadata = None

            # Przygotowanie obiektu JSON
            json_object: Dict[str, Any] = {
                "thread_ID": thread_id,
                "checkpoint": checkpoint,
                "metadata": metadata
            }

            # Grupowanie danych według thread_ID
            if thread_id not in data_by_thread:
                data_by_thread[thread_id] = []
            data_by_thread[thread_id].append(json_object)

        # Zapisz dane dla każdego thread_ID w osobnym pliku JSON
        for thread_id, jsons in data_by_thread.items():
            output_path = os.path.join(json_dir, f"thread_{thread_id}.json")
            try:
                with open(output_path, 'w') as json_file:
                    # Zapisz dane jako JSON
                    json.dump(jsons, json_file, indent=4)
                print(f"JSON file created: {output_path}")
            except Exception as e:
                print(f"Error writing JSON file for thread_ID {thread_id}: {e}")

    finally:
        conn.close()