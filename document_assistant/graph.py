from langgraph.graph import StateGraph
from typing import TypedDict


class State(TypedDict):
    count: int


def add_one(state: State):
    state['count'] += 1
    return state


graph = StateGraph(State)
graph.add_node("increment", add_one)
graph.set_entry_point("increment")
graph.set_finish_point("increment")


if __name__ == '__main__':
    app = graph.compile()
    # app.get_graph().draw_mermaid_png(output_file_path="flow.png")
    result = app.invoke({"count": 1})
    print(result)
