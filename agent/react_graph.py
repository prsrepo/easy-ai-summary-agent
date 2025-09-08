from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain_tavily.tavily_search import TavilySearch
from langgraph.types import interrupt
from langgraph_runtime_inmem.checkpoint import InMemorySaver
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()


class State(TypedDict):
    user_msg: str | None
    summary: str | None


def human_approval(state: State):
    return interrupt(
        {
            "question": "Do you accept the summary?",
            "llm_output": state["summary"],
        }
    )


llm = init_chat_model("openai:gpt-4.1")
search_tool = TavilySearch(max_results=3)

sys_msg = SystemMessage(
    content="""
You are a helpful assistant tasked with summarizing websearch results based on the user search query.
Summarize the results in a clear, readable way.
"""
)

user_prompt = """
Given the following web input:
{user_input}

These are the web results:
{web_results}
"""


def assistant(state: State):
    user_message = state["user_msg"]


    results = search_tool.invoke(user_message)
    web_result_content = "\n".join(
        [r["content"] for r in results.get("results", [])]
    )
    user_msg = HumanMessage(
        content=user_prompt.format(
            user_input=user_message, web_results=web_result_content
        )
    )
    response = llm.invoke([sys_msg, user_msg])
    return {"summary": response.content}


def print_summary(state: State):
    print("\n=== FINAL SUMMARY ===\n")
    print(state["summary"])
    print("\n=====================\n")


# Build graph
graph_builder = StateGraph(State)

graph_builder.add_node("assistant", assistant)
graph_builder.add_node("human_approval", human_approval)
graph_builder.add_node("print_summary", print_summary)

graph_builder.add_edge(START, "assistant")

# conditional routing after human approval
graph_builder.add_conditional_edges(
    "human_approval",
    lambda user_input: "print_summary" if user_input else "assistant",
)

graph_builder.add_edge("print_summary", END)

checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)


# --- CLI Runner ---
def run_cli():
    query = input("Enter your search query: ")
    state = {"user_msg": query}
    config = {"configurable": {"thread_id": "cli-session-1"}}

    # --- initial run ---
    for event in graph.stream(state, config=config):
        for node, value in event.items():
            print(f"Step: {node}")
            if node == "assistant":
                print("\n[Assistant produced summary candidate]\n")
            if node == "human_approval":
                # This value is the interrupt payload
                print("\n--- SUMMARY DRAFT ---\n")
                print(value["llm_output"])
                print("\n---------------------\n")

                # ask human
                while True:
                    choice = input("Do you approve? (y/n): ").strip().lower()
                    if choice in ("y", "n"):
                        break

                approved = choice == "y"

                # --- resume run ---
                for resumed in graph.resume(approved, name="human_approval", config=config):
                    for rnode, rvalue in resumed.items():
                        print(f"Resumed at: {rnode}")



if __name__ == "__main__":
    run_cli()
