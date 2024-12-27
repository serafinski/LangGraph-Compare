import os
import pandas as pd
import pm4py
from typing import Union
from langgraph.graph.state import CompiledStateGraph
from .analyze import get_mean_act_times
from .experiment import ExperimentPaths

def generate_mermaid(graph: CompiledStateGraph, output: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save a mermaid graph visualization.

    :param graph: Compiled state graph
    :type graph: CompiledStateGraph
    :param output: ExperimentPaths instance or path to save the visualization
    :type output: Union[ExperimentPaths, str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> generate_mermaid(graph, exp)
    Mermaid saved as: experiments/my_experiment/img/mermaid.png

    >>> # Using direct path:
    >>> generate_mermaid(graph, "output/mermaid.png")
    Mermaid saved as: output/mermaid.png
    """
    if isinstance(output, ExperimentPaths):
        output_path = os.path.join(output.img_dir, 'mermaid.png')
    else:
        output_path = output

    with open(output_path, 'wb') as file:
        file.write(graph.get_graph().draw_mermaid_png())

    print("Mermaid saved as:", output_path)


def generate_prefix_tree(event_log: pd.DataFrame, output: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save a prefix tree visualization.

    :param event_log: Event log data
    :type event_log: pd.DataFrame
    :param output: ExperimentPaths instance or path to save the visualization
    :type output: Union[ExperimentPaths, str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> generate_prefix_tree(event_log, exp)
    Prefix Tree saved as: experiments/my_experiment/img/prefix_tree.png

    >>> # Using direct path:
    >>> generate_prefix_tree(event_log, "output/prefix_tree.png")
    Prefix Tree saved as: output/prefix_tree.png
    """
    if isinstance(output, ExperimentPaths):
        output_path = os.path.join(output.img_dir, 'prefix_tree.png')
    else:
        output_path = output

    # Jeżeli użytkownik nie podał ścieżki
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Wygeneruj prefix tree
    prefix_tree = pm4py.discover_prefix_tree(
        event_log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp'
    )

    # Zapisz wizualizacje prefix tree
    pm4py.save_vis_prefix_tree(prefix_tree, output_path)
    print("Prefix Tree saved as:", output_path)


def generate_performance_dfg(event_log: pd.DataFrame, output: Union[ExperimentPaths, str]) -> None:
    """
    Generate and save a visualization of directly-follows graph annotated with performance.

    :param event_log: Event log data
    :type event_log: pd.DataFrame
    :param output: ExperimentPaths instance or path to save the visualization
    :type output: Union[ExperimentPaths, str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> generate_performance_dfg(event_log, exp)
    Performance DFG saved as: experiments/my_experiment/img/dfg_performance.png

    >>> # Using direct path:
    >>> generate_performance_dfg(event_log, "output/dfg_performance.png")
    Performance DFG saved as: output/dfg_performance.png
    """

    if isinstance(output, ExperimentPaths):
        output_path = os.path.join(output.img_dir, 'dfg_performance.png')
    else:
        output_path = output

    # Jeżeli użytkownik nie podał ścieżki
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)
    pm4py.save_vis_performance_dfg(dfg,start_activities, end_activities, output_path,serv_time=get_mean_act_times(event_log))
    print("Performance DFG saved as:", output_path)


def generate_visualizations(
        event_log: pd.DataFrame,
        graph: CompiledStateGraph,
        output: Union[ExperimentPaths, str]
) -> None:
    """
    Generate and save all process visualizations.

    :param event_log: Event log data
    :type event_log: pd.DataFrame
    :param graph: Compiled state graph
    :type graph: CompiledStateGraph
    :param output: ExperimentPaths instance or directory to save visualizations
    :type output: Union[ExperimentPaths, str]

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
    >>> generate_visualizations(event_log, graph, "output/visualizations")
    Generating all visualizations...
    Mermaid saved as: output/visualizations/mermaid.png
    Prefix Tree saved as: output/visualizations/prefix_tree.png
    Performance DFG saved as: output/visualizations/dfg_performance.png
    All visualizations generated successfully!
    """

    print("Generating all visualizations...")

    if isinstance(output, ExperimentPaths):
        output_dir = output.img_dir
    else:
        output_dir = output
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    # Generate mermaid diagram
    mermaid_path = os.path.join(output_dir, 'mermaid.png')
    generate_mermaid(graph, mermaid_path)

    # Generate prefix tree
    tree_path = os.path.join(output_dir, 'prefix_tree.png')
    generate_prefix_tree(event_log, tree_path)

    # Generate performance DFG
    dfg_path = os.path.join(output_dir, 'dfg_performance.png')
    generate_performance_dfg(event_log, dfg_path)

    print("All visualizations generated successfully!")