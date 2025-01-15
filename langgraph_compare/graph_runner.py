from typing import Dict, Any
from langgraph.graph.state import CompiledStateGraph
import copy


def run_multiple_iterations(
        graph: CompiledStateGraph,
        starting_thread_id: int,
        num_repetitions: int,
        user_input_template: Dict[str, Any],
        recursion_limit: int = 100
) -> None:
    """
    Run the provided graph `num_repetitions` times, incrementing the thread_id each time.
    Tracks and displays step iterations within each graph run.

    :param graph: The compiled StateGraph to run.
    :type graph: CompiledStateGraph
    :param starting_thread_id: The starting thread_id for the graph.
    :type starting_thread_id: int
    :param num_repetitions: Number of times to run the graph.
    :type num_repetitions: int
    :param user_input_template: The template for user input, which may vary by iteration.
    :type user_input_template: Dict[str, Any]
    :param recursion_limit: Maximum recursion depth allowed for each graph run.
    :type recursion_limit: int

    **Example**:

    .. code-block:: python

        # .compile method from official langgraph package
        graph = graph_builder.compile(checkpointer=memory)

        # Run the graph for 2 iterations, starting from thread ID 1
        run_multiple_iterations(graph, 1, 2, {"messages": [("user", "Tell me a joke")]})

        # Output:
        # Iteration: 1, Thread_ID 1
        # Step 0:
        # {'messages': [AIMessage(content='Climate change is a significant global challenge...',
        # additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 18,
        # 'prompt_tokens': 11, 'total_tokens': 29}})]}
        # ---
        # Iteration: 2, Thread_ID 2
        # Step 0:
        # {'messages': [AIMessage(content='The climate crisis requires immediate action...',
        # additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 17,
        # 'prompt_tokens': 11, 'total_tokens': 28}})]}
        # ---
    """
    for i in range(num_repetitions):
        # Generate config for current thread ID
        current_thread_id = str(starting_thread_id + i)
        config = {
            "configurable": {"thread_id": current_thread_id},
            "recursion_limit": recursion_limit
        }

        # Create a deep copy of the template for each iteration
        # This ensures complete isolation of state between runs
        user_input = copy.deepcopy(user_input_template)

        print("#" * 30)
        print(f"Iteration: {i + 1}, Thread_ID {current_thread_id}")
        print("#" * 30)

        # Stream the graph with step tracking
        events = graph.stream(user_input, config, stream_mode="values")
        for step_num, event in enumerate(events):
            for key, value in event.items():
                if "__end__" not in value:
                    print(f"Step {step_num}:")
                    print(value)
                    print("---")
