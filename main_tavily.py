import sqlite3

from dotenv import load_dotenv
from typing import Annotated

from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph_log_parser import *

create_folder_structure("files/tavily")

database = "files/tavily/db/tavily.sqlite"

# Inicjalizacja .env
load_dotenv()

conn = sqlite3.connect(database, check_same_thread=False)
memory = SqliteSaver(conn)

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

run_graph_iterations(graph, 6, 3, user_input)

output = "files/tavily/json"
csv_output = "files/tavily/csv_output.csv"

export_sqlite_to_jsons(database, output)

graph_config = GraphConfig(
    nodes=["chatbot_node", "tools"]
)

export_jsons_to_csv(output, csv_output, graph_config)

# ANALIZA
print()
event_log = load_event_log(csv_output)
print_full_analysis(event_log)
generate_prefix_tree(event_log, 'files/tavily/img/tree.png')