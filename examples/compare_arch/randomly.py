from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import AIMessage
from langgraph_compare import *
from dotenv import load_dotenv
import random

exp = create_experiment("random")
memory = exp.memory

load_dotenv()

class State(MessagesState):
    current_step: int
    final_answer: str
    visited_agents: list
    attempts: int


def researcher(state: State) -> State:
    """Research agent that processes the initial query."""
    state["messages"].append(AIMessage(content="Research completed: Found relevant information"))
    state["current_step"] += 1
    state["visited_agents"].append("researcher")
    return state


def analyzer(state: State) -> State:
    """Analyzer agent that processes research results."""
    state["messages"].append(AIMessage(content="Analysis completed: Processed research data"))
    state["current_step"] += 1
    state["visited_agents"].append("analyzer")
    return state


def writer(state: State) -> State:
    """Writer agent that creates final response."""
    state["final_answer"] = "Final synthesized response"
    state["current_step"] += 1
    state["visited_agents"].append("writer")
    return state


def should_end(state: State) -> bool:
    """Determines if the workflow should end."""
    agents = ["researcher", "analyzer", "writer"]
    max_attempts = random.randint(1, 10)
    conditions = [
        # Maximum attempts reached
        state["attempts"] >= max_attempts,
        # All agents visited
        all(agent in state["visited_agents"] for agent in agents),
    ]
    return any(conditions)


def route_next_step(state: State) -> str:
    """Routes to the next step randomly or ends the process."""
    state["attempts"] += 1

    if should_end(state):
        return END

    agents = ["researcher", "analyzer", "writer"]

    return random.choice(agents)


def build_random_graph():
    # Define the graph
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("researcher", researcher)
    workflow.add_node("analyzer", analyzer)
    workflow.add_node("writer", writer)

    # Add edges with conditional routing
    workflow.add_edge(START, "researcher")

    for node in ["researcher", "analyzer", "writer"]:
        workflow.add_conditional_edges(
            node,
            route_next_step,
            {
                "researcher": "researcher",
                "analyzer": "analyzer",
                "writer": "writer",
                END: END
            }
        )

    # Compile with checkpointing
    chain = workflow.compile(checkpointer=memory)
    return chain


# Build the graph and create the chain
chain = build_random_graph()

# Run multiple iterations and analyze results
initial_state = {
    "messages": [("user", "Please research the topic of multi-agent systems")],
    "current_step": 0,
    "visited_agents": [],
    "attempts": 0
}

print()
run_multiple_iterations(chain, 1, 1000, initial_state)
print()

graph_config = GraphConfig(
    nodes=["researcher", "analyzer", "writer"]
)

prepare_data(exp, graph_config)

print()
event_log = load_event_log(exp)
print_analysis(event_log)
print()

generate_artifacts(event_log, chain, exp)