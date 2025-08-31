from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START

from agent.models import State
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

load_dotenv()

llm = init_chat_model('openai:gpt-4.1')

tool = TavilySearch(max_results=2)
tools = [tool]

llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state['messages'])]}


graph_builder = StateGraph(State)


graph_builder.add_node('chatbot', chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, 'chatbot')

# memory = InMemorySaver()
# graph = graph_builder.compile(checkpointer=memory)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):

    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
                            #   {"configurable": {"thread_id": "1"}}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
