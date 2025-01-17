import datetime
import json

from langchain_core.messages import ToolMessage
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool

from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages

from typing import Annotated
from typing_extensions import TypedDict

from pydantic import ValidationError, BaseModel, Field

from langchain_experimental.utilities import PythonREPL

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether

from dotenv import load_dotenv

from langgraph_compare import *

exp = create_experiment("code_10", "check")
memory = exp.memory

load_dotenv()

# TOOLS
# llm = ChatOpenAI(model="gpt-4o-mini")
# llm = ChatGroq(model="llama-3.1-8b-instant")
llm = ChatTogether(model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
repl = PythonREPL()


# INITIAL RESPONDER
class CodeReflection(BaseModel):
    missing: str = Field(description="What is missing from the implementation")
    superfluous: str = Field(description="What is unnecessary in the implementation")


class GenerateCode(BaseModel):
    """Generate initial code implementation with analysis and reflection."""

    answer: str = Field(description="~Code implementation with explanation")
    reflection: CodeReflection = Field(description="Reflection on the implementation")
    code_samples: list[str] = Field(
        description="1-3 code samples to test and verify the implementation"
    )


class ReviseCode(BaseModel):
    """Revise code implementation based on previous reflection."""

    answer: str = Field(description="~250 word revised implementation with explanation")
    reflection: CodeReflection = Field(description="New reflection on the implementation")
    code_samples: list[str] = Field(
        description="1-3 code samples to test the revised implementation"
    )


class ResponderWithRetries:
    def __init__(self, runnable, validator):
        self.runnable = runnable
        self.validator = validator

    def respond(self, state: dict):
        response = []
        for attempt in range(3):
            response = self.runnable.invoke(
                {"messages": state["messages"]}, {"tags": [f"attempt:{attempt}"]}
            )
            try:
                self.validator.invoke(response)
                return {"messages": response}
            except ValidationError as e:
                # Create new messages list with error response
                new_messages = state["messages"] + [
                    response,
                    ToolMessage(
                        content=f"{repr(e)}\n\nPay close attention to the function schema.\n\n"
                                + json.dumps(self.validator.model_json_schema())
                                + " Respond by fixing all validation errors.",
                        tool_call_id=response.tool_calls[0]["id"],
                    ),
                ]
                state = {"messages": new_messages}
        return {"messages": response}


actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are expert software engineer.
            Current time: {time}

            1. {first_instruction}
            2. Reflect and critique your implementation. Be severe to maximize improvement.
            3. Provide code samples to test and verify your implementation.""",
        ),
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "\n\n<system>Review the code request and actions taken. Respond using the {function_name} function.</system>",
        ),
    ]
).partial(
    time=lambda: datetime.datetime.now().isoformat(),
)

initial_chain = (
        actor_prompt_template.partial(
            first_instruction="Provide a detailed code implementation with explanation.",
            function_name=GenerateCode.__name__,
        ) | llm.bind_tools(tools=[GenerateCode]))

validator = PydanticToolsParser(tools=[GenerateCode])

first_responder = ResponderWithRetries(
    runnable=initial_chain, validator=validator
)

# REVISION
revise_instructions = """Revise your code implementation using the execution results.
    - Use the previous critique to improve your implementation
    - Make sure the code handles edge cases
    - Focus on improving efficiency and readability
    - Keep the explanation clear and concise within 250 words"""

revision_chain = (
        actor_prompt_template.partial(
            first_instruction=revise_instructions,
            function_name=ReviseCode.__name__,
        )
        | llm.bind_tools(tools=[ReviseCode])
)
revision_validator = PydanticToolsParser(tools=[ReviseCode])

revisor = ResponderWithRetries(
    runnable=revision_chain, validator=revision_validator
)


# TOOL NODE
def execute_code(code: str) -> str:
    """Execute code in REPL and return output."""
    try:
        return repl.run(code)
    except Exception as e:
        return f"Error: {str(e)}"


def run_code_samples(request: GenerateCode | ReviseCode, **kwargs):
    """Run the code samples and return results."""
    results = []
    for code in request.code_samples:
        output = execute_code(code)
        results.append({
            "code": code,
            "output": output
        })
    return results


tool_node = ToolNode(
    [
        StructuredTool.from_function(run_code_samples, name=GenerateCode.__name__),
        StructuredTool.from_function(run_code_samples, name=ReviseCode.__name__),
    ]
)


# CONSTRUCT GRAPH
class State(TypedDict):
    messages: Annotated[list, add_messages]


MAX_ITERATIONS = 5
builder = StateGraph(State)

builder.add_node("draft", first_responder.respond)
builder.add_node("execute_tools", tool_node)
builder.add_node("revise", revisor.respond)

# Add edges
builder.add_edge(START, "draft")
builder.add_edge("draft", "execute_tools")
builder.add_edge("execute_tools", "revise")


def get_num_iterations(state: list):
    """Count the number of iterations in the current state."""
    i = 0
    for m in state[::-1]:
        if m.type not in {"tool", "ai"}:
            break
        i += 1
    return i


def event_loop(state: dict):
    num_iterations = get_num_iterations(state["messages"])
    if num_iterations > MAX_ITERATIONS:
        return END
    return "execute_tools"


builder.add_conditional_edges("revise", event_loop, ["execute_tools", END])
graph = builder.compile(checkpointer=memory)

user_input = {"messages": [("user",
                            "Given an array of integers, find the length of the longest subsequence such that all elements of the subsequence are sorted in increasing order.")]}

print()
run_multiple_iterations(graph, 1, 10, user_input)
print()

graph_config = GraphConfig(
    nodes=["draft", "execute_tools", "revise"]
)

prepare_data(exp, graph_config)

# ANALYSIS
print()
event_log = load_event_log(exp)
print_analysis(event_log)
print()

generate_artifacts(event_log, graph, exp)