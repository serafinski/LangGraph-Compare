import os
import pandas as pd
import pm4py
from typing import Union
from langgraph.graph.state import CompiledStateGraph
from .analyze import get_mean_act_times
from .experiment import ExperimentPaths


def _validate_directory(directory_path: str) -> None:
    """
    Validate that the specified directory exists.

    :param directory_path: Path to the directory
    :type directory_path: str
    :raises FileNotFoundError: If the directory does not exist
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory does not exist: {directory_path}")


def generate_mermaid(graph: CompiledStateGraph, output_dir: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save a mermaid graph visualization.

    :param graph: Compiled state graph
    :type graph: CompiledStateGraph
    :param output_dir: ExperimentPaths instance or directory path where visualization will be saved
    :type output_dir: Union[ExperimentPaths, str]
    :raises FileNotFoundError: If the output directory does not exist

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> generate_mermaid(graph, exp)
    Mermaid saved as: experiments/my_experiment/img/mermaid.png

    >>> # Using direct path:
    >>> generate_mermaid(graph, "output/visualizations")  # Directory must exist
    Mermaid saved as: output/visualizations/mermaid.png
    """
    if isinstance(output_dir, ExperimentPaths):
        img_dir = output_dir.img_dir
    else:
        img_dir = output_dir

    _validate_directory(img_dir)

    # Create the full file path
    output_path = os.path.join(img_dir, 'mermaid.png')

    with open(output_path, 'wb') as file:
        file.write(graph.get_graph().draw_mermaid_png())

    print("Mermaid saved as:", output_path)


def generate_prefix_tree(event_log: pd.DataFrame, output_dir: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save a prefix tree visualization.

    :param event_log: Event log data
    :type event_log: pd.DataFrame
    :param output_dir: ExperimentPaths instance or directory path where visualization will be saved
    :type output_dir: Union[ExperimentPaths, str]
    :raises FileNotFoundError: If the output directory does not exist

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> generate_prefix_tree(event_log, exp)
    Prefix Tree saved as: experiments/my_experiment/img/prefix_tree.png

    >>> # Using direct path:
    >>> generate_prefix_tree(event_log, "output/visualizations")  # Directory must exist
    Prefix Tree saved as: output/visualizations/prefix_tree.png
    """
    if isinstance(output_dir, ExperimentPaths):
        img_dir = output_dir.img_dir
    else:
        img_dir = output_dir

    _validate_directory(img_dir)
    output_path = os.path.join(img_dir, 'prefix_tree.png')

    # Generate prefix tree
    prefix_tree = pm4py.discover_prefix_tree(
        event_log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp'
    )

    # Save prefix tree visualization
    pm4py.save_vis_prefix_tree(prefix_tree, output_path)
    print("Prefix Tree saved as:", output_path)


def generate_performance_dfg(event_log: pd.DataFrame, output_dir: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save a visualization of directly-follows graph annotated with performance.

    :param event_log: Event log data
    :type event_log: pd.DataFrame
    :param output_dir: ExperimentPaths instance or directory path where visualization will be saved
    :type output_dir: Union[ExperimentPaths, str]
    :raises FileNotFoundError: If the output directory does not exist

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> generate_performance_dfg(event_log, exp)
    Performance DFG saved as: experiments/my_experiment/img/dfg_performance.png

    >>> # Using direct path:
    >>> generate_performance_dfg(event_log, "output/visualizations")  # Directory must exist
    Performance DFG saved as: output/visualizations/dfg_performance.png
    """
    if isinstance(output_dir, ExperimentPaths):
        img_dir = output_dir.img_dir
    else:
        img_dir = output_dir

    _validate_directory(img_dir)
    output_path = os.path.join(img_dir, 'dfg_performance.png')

    dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)
    pm4py.save_vis_performance_dfg(dfg, start_activities, end_activities, output_path,
                                   serv_time=get_mean_act_times(event_log))
    print("Performance DFG saved as:", output_path)


def generate_visualizations(event_log: pd.DataFrame, graph: CompiledStateGraph,
                            output_dir: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save all process visualizations.

    :param event_log: Event log data
    :type event_log: pd.DataFrame
    :param graph: Compiled state graph
    :type graph: CompiledStateGraph
    :param output_dir: ExperimentPaths instance or directory path where visualizations will be saved
    :type output_dir: Union[ExperimentPaths, str]
    :raises FileNotFoundError: If the output directory does not exist

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> generate_visualizations(event_log, graph, exp)
    Generating all visualizations...
    Mermaid saved as: experiments/my_experiment/img/mermaid.png
    Prefix Tree saved as: experiments/my_experiment/img/prefix_tree.png
    Performance DFG saved as: experiments/my_experiment/img/dfg_performance.png
    All visualizations generated successfully!

    >>> # Using direct path:
    >>> generate_visualizations(event_log, graph, "output/visualizations")  # Directory must exist
    Generating all visualizations...
    Mermaid saved as: output/visualizations/mermaid.png
    Prefix Tree saved as: output/visualizations/prefix_tree.png
    Performance DFG saved as: output/visualizations/dfg_performance.png
    All visualizations generated successfully!
    """
    print("Generating all visualizations...")

    generate_mermaid(graph, output_dir)
    generate_prefix_tree(event_log, output_dir)
    generate_performance_dfg(event_log, output_dir)

    print("All visualizations generated successfully!")