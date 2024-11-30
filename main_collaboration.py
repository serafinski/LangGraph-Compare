import sqlite3

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph, START
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
import functools
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode

from langgraph_log_parser import *

exp = initialize_experiment("collaboration")

# Inicjalizacja .env
load_dotenv()

conn = sqlite3.connect(exp.database, check_same_thread=False)
memory = SqliteSaver(conn)

#####
# TWORZENIE AGENTA
#####
def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)

#####
# TWORZENIE TOOL'A
#####
tavily_tool = TavilySearchResults(max_results=5)

# Warning: This executes code locally, which can be unsafe when not sandboxed

repl = PythonREPL()

@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )

#####
# DEFINIOWANIE STANU
#####

# This defines the object that is passed between each node
# in the graph. We will create different nodes for each agent and tool
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str

#####
# DEFINIOWANIE WĘZŁÓW AGENTA
#####

# Helper function to create a node for a given agent
def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }


llm = ChatOpenAI(model="gpt-4o")

# Research agent and node
research_agent = create_agent(
    llm,
    [tavily_tool],
    system_message="You should provide accurate data for the chart_generator to use.",
)
research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

# chart_generator
chart_agent = create_agent(
    llm,
    [python_repl],
    system_message="Any charts you display will be visible by the user.",
)
chart_node = functools.partial(agent_node, agent=chart_agent, name="chart_generator")

#####
# DEFINIOWANIE TOOL NODE'A
#####
tools = [tavily_tool, python_repl]
tool_node = ToolNode(tools)

#####
# DEFINIOWANIE LOGIKI KRAWĘDZI
#####

# Either agent can decide to end
def router(state):
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        # The previous agent is invoking a tool
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    return "continue"

#####
# DEFINIOWANIE KOŃCOWEGO GRAFU
#####

workflow = StateGraph(AgentState)

workflow.add_node("Researcher", research_node)
workflow.add_node("chart_generator", chart_node)
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "Researcher",
    router,
    {"continue": "chart_generator", "call_tool": "call_tool", END: END},
)
workflow.add_conditional_edges(
    "chart_generator",
    router,
    {"continue": "Researcher", "call_tool": "call_tool", END: END},
)

workflow.add_conditional_edges(
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],
    {
        "Researcher": "Researcher",
        "chart_generator": "chart_generator",
    },
)
workflow.add_edge(START, "Researcher")
graph = workflow.compile(checkpointer=memory)

# config = {"configurable": {"thread_id": "4"},"recursion_limit": 150}
#
# events = graph.stream(
#     {
#         "messages": [
#             HumanMessage(
#                 content="Fetch the UK's GDP over the past 5 years,"
#                 " then draw a line graph of it."
#                 " Once you code it up, finish."
#             )
#         ],
#     },
#     # Maximum number of steps to take in the graph
#     config,
# )
# for s in events:
#     print(s)
#     print("----")

user_input = {
    "messages": [
        HumanMessage(
            content="Fetch the UK's GDP over the past 5 years,"
                    " then draw a line graph of it."
                    " Once you code it up, finish."
        )
    ]
}

run_graph_iterations(
    graph=graph,
    starting_thread_id=1,
    num_repetitions=3,
    user_input_template=user_input,
    recursion_limit=150
)

export_sqlite_to_jsons(exp.database, exp.json_dir)

graph_config = GraphConfig(
    nodes=['Researcher','chart_generator', 'call_tool']
)

export_jsons_to_csv(exp.json_dir, exp.get_csv_path(), graph_config)

# ANALIZA
print()
event_log = load_event_log(exp.get_csv_path())
print_full_analysis(event_log)
generate_prefix_tree(event_log, exp.get_img_path())
generate_performance_dfg(event_log, exp.get_img_path())