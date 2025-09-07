from langgraph.graph import StateGraph, START, END
from typing import TypedDict



class State(TypedDict):
    user_query: str
    search_data: str
    summary: str
    is_approved: bool
    email: str


def collect_search_data(state: TypedDict) -> dict:
    return {"search_data": "Foo bar"}


def summarize_search_data(state: TypedDict) -> dict:
    return {"summary": "Foo bar"}


def wait_for_approval(state: TypedDict) -> dict:
    return {"is_approved": True}


def send_summary_email(state: TypedDict) -> dict:
    return {"email": "Foo bar"}



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
        lambda state: "approved" if state["is_approved"] else "rejected",
        {
            "approved": "send_summary_email",
            "rejected": "summarize_search_data"
        }
    )

    flow.add_edge("wait_for_approval", "send_summary_email")
    flow.set_finish_point("send_summary_email")
    # flow.add_conditional_edges()
    return flow

if __name__ == '__main__':
    graph = get_graph().compile()
    graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
    result = graph.invoke({
        "user_query": "whats the climate in bangalore?"
    })
    print(result)

