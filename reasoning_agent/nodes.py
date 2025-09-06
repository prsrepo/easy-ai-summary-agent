from http.client import responses

from dotenv import load_dotenv
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

from reasoning_agent.react import llm, tools



load_dotenv()


SYSTEM_MESSAGE = """
You are a helpful assistant that can use tools to answer questions
"""


def run_agent_reasoning(state: MessagesState):
    response = llm.invoke([
        {"role": "system",
         "content": SYSTEM_MESSAGE},
        *state["messages"]
    ])
    return {"messages": [response]}


tool_node = ToolNode(tools)

