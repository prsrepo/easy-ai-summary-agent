from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START

from agent.models import State
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

llm = init_chat_model('openai:gpt-4.1')

tool = TavilySearch(max_results=2)
tools = [tool]

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state['messages'])]}


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()