import os
import json
import csv
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from glob import glob
from .experiment import ExperimentPaths


@dataclass
class SupervisorConfig:
    """
    Configuration for a supervisor node.

    :param name: Name of the supervisor.
    :type name: str
    :param supervisor_type: Type of the supervisor ('graph' or 'subgraph').
    :type supervisor_type: str
    """
    name: str
    supervisor_type: str


@dataclass
class SubgraphConfig:
    """
    Configuration for a subgraph and its components.

    :param name: Name of the subgraph.
    :type name: str
    :param nodes: List of nodes within the subgraph.
    :type nodes: List[str]
    :param supervisor: Configuration of the subgraph's supervisor.
    :type supervisor: SupervisorConfig
    """
    name: str
    nodes: List[str]
    supervisor: SupervisorConfig  # Subgraph's supervisor


@dataclass
class GraphConfig:
    """
    Overall graph configuration.

    :param supervisors: Optional list of graph-level supervisors.
    :type supervisors: Optional[List[SupervisorConfig]]
    :param subgraphs: Optional list of subgraphs.
    :type subgraphs: Optional[List[SubgraphConfig]]
    :param nodes: Optional list of nodes for non-subgraph mode.
    :type nodes: Optional[List[str]]
    """
    # Optional graph-level supervisors
    supervisors: Optional[List[SupervisorConfig]] = None
    # Optional subgraphs
    subgraphs: Optional[List[SubgraphConfig]] = None
    # Optional nodes list for non-subgraph mode
    nodes: Optional[List[str]] = None


def _build_config_mappings(graph_config: GraphConfig) -> Dict[str, Any]:
    """
    Build lookup structures from graph configuration.

    :param graph_config: The graph configuration object.
    :type graph_config: GraphConfig

    :return: A dictionary with mappings for supervisors, subgraphs, and nodes.
    :rtype: Dict
    """
    # Initialize all mappings

    # Set of graph-level supervisors (filled in later)
    graph_supervisors = set()
    # Dictionary -> key: subgraph name, value: SubgraphConfig object
    subgraph_map = {}
    # Dictionary -> key: subgraph supervisor name, value: subgraph name
    # For quick lookup to which subgraph a supervisor belongs
    subgraph_supervisors = {}
    # Dictionary -> key: node name, value: subgraph name - for assigning nodes to subgraphs
    node_to_subgraph = {}
    # Set of valid nodes - helps to figure out if activities are valid
    valid_nodes = set()

    # Handle supervisors if present on a graph level in GraphConfig
    if graph_config.supervisors:
        # Fills out the set with all graph-level supervisors names
        graph_supervisors = {sup.name for sup in graph_config.supervisors}

    # Handle subgraphs if present in GraphConfig
    if graph_config.subgraphs:
        # Build mappings for subgraphs (name of subgraph -> SubgraphConfig object)
        subgraph_map = {sg.name: sg for sg in graph_config.subgraphs}
        # Build mappings for subgraph supervisors (name of supervisor -> name of subgraph)
        subgraph_supervisors = {sg.supervisor.name: sg.name for sg in graph_config.subgraphs}

        # Collect nodes from subgraphs
        for sg in graph_config.subgraphs:
            for node in sg.nodes:
                # Assign nodes to subgraphs
                node_to_subgraph[node] = sg.name
                # Add nodes to valid nodes set = ready for processing
                valid_nodes.add(node)

    # Handle non-subgraph case
    elif graph_config.nodes:
        # If there are no subgraphs, we check if we have nodes to process in non-subgraph mode
        # Add all nodes to valid nodes set
        valid_nodes.update(graph_config.nodes)
    else:
        raise ValueError("Either subgraphs or nodes must be provided in the configuration")

    return {
        'graph_supervisors': graph_supervisors,
        'subgraph_map': subgraph_map,
        'subgraph_supervisors': subgraph_supervisors,
        'node_to_subgraph': node_to_subgraph,
        'valid_nodes': valid_nodes
    }


def _is_graph_supervisor(activity: str, config: Dict[str, Any]) -> bool:
    """
    Check if an activity is a graph-level supervisor.

    :param activity: Name of the activity.
    :type activity: str
    :param config: Precomputed configuration mappings.
    :type config: Dict

    :return: True if the activity is a graph-level supervisor.
    :rtype: bool
    """
    return activity in config['graph_supervisors']


def _get_subgraph_context(json_entry: Dict, config: Dict[str, Any], has_subgraphs: bool) -> Optional[str]:
    """
    Determine the current subgraph context from a JSON entry.

    :param json_entry: A single JSON entry to evaluate.
    :type json_entry: Dict
    :param config: Precomputed configuration mappings.
    :type config: Dict
    :param has_subgraphs: Indicates whether the graph config has subgraphs.
    :type has_subgraphs: bool

    :return: Name of the subgraph, if applicable.
    :rtype: Optional[str]
    """
    # If there are no subgraphs, we can't determine the subgraph context
    if not has_subgraphs:
        return None

    # Fetch metadata field from JSON entry
    metadata = json_entry.get('metadata', {})
    # langgraph_checkpoint_ns can contain information on what subgraph we're in like:
    # "langgraph_checkpoint_ns": "ResearchTeam:513d809b-96a1-a27b-6e39-d31ac60f8c30|Search:a5527da0-52df-17fe-4e51-e7073b748101"
    if 'langgraph_checkpoint_ns' in metadata:
        checkpoint_ns = metadata['langgraph_checkpoint_ns']
        # Split the checkpoint_ns by '|' and take the first part
        parts = checkpoint_ns.split('|')
        if parts:
            # Split the first part by ':' and take the first part (e.g. "ResearchTeam")
            subgraph_name = parts[0].split(':')[0]
            # Check if the subgraph_name is in the subgraph_map
            if subgraph_name in config['subgraph_map']:
                return subgraph_name

    # If langgraph_checkpoint_ns is not present, we can try to get the langgraph_node like:
    # "langgraph_node": "ResearchTeam"
    node = metadata.get('langgraph_node')
    # If the node is in the node_to_subgraph mapping, we can return the subgraph name
    if node in config['node_to_subgraph']:
        return config['node_to_subgraph'][node]

    return None


def _is_valid_activity(activity: str, config: Dict[str, Any]) -> bool:
    """
    Check if an activity should be included in the CSV output.

    :param activity: Name of the activity
    :param config: Precomputed configuration mappings
    :return: True if the activity should be included
    """
    return (
            activity == '__start__' or
            _is_graph_supervisor(activity, config) or
            activity in config['subgraph_supervisors'] or
            activity in config['valid_nodes']
    )


def _find_end_timestamp(json_data: List[Dict], start_index: int, case_id: Any, config: Dict[str, Any]) -> Optional[Any]:
    """
    Look ahead in the JSON entries to find the next timestamp for the same case_id,
    but only from activities that will be saved to the CSV.

    :param json_data: List of all JSON entries
    :param start_index: Current index in the JSON data
    :param case_id: The thread_ID/case_id we are processing
    :param config: Precomputed configuration mappings
    :return: The next valid timestamp or None if not found
    """
    # Look ahead for the next timestamp
    for j in range(start_index + 1, len(json_data)):
        # Get the next JSON entry
        next_json = json_data[j]
        # Check same thread_ID
        if next_json.get('thread_ID') != case_id:
            continue

        # Get writes from metadata
        writes = next_json.get('metadata', {}).get('writes', {})
        if not writes:
            continue

        # Find the next activity (first key that isn't 'messages')
        next_activity = next((key for key in writes.keys() if key != 'messages'), None)
        if not next_activity:
            continue

        # Only use timestamp if the activity would be saved to CSV
        if _is_valid_activity(next_activity, config):
            return next_json['checkpoint'].get('ts')

    return None


def _insert_subgraph_start_if_needed(
        json_data: List[Dict],
        current_index: int,
        case_id: Any,
        entries_to_write: List[Dict[str, Any]],
        config: Dict[str, Any]
) -> None:
    """
    Look ahead for a subgraph supervisor activity when we're currently on a graph supervisor
    and insert a '__start__' entry for it, if found.

    :param json_data: List of all JSON entries.
    :type json_data: List[Dict]
    :param current_index: Current index in the JSON data.
    :type current_index: int
    :param case_id: The thread_ID/case_id we are processing.
    :type case_id: Any
    :param entries_to_write: The list of entries to eventually be written to CSV.
    :type entries_to_write: List[Dict[str, Any]]
    :param config: Precomputed configuration mappings.
    :type config: Dict
    """
    # Look ahead for next subgraph supervisor activity
    for j in range(current_index + 1, len(json_data)):
        next_json = json_data[j]
        # If the thread_ID is different, skip
        if next_json.get('thread_ID') != case_id:
            continue

        # Looking for the next JSON entry with writes
        next_metadata = next_json.get('metadata', {})
        next_writes = next_metadata.get('writes', {})
        if not next_writes:
            continue

        # Find the next key that isn't 'messages' - this is the next activity
        next_activity = next((key for key in next_writes.keys() if key != 'messages'), None)

        # If the next activity is a subgraph supervisor, we need to write an __start__ entry
        if next_activity in config['subgraph_supervisors']:
            # Get information about the next subgraph supervisor (the subgraph name)
            next_context = config['subgraph_supervisors'][next_activity]
            # Write an __start__ entry for the next subgraph supervisor
            entries_to_write.append({
                'case_id': case_id,
                'timestamp': next_json['checkpoint'].get('ts'),
                'end_timestamp': next_json['checkpoint'].get('ts'),
                'cost': 0,
                'activity': '__start__',
                # org:resource is the next subgraph's name
                'org:resource': next_context
            })
            break


def _handle_subgraph_mode(
        activity: str,
        visited_global_start: bool,
        i: int,
        json_data: List[Dict],
        case_id: Any,
        config: Dict[str, Any],
        context: Optional[str],
        entries_to_write: List[Dict[str, Any]]
) -> Tuple[bool, Optional[str], bool]:
    """
    Handle the processing logic for subgraph mode.

    :param activity: The identified activity from a JSON entry.
    :type activity: str
    :param visited_global_start: Whether we've visited the global '__start__'.
    :type visited_global_start: bool
    :param i: The current index of the JSON entry in the json_data list.
    :type i: int
    :param json_data: The entire list of JSON entries.
    :type json_data: List[Dict]
    :param case_id: The thread_ID/case_id we are processing.
    :type case_id: Any
    :param config: Precomputed configuration mappings.
    :type config: Dict
    :param context: The subgraph context if available.
    :type context: Optional[str]
    :param entries_to_write: The list where processed entries are accumulated.
    :type entries_to_write: List[Dict]

    :return: A tuple of (should_write, org_resource, visited_global_start).
    :rtype: Tuple[bool, Optional[str], bool]
    """
    should_write = False
    org_resource = None

    # Visiting global __start__ activity for the first time
    if activity == '__start__' and not visited_global_start:
        should_write = True
        org_resource = '__start__'
        visited_global_start = True

    # If activity is a graph supervisor
    elif _is_graph_supervisor(activity, config):
        should_write = True
        # org_resource is the name of the graph supervisor
        org_resource = activity
        # Look ahead for next subgraph supervisor activity
        _insert_subgraph_start_if_needed(json_data, i, case_id, entries_to_write, config)

    # If activity is a subgraph supervisor
    elif activity in config['subgraph_supervisors']:
        should_write = True
        # org_resource is name of the subgraph
        org_resource = config['subgraph_supervisors'][activity]

    # If activity is a node in a subgraph
    elif activity in config['valid_nodes'] and context:
        should_write = True
        # org_resource is the subgraph name
        org_resource = config['node_to_subgraph'][activity]

    return should_write, org_resource, visited_global_start


def _handle_non_subgraph_mode(
        activity: str,
        visited_global_start: bool,
        has_supervisors: bool,
        config: Dict[str, Any]
) -> Tuple[bool, Optional[str], bool]:
    """
    Handle the processing logic for non-subgraph mode.

    :param activity: The identified activity from a JSON entry.
    :type activity: str
    :param visited_global_start: Whether we've visited the global '__start__'.
    :type visited_global_start: bool
    :param has_supervisors: Indicates whether the graph config has supervisors.
    :type has_supervisors: bool
    :param config: Precomputed configuration mappings.
    :type config: Dict

    :return: A tuple of (should_write, org_resource, visited_global_start).
    :rtype: Tuple[bool, Optional[str], bool]
    """
    should_write = False
    org_resource = None

    # Visiting global __start__ activity for the first time
    if activity == '__start__' and not visited_global_start:
        should_write = True
        org_resource = '__start__'
        visited_global_start = True

    # If activity is a graph supervisor
    elif has_supervisors and _is_graph_supervisor(activity, config):
        should_write = True
        # org_resource is the activity itself
        org_resource = activity

    # Only process explicitly listed nodes
    elif activity in config['valid_nodes']:
        should_write = True
        # org_resource is the activity itself
        org_resource = activity

    return should_write, org_resource, visited_global_start


def _process_single_json(json_data: List[Dict], graph_config: GraphConfig, config: Dict) -> List[Dict[str, Any]]:
    """
    Process a single JSON and return entries to write.

    :param json_data: List of JSON entries.
    :type json_data: List[Dict]
    :param graph_config: The graph configuration object.
    :type graph_config: GraphConfig
    :param config: Precomputed configuration mappings.
    :type config: Dict

    :return: List of processed entries to write.
    :rtype: List[Dict]
    """
    # Check if the graph configuration has subgraphs
    has_subgraphs = bool(graph_config.subgraphs)
    # Check if the graph configuration has supervisors
    has_supervisors = bool(graph_config.supervisors)
    # Have we visited global __start__ activity?
    visited_global_start = False

    # First collect all valid entries organized by case_id
    entries_by_case = {}

    # First pass to collect valid activities
    for i, json_entry in enumerate(json_data):
        # Extract thread_ID from JSON entry
        case_id = json_entry.get('thread_ID')
        # Extract timestamp from checkpoint field in JSON entry
        timestamp = json_entry['checkpoint'].get('ts')

        # Extract metadata field from JSON entry
        metadata = json_entry.get('metadata', {})
        # Extract writes field from metadata
        writes = metadata.get('writes', {})

        if not writes:
            continue

        # Look for the first key in writes that isn't 'messages'
        # This is the activity name
        activity = next((key for key in writes.keys() if key != 'messages'), None)
        if not activity:
            continue

        # If we haven't seen this case_id before, create an empty list
        if case_id not in entries_by_case:
            entries_by_case[case_id] = []

        # Get the subgraph context if applicable
        context = _get_subgraph_context(json_entry, config, has_subgraphs) if has_subgraphs else None

        # Determine if we should write this entry and get its org_resource
        if has_subgraphs:
            should_write, org_resource, visited_global_start = _handle_subgraph_mode(
                activity=activity,
                visited_global_start=visited_global_start,
                i=i,
                json_data=json_data,
                case_id=case_id,
                config=config,
                context=context,
                # We'll handle __start__ entries separately
                entries_to_write=[]
            )
        else:
            should_write, org_resource, visited_global_start = _handle_non_subgraph_mode(
                activity=activity,
                visited_global_start=visited_global_start,
                has_supervisors=has_supervisors,
                config=config
            )

        # If the activity should be written, compute end_timestamp
        if should_write:
            entries_by_case[case_id].append({
                'case_id': case_id,
                'timestamp': timestamp,
                'activity': activity,
                'org:resource': org_resource,
            })

    # Now process the collected entries, add subgraph __start__ entries where needed, and set end_timestamps
    final_entries = []
    for case_id, entries in entries_by_case.items():
        # Sort entries by timestamp
        entries.sort(key=lambda x: x['timestamp'])
        processed_entries = []

        # Process entries and add __start__ entries where needed
        for i, entry in enumerate(entries):
            current_activity = entry['activity']

            # If this is a subgraph supervisor and the previous activity was a global supervisor
            # (or we're just starting), add a __start__ entry
            if (current_activity in config['subgraph_supervisors'] and
                    (i == 0 or _is_graph_supervisor(entries[i - 1]['activity'], config))):
                subgraph_name = config['subgraph_supervisors'][current_activity]
                processed_entries.append({
                    'case_id': case_id,
                    'timestamp': entry['timestamp'],
                    'activity': '__start__',
                    'org:resource': subgraph_name,
                })

            processed_entries.append(entry)

        # Set end_timestamps
        for i, entry in enumerate(processed_entries):
            if i < len(processed_entries) - 1:
                # If not the last entry, end_timestamp is the next entry's timestamp
                end_timestamp = processed_entries[i + 1]['timestamp']
            else:
                # If last entry, end_timestamp is its own timestamp
                end_timestamp = entry['timestamp']

            final_entries.append({
                'case_id': entry['case_id'],
                'timestamp': entry['timestamp'],
                'end_timestamp': end_timestamp,
                'cost': 0,
                'activity': entry['activity'],
                'org:resource': entry['org:resource']
            })

    return final_entries

def _validate_directory(directory_path: str) -> None:
    """
    Validate that the specified directory exists.

    :param directory_path: Path to the directory
    :type directory_path: str
    :raises FileNotFoundError: If the directory does not exist
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory does not exist: {directory_path}")


def export_jsons_to_csv(source: Union[ExperimentPaths, str], graph_config: GraphConfig,
                        output_dir: Optional[str] = None) -> None:
    """
    Process all JSON files and export them to csv_output.csv in the specified directory.
    Can use either an ExperimentPaths instance or explicit paths.

    :param source: Either an ExperimentPaths instance or a path to the JSON directory
    :type source: Union[ExperimentPaths, str]
    :param graph_config: The graph configuration object
    :type graph_config: GraphConfig
    :param output_dir: Directory where csv_output.csv will be saved (required if source is a str)
    :type output_dir: Optional[str]

    **Examples:**

    >>> # Using ExperimentPaths:
    >>> exp = create_experiment("my_experiment")
    >>> graph_config = GraphConfig(nodes=["chatbot_node"])
    >>> export_jsons_to_csv(exp, graph_config)
    Processed: experiments/my_experiment/json/thread_1.json
    Processed: experiments/my_experiment/json/thread_2.json
    Processed: experiments/my_experiment/json/thread_3.json
    Successfully exported combined data to: experiments/my_experiment/csv/csv_output.csv

    >>> # Using direct paths:
    >>> export_jsons_to_csv("path/to/jsons", graph_config, "path/to/output_directory")
    Processed: path/to/jsons/thread_1.json
    Processed: path/to/jsons/thread_2.json
    Processed: path/to/jsons/thread_3.json
    Successfully exported combined data to: path/to/output_directory/csv_output.csv
    """

    csv_fields = ['case_id', 'timestamp', 'end_timestamp', 'cost', 'activity', 'org:resource']

    # Determine paths based on input type
    if isinstance(source, ExperimentPaths):
        json_dir = source.json_dir
        output_path = source.get_csv_path()
    else:
        if output_dir is None:
            raise ValueError("output_dir must be provided when using a JSON directory path directly")

        # Validate that both directories exist
        _validate_directory(source)  # Validate JSON directory
        _validate_directory(output_dir)  # Validate output directory

        json_dir = source
        output_path = os.path.join(output_dir, 'csv_output.csv')

    # Build configuration mappings
    config = _build_config_mappings(graph_config)

    # Get all JSON files from the experiment's json directory
    json_files = glob(os.path.join(json_dir, '*.json'))

    if not json_files:
        raise ValueError(f"No JSON files found in {json_dir}")

    # Placeholder for all entries
    all_entries = []

    # Process each JSON file
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                jsons = json.load(f)

            # Process the current JSON file
            entries = _process_single_json(jsons, graph_config, config)
            # Append processed entries to all_entries
            all_entries.extend(entries)

            print(f"Processed: {json_file}")
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")

    # Sort all entries by timestamp
    all_entries.sort(key=lambda x: x['timestamp'])

    # Write combined results to CSV
    with open(output_path, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(all_entries)

    print(f"Successfully exported combined data to: {output_path}")
