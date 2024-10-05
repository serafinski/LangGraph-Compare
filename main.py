import sqlite3
import sys

from dotenv import load_dotenv
from typing import Annotated

from langgraph.checkpoint.sqlite import SqliteSaver
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.globals import set_debug

# Import metody do zapisywania do pliku i wypisywanie output'u
from tee import Tee

# Debug mode - LangChain
set_debug(True)

# Otwarcie pliku do którego będziemy zapisywać
log_file = open('langchain_debug_logs.log', 'w')

# Użycie metody działającej ala tee na linux'ie
sys.stdout = Tee(sys.stdout, log_file)

# Inicjalizacja .env
load_dotenv()

conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

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

graph_builder.add_edge(START, "chatbot_node_test")
graph_builder.add_edge("chatbot_node", END)

graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}
user_input = {"messages": [("user", "Hi")]}

# Wywołanie grafu
for event in graph.stream(user_input, config, stream_mode="debug"):
    pass

# Przywrócenie stdout do oryginalnego stanu
sys.stdout = sys.__stdout__

# Zamknięcie pliku
log_file.close()
