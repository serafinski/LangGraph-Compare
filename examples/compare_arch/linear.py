from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from langgraph_compare import *
from dotenv import load_dotenv
from typing import Annotated
from langgraph.graph.message import add_messages

exp = create_experiment("linear")
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
    return state

def analyzer(state: State) -> State:
    """Analyzer agent that processes research results."""
    messages = state["messages"]
    # Simulate analysis
    state["messages"].append(AIMessage(content="Analysis completed: Processed research data"))
    return state

def writer(state: State) -> State:
    """Writer agent that creates final response."""
    messages = state["messages"]
    state["final_answer"] = "Final synthesized response"
    return state

def build_linear_graph():
    # Define the graph
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("researcher", researcher)
    workflow.add_node("analyzer", analyzer)
    workflow.add_node("writer", writer)

    # Add edges
    workflow.add_edge(START, "researcher")
    workflow.add_edge("researcher", "analyzer")
    workflow.add_edge("analyzer", "writer")
    workflow.add_edge("writer", END)

    # Compile
    chain = workflow.compile(checkpointer=memory)
    return chain

# Create and run the chain
chain = build_linear_graph()

print()
run_multiple_iterations(chain, 1,1000,{"messages": [("user", "Test")]})
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