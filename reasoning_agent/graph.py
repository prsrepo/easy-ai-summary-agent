from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState, StateGraph, END

from reasoning_agent.nodes import run_agent_reasoning, tool_node


load_dotenv()

AGENT_REASON="agent_reason"
ACT="act"
LAST=-1

def should_continue(state: MessagesState) -> str:
    if not state["messages"][LAST].tool_calls:
        return END
    return ACT

def get_graph():
    flow = StateGraph(MessagesState)
    flow.add_node(AGENT_REASON, run_agent_reasoning)
    flow.add_node(ACT, tool_node)

    flow.set_entry_point(AGENT_REASON)


    flow.add_conditional_edges(AGENT_REASON, should_continue, {
        END:END,
        ACT:ACT
    })
    flow.add_edge(ACT, AGENT_REASON)
    return flow
