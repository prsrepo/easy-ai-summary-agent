from langgraph.graph import StateGraph, START, END
from react_hitl_agent.nodes import State, collect_search_data, summarize_search_data, wait_for_approval, send_summary_email


def get_graph() -> StateGraph:
    flow = StateGraph(State)

    flow.add_node("collect_search_data", collect_search_data)
    flow.add_node("summarize_search_data", summarize_search_data)
    flow.add_node("wait_for_approval", wait_for_approval)
    flow.add_node("send_summary_email", send_summary_email)

    flow.set_entry_point("collect_search_data")
    flow.add_edge("collect_search_data", "summarize_search_data")
    flow.add_edge("summarize_search_data", "wait_for_approval")

    flow.add_conditional_edges(
        "wait_for_approval",
        lambda state: "approved" if state.get("is_approved") else "rejected",
        {
            "approved": "send_summary_email",
            "rejected": "summarize_search_data"
        }
    )

    # flow.add_edge("wait_for_approval", "send_summary_email")
    flow.set_finish_point("send_summary_email")
    # flow.add_conditional_edges()
    return flow
