from dotenv import load_dotenv
from typing import Annotated

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph_log_parser import *

exp = create_experiment("tavily")
memory = exp.memory

# Inicjalizacja .env
load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


tool = TavilySearchResults(max_results=2)
tools = [tool]

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot_node", chatbot)

# Tutaj predefiniowane
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot_node",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot_node")
graph_builder.set_entry_point("chatbot_node")

graph = graph_builder.compile(checkpointer=memory)

# config = {"configurable": {"thread_id": "2"}}
# user_input = {"messages": [("user", "Tell me about PJATK in Warsaw")]}
#
# # Wywołanie grafu
# for event in graph.stream(user_input, config):
#     for value in event.values():
#         print("Assistant:", value["messages"][-1].content)

user_input = {"messages": [("user", "Tell me about PJATK in Warsaw")]}

print()
run_multiple_iterations(graph, 1, 3, user_input)
print()

graph_config = GraphConfig(
    nodes=["chatbot_node", "tools"]
)

prepare_data(exp, graph_config)

# ANALIZA
print()
event_log = load_event_log(exp)
print_analysis(event_log)
print()

generate_artifacts(event_log, graph, exp)