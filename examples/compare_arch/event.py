from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from langgraph_compare import *
from dotenv import load_dotenv
from langgraph.graph.message import add_messages

exp = create_experiment("event")
memory = exp.memory

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]
    current_step: int
    final_answer: str

def researcher(state: State) -> State:
    """Research agent that processes the initial query."""
    messages = state["messages"]
    # Simulate research processing
    state["messages"].append(AIMessage(content="Research completed: Found relevant information"))
    state["current_step"] += 1
    return state

def analyzer(state: State) -> State:
    """Analyzer agent that processes research results."""
    messages = state["messages"]
    # Simulate analysis
    state["messages"].append(AIMessage(content="Analysis completed: Processed research data"))
    state["current_step"] += 1
    return state

def writer(state: State) -> State:
    """Writer agent that creates final response."""
    messages = state["messages"]
    state["final_answer"] = "Final synthesized response"
    state["current_step"] += 1
    return state


def should_end(state: State) -> bool:
    """Determines if the workflow should end based on step count."""
    return state["current_step"] >= 12


def route_next_step(state: State) -> str:
    """Routes to the next step in the cycle or ends if step count reached."""
    if should_end(state):
        return END

    # Determine next step based on current step modulo 3
    step_position = state["current_step"] % 3
    if step_position == 0:
        return "researcher"
    elif step_position == 1:
        return "analyzer"
    else:
        return "writer"

def build_event_driven_graph():
    # Define the graph
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("researcher", researcher)
    workflow.add_node("analyzer", analyzer)
    workflow.add_node("writer", writer)

    # Add edges with proper conditional routing
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

        # Compile
    chain = workflow.compile(checkpointer=memory)
    return chain

chain = build_event_driven_graph()

print()
run_multiple_iterations(chain, 1,1000,{"messages": [("user", "Test")], "current_step": 0})
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