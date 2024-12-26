# LangGraph Log Parser

# Documentation
Documentation is available at: https://serafinski.github.io/LangGraph-Log-Parser/

# Purpose
This Python package facilitates the parsing of run logs generated by [LangGraph](https://langchain-ai.github.io/langgraph/). During execution, logs are stored in an SQLite database in an encoded format _(using msgpack)_. These logs are then decoded and exported to a `json` format. Subsequently, the `json` files are transformed into `csv` files for further analysis.

Once in `csv` format, the data can be analyzed using methods from the [py4pm](https://processintelligence.solutions/static/api/2.7.11/index.html) library. These methods calculate specific statistics related to the multi-agent infrastructure's performance and enable visualizations of the process behavior and execution flow.

This pipeline provides a streamlined approach for extracting, transforming, and analyzing logs, offering valuable insights into multi-agent systems.

# Installation
This package requires Python 3.9 or higher. [Check below for more information on creating environment.](#environment-setup)

If you would like to develop this package, use poetry with Python 3.10 - since 3.10 is the needed minimum by Sphinx.
Install needed dependencies with:
```dotenv
poetry install --with dev,test,docs
```
## Prerequisites
This package requires Graphviz to be installed on your system.

### Windows
Download the Graphviz installer from the [Graphviz website](https://graphviz.org/download/).

### macOS
Install Graphviz using Homebrew:
```dotenv
brew install graphviz
```

### Linux
For Debian, Ubuntu, use the following command:
```dotenv
sudo apt-get install graphviz
```
<br>

For Fedora, Rocky Linux, RHEL or CentOS use the following command:
```dotenv
sudo dnf install graphviz
```

## Environment setup
To create virtual environment (using conda), use the following commands:
```dotenv
conda create -n langgraph_log_parser python=3.9
conda activate langgraph_log_parser
pip install langgraph_log_parser
```
# Basic Example
This example is based on the [Building a Basic Chatbot](https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot) from LangGraph documentation.

It will require You to install the following packages _(besides `langgraph_log_parser`)_:
```dotenv
pip install python-dotenv langchain-openai
```
**Example:**

```python
from dotenv import load_dotenv
from typing import Annotated

from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langgraph_log_parser import *

exp = create_experiment("main")
memory = exp.memory

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-4o-mini")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot_node", chatbot)

graph_builder.add_edge(START, "chatbot_node")
graph_builder.add_edge("chatbot_node", END)

graph = graph_builder.compile(checkpointer=memory)

run_multiple_iterations(graph, 1, 5, {"messages": [("user", "Tell me a joke")]})

export_sqlite_to_jsons(exp.database, exp.json_dir)

graph_config = GraphConfig(
    nodes=["chatbot_node"]
)

export_jsons_to_csv(exp.json_dir, exp.get_csv_path(), graph_config)

print()
event_log = load_event_log(exp.get_csv_path())
print_analysis(event_log)

generate_reports(event_log, exp.reports_dir)

generate_visualizations(event_log, graph, exp.img_dir)
```