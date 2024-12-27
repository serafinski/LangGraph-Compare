from dotenv import load_dotenv
from typing import Annotated

from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langgraph_log_parser import *

exp = create_experiment("main")
memory = exp.memory

# Inicjalizacja .env
load_dotenv()

class State(TypedDict):
    # Klucz Messages ma typ "list". The
    # Funkcja `add_messages` definuje jak klucz ma być aktualizowany
    # (w tym przypadku dodanie do listy, nie nadpisywanie)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-4o-mini")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# Pierwszy argument - unikatowa nazwa node'a
# Drugi argument - funkcja która będzie wywoływana kiedy node będzie używany
graph_builder.add_node("chatbot_node", chatbot)

graph_builder.add_edge(START, "chatbot_node")
graph_builder.add_edge("chatbot_node", END)

graph = graph_builder.compile(checkpointer=memory)

print()
run_multiple_iterations(graph, 1, 5, {"messages": [("user", "Tell me a joke")]})

print()
export_sqlite_to_jsons(exp)
print()

graph_config = GraphConfig(
    nodes=["chatbot_node"]
)

export_jsons_to_csv(exp, graph_config)

# ANALIZA
print()
event_log = load_event_log(exp)
print_analysis(event_log)
print()
generate_reports(event_log, exp)
print()
generate_visualizations(event_log, graph, exp)