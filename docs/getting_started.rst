:orphan:

.. _getting_started:

Getting Started
===============

.. contents:: Table of Contents


Preface
-------
As an example we are going to use a `Building a Basic Chatbot <https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot>`_ from LangGraph documentation.

Prerequisites
-------------
This package leverages `SqliteSaver <https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.sqlite.SqliteSaver>`_ from LangGraph which allows to save checkpoints in a SQLite database.

To initiate SQLite correctly be sure to do the following:

.. code-block:: python

    # Needed imports
    import sqlite3
    from langgraph.checkpoint.sqlite import SqliteSaver

    # Name for your SQLite database
    # The "test/db" directory will make sense in a sec. (see "Creating folder structure" below)
    database = "test/db/test.sqlite"

    # Initiate connection
    conn = sqlite3.connect(database, check_same_thread=False)
    memory = SqliteSaver(conn)

    # Rest of the code...

    # Remember to compile your graph with SQLite as checkpointer memory
    graph = graph_builder.compile(checkpointer=memory)

Creating folder structure
-------------------------
You can create a folder structure for storing your working data.

To create a folder structure, you can use the function :func:`langgraph_log_parser.create_structure.create_folder_structure`.

This can be done like this:

.. code-block:: python

    from langgraph_log_parser.create_structure import create_folder_structure

    create_folder_structure("test")


Function should create a folder structure containing folders :code:`db`, :code:`img` and :code:`json`:

.. code-block:: text

    test/
    ├── db/
    ├── img/
    └── json/

For more details, refer to the documentation of the :mod:`langgraph_log_parser.create_structure` module.

Running graph multiple times
----------------------------
Since the aim of this package is to monitor multiple runs of the multi-agents system I've created a :func:`langgraph_log_parser.graph_runner.run_graph_iterations` that allows to run selected graph multiple times.

This function will create a thread for every single run of the graph - starting from selected :code:`starting_thread_id`.

**Example:**

.. code-block:: python

    from langgraph_log_parser.graph_runner import run_graph_iterations

    # Graph with SQLite checkpointer memory
    graph = graph_builder.compile(checkpointer=memory)

    # This takes graph and runs it 5 times - creating 1 thread for every single run, starting from thread_id=1
    run_graph_iterations(graph, 1,5, {"messages": [("user", "Tell me a joke")]})

For more details, refer to the documentation of the :mod:`langgraph_log_parser.graph_runner` module.

Exporting SQLite to JSON's
--------------------------
After running graph multiple times we need to retrieve the data from the SQLite database.

For this I've created a function :func:`langgraph_log_parser.sql_to_jsons.export_sqlite_to_jsons` that retrieves data from the database and deserializes it from :code:`msgpack`.

Post deserialization - function saves every single thread to a separate :code:`json` file.

**Example:**

.. code-block:: python

    from langgraph_log_parser.sql_to_jsons import export_sqlite_to_jsons

    # Database from previous step
    database = "test/db/test.sqlite"

    # Saving json's to previously auto generated directory
    output = "test/json"

    export_sqlite_to_jsons(database, output)


**Folder structure should like this now:**

.. code-block:: text

    test/
    ├── db/
    │   └── test.sqlite
    ├── img/
    └── json/
        └── thread_1.json
        └── thread_2.json
        └── thread_3.json
        └── thread_4.json
        └── thread_5.json

For more details, refer to the documentation of the :mod:`langgraph_log_parser.sql_to_jsons` module.

.. _exporting_jsons_to_csv:

Exporting JSON's to CSV
-----------------------
We retrieved the data from the database. Now it's time to create a :code:`.csv` file that can be loaded as an event log.

For this I've created :func:`langgraph_log_parser.jsons_to_csv.export_jsons_to_csv`.
This function takes every singe :code:`.json` file from selected directory and parses it - extracting all the necessary data to create event log.
This requires :class:`langgraph_log_parser.jsons_to_csv.GraphConfig` a custom class that defines how graph was configured so parser can parse accordingly.

In this example we will focus on a basic usage of :code:`GraphConfig`.
I will dive deeper into :code:`GraphConfig` in :ref:`advanced_examples`.

**Example:**

In case of `Building a Basic Chatbot <https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot>`_ we have only one node called :code:`chatbot_node`.

Because of that we will only have one node in :code:`nodes` list. Once graph config is defined we can execute needed method to export all JSON's to one :code:`.csv` file.

.. code-block:: python

    from langgraph_log_parser.jsons_to_csv import GraphConfig, export_jsons_to_csv

    # Taking json's to previously auto generated directory
    output = "test/json"

    # The name of the csv file
    csv_output = "test/csv_output.csv"

    # Basic graph config
    graph_config = GraphConfig(
    nodes=["chatbot_node"]
    )

    export_jsons_to_csv(output, csv_output, graph_config)

**Folder structure should like this now:**

.. code-block:: text

    test/
    ├── db/
    │   └── test.sqlite
    ├── img/
    ├── json/
    │    └── thread_1.json
    │    └── thread_2.json
    │    └── thread_3.json
    │    └── thread_4.json
    │    └── thread_5.json
    └── csv_output.csv

For more details, refer to the documentation of the :mod:`langgraph_log_parser.jsons_to_csv` module.

Running analysis
----------------
We've successfully parsed JSON's into the :code:`.csv` file. Now we can run analysis on the event log.

**I'm not going to go into details on every single function and what it does - we will focus on one that prints full analysis into the console - since it's the easiest way to see the analysis.**

You can find every function specification in modules here:

* :mod:`langgraph_log_parser.analyze` - for running analysis on every :code:`thread_id` `(case_id)`
* :mod:`langgraph_log_parser.analyze_case_id` - for running analysis on single :code:`thread_id` `(case_id)`


In both examples we will use :func:`langgraph_log_parser.load_events.load_event_log` from module :mod:`langgraph_log_parser.load_events` to load event log we will use in analysis.

**Example for analysis on entire event log:**

In case of printing analysis for entire event log we will use :func:`langgraph_log_parser.analyze.print_full_analysis` from module :mod:`langgraph_log_parser.analyze`.

.. code-block:: python

    from langgraph_log_parser.load_events import load_event_log
    from langgraph_log_parser.analyze import print_full_analysis

    # The name of the csv file
    csv_output = "test/csv_output.csv"

    # Using to load events from .csv file
    event_log = load_event_log(csv_output)

    # This function will print an analysis in console for entire event log
    print_full_analysis(event_log)

This will return information for every :code:`thread_id` `(case_id)` about the following:

* start activities
* end activities
* count of each activity (summed from every case)
* every sequence
* ID of last sequence occurrence with probability of occurrence
* minimal self-distances for every activity (on case basis)
* witnesses of minimum self-distances (on case basis)
* count of activity rework (on case basis)
* mean duration of every activity `(in sec)`
* duration of the case `(in sec)` (on case basis)

**Example for analysis on single case_id:**

In case of printing analysis for single :code:`case_id` we will use :func:`langgraph_log_parser.analyze_case_id.print_full_analysis_by_id` from module :mod:`langgraph_log_parser.analyze_case_id`.

.. code-block:: python

    from langgraph_log_parser.load_events import load_event_log
    from langgraph_log_parser.analyze_case_id import print_full_analysis_by_id

    # The name of the csv file
    csv_output = "test/csv_output.csv"

    # Using to load events from .csv file
    event_log = load_event_log(csv_output)

    case_id = 15

    # This function will print an analysis in console for single case_id
    print_full_analysis_by_id(event_log,case_id)

This will return information for single :code:`thread_id` `(case_id)` about the following:

* start activity
* end activity
* count of each activity
* sequence of activities
* sequence of activities with probability of occurrence for the sequence
* minimal self-distances for every activity
* witnesses of minimum self-distances
* count of activity rework
* sum service time of every activity (in sec)
* duration of the case (in sec)
