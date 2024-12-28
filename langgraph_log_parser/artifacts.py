import pandas as pd
from typing import Union, Optional
from langgraph.graph.state import CompiledStateGraph

from .experiment import ExperimentPaths
from .sql_to_jsons import export_sqlite_to_jsons
from .jsons_to_csv import  GraphConfig, export_jsons_to_csv
from .create_report import generate_reports
from .visualize import generate_visualizations

def prepare_data(
    source: Union[ExperimentPaths, str],
    graph_config: GraphConfig,
    output_folder: Optional[str] = None,
    csv_path: Optional[str] = None
) -> None:
    """
    Complete pipeline to export data from SQLite to CSV via JSON intermediary.
    Executes export_sqlite_to_jsons followed by export_jsons_to_csv.

    :param source: Either an ExperimentPaths instance or a path to the SQLite database
    :type source: Union[ExperimentPaths, str]
    :param graph_config: The graph configuration object for CSV export
    :type graph_config: GraphConfig
    :param output_folder: Path to the output folder for JSON files (required if source is a str)
    :type output_folder: Optional[str]
    :param csv_path: Path for the output CSV file (required if source is a str)
    :type csv_path: Optional[str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> graph_config = GraphConfig(nodes=["chatbot_node"])
    >>> export_sqlite_to_csv(exp, graph_config)
    JSON file created: experiments/my_experiment/json/thread_1.json
    JSON file created: experiments/my_experiment/json/thread_2.json
    Processed: experiments/my_experiment/json/thread_1.json
    Processed: experiments/my_experiment/json/thread_2.json
    Successfully exported combined data to: experiments/my_experiment/csv/csv_output.csv

    >>> # Using direct paths:
    >>> export_sqlite_to_csv(
    ...     "path/to/db.sqlite",
    ...     graph_config,
    ...     output_folder="path/to/json_output",
    ...     csv_path="path/to/output.csv"
    ... )
    JSON file created: path/to/json_output/thread_1.json
    JSON file created: path/to/json_output/thread_2.json
    Processed: path/to/json_output/thread_1.json
    Processed: path/to/json_output/thread_2.json
    Successfully exported combined data to: path/to/output.csv
    """
    # Step 1: Export SQLite to JSON files
    export_sqlite_to_jsons(source, output_folder)

    print()

    # Step 2: Convert JSON files to CSV
    # If using ExperimentPaths, we pass the same source
    # If using direct paths, we need to pass the JSON output directory as source
    json_source = source if isinstance(source, ExperimentPaths) else output_folder
    export_jsons_to_csv(json_source, graph_config, csv_path)

def generate_artifacts(
    event_log: pd.DataFrame,
    graph: CompiledStateGraph,
    output: Union[ExperimentPaths, str]
) -> None:
    """
    Generate all analysis artifacts including reports and visualizations.
    Executes generate_reports followed by generate_visualizations.

    :param event_log: Event log data containing process execution information
    :type event_log: pd.DataFrame
    :param graph: Compiled state graph for visualization generation
    :type graph: CompiledStateGraph
    :param output: ExperimentPaths instance or path to save the analysis outputs
    :type output: Union[ExperimentPaths, str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> generate_artifacts(event_log,graph,exp)
    Metrics report successfully generated at: experiments/my_experiment/reports/metrics_report.json
    Sequences report successfully generated at: experiments/my_experiment/reports/sequences_report.json
    All reports successfully generated.
    Generating all visualizations...
    Mermaid saved as: experiments/my_experiment/img/mermaid.png
    Prefix Tree saved as: experiments/my_experiment/img/prefix_tree.png
    Performance DFG saved as: experiments/my_experiment/img/dfg_performance.png
    All visualizations generated successfully!
    Analysis generation completed successfully!

    >>> # Using direct path:
    >>> generate_artifacts(event_log,graph,"analysis_output")
    Metrics report successfully generated at: analysis_output/reports/metrics_report.json
    Sequences report successfully generated at: analysis_output/reports/sequences_report.json
    All reports successfully generated.
    Generating all visualizations...
    Mermaid saved as: analysis_output/img/mermaid.png
    Prefix Tree saved as: analysis_output/img/prefix_tree.png
    Performance DFG saved as: analysis_output/img/dfg_performance.png
    All visualizations generated successfully!
    Analysis generation completed successfully!
    """
    # Step 1: Generate reports
    generate_reports(event_log, output)

    print()

    # Step 2: Generate visualizations
    generate_visualizations(event_log, graph, output)

    print("Analysis generation completed successfully!")