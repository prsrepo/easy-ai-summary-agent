import logging
import os
from typing import TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_tavily import TavilySearch
from langgraph.types import Command, interrupt

from react_hitl_agent.utils import send_email_tool

LOGGER = logging.getLogger(__name__)


class State(TypedDict):
    user_query: str
    search_data: str
    summary: str
    is_approved: bool
    email: str


def collect_search_data(state: TypedDict) -> dict:
    LOGGER.info("Collecting search data")
    search_tool = TavilySearch(max_results=3)
    results = search_tool.invoke(state["user_query"])
    web_result_content = "\n".join([r["content"] for r in results.get("results", [])])
    return {"search_data": web_result_content}


def summarize_search_data(state: TypedDict) -> dict:
    LOGGER.info("Summerizing search data")
    llm = init_chat_model("openai:gpt-4.1")

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

    user_msg = HumanMessage(
        content=user_prompt.format(
            user_input=state["user_query"], web_results=state["search_data"]
        )
    )
    response = llm.invoke([sys_msg, user_msg])
    return {"summary": response.content}


def wait_for_approval(state: TypedDict) -> dict:
    LOGGER.info("Waiting for approval task")
    interrupt({"pending_summary": state.get("summary", "")})
    return {"is_approved": state["is_approved"]}


def send_summary_email(state: TypedDict) -> dict:
    LOGGER.info("Sending summary email")
    send_email_tool(
        os.environ.get("GMAIL"),
        f"Summary for user query: {state['user_query']}",
        state["summary"],
    )
    return {"email": "Sent"}
