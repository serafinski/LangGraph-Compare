from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

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
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

user_input = "Why is the sky blue?"
for event in graph.stream({"messages": ("user", user_input)}):
    for value in event.values():
        print("Assistant:", value["messages"][-1].content)
