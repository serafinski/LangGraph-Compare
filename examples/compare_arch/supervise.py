from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import AIMessage
from langgraph_compare import *
from dotenv import load_dotenv
import random
from typing import Literal
from pydantic import BaseModel

exp = create_experiment("supervise")
memory = exp.memory

load_dotenv()

# Define valid routing options
VALID_STEPS = ["researcher", "analyser", "writer"]
options = ["FINISH"] + VALID_STEPS


# Define the response model for supervisor
class RouteResponse(BaseModel):
    next: Literal["FINISH", "researcher", "analyser", "writer"]


# Define the agent state
class AgentState(MessagesState):
    next: str
    current_step: int


def increment_step(state: AgentState) -> AgentState:
    """Helper function to increment step counter"""
    state["current_step"] = state.get("current_step", 0) + 1
    return state


def supervisor(state: AgentState) -> AgentState:
    """Supervisor agent that controls the workflow."""
    # Increment step counter twice - once for review, once for decision
    state = increment_step(state)
    state = increment_step(state)

    # Check if we've exceeded step limit
    if state["current_step"] >= 18:
        return {"next": "FINISH", "current_step": state["current_step"]}

    # 75% chance to continue to next step, 25% chance to retry current step
    if random.random() >= 0.25:
        last_message = state["messages"][-1].content if state["messages"] else None

        if "Research completed" in str(last_message):
            return {"next": "analyser", "current_step": state["current_step"]}
        elif "Analysis completed" in str(last_message):
            return {"next": "writer", "current_step": state["current_step"]}
        elif "Final synthesized" in str(last_message):
            return {"next": "FINISH", "current_step": state["current_step"]}
        else:
            return {"next": "researcher", "current_step": state["current_step"]}
    else:
        # Get current node from last message or default to researcher
        last_message = state["messages"][-1].content if state["messages"] else None
        current = "researcher"
        for step in VALID_STEPS:
            if step in str(last_message).lower():
                current = step
                break
        return {"next": current, "current_step": state["current_step"]}


def researcher(state: AgentState) -> AgentState:
    """Research agent that processes the initial query."""
    state = increment_step(state)
    return {
        "messages": [AIMessage(content="Research completed: Found relevant information")],
        "current_step": state["current_step"]
    }


def analyser(state: AgentState) -> AgentState:
    """Analyser agent that processes research results."""
    state = increment_step(state)
    return {
        "messages": [AIMessage(content="Analysis completed: Processed research data")],
        "current_step": state["current_step"]
    }


def writer(state: AgentState) -> AgentState:
    """Writer agent that creates final response."""
    state = increment_step(state)
    return {
        "messages": [AIMessage(content="Final synthesized response")],
        "current_step": state["current_step"]
    }


def build_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("researcher", researcher)
    workflow.add_node("analyser", analyser)
    workflow.add_node("writer", writer)

    # Add initial edge from START to supervisor
    workflow.add_edge(START, "supervisor")

    # Add edges from worker nodes to supervisor
    for node in VALID_STEPS:
        workflow.add_edge(node, "supervisor")

    # Add conditional edges from supervisor
    conditional_map = {k: k for k in VALID_STEPS}
    conditional_map["FINISH"] = END

    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x["next"],
        conditional_map
    )

    chain = workflow.compile(checkpointer=memory)
    return chain


chain = build_graph()

print()
run_multiple_iterations(chain, 1, 1000, {
    "messages": [AIMessage(content="Please research the topic of multi-agent systems")],
    "current_step": 0,
    "next": "researcher"
})
print()

graph_supervisor = SupervisorConfig(
    name="supervisor",
    supervisor_type="graph"
)

graph_config = GraphConfig(
    supervisors=[graph_supervisor],
    nodes=["researcher", "analyser", "writer"]
)

prepare_data(exp, graph_config)

print()
event_log = load_event_log(exp)
print_analysis(event_log)
print()

generate_artifacts(event_log, chain, exp)