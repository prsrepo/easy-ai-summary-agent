import dotenv

from fastapi import FastAPI
from langgraph.types import Command

from react_hitl_agent.db import checkpointer
from react_hitl_agent.graph import get_summarization_graph

dotenv.load_dotenv()

app = FastAPI()


@app.post("/query")
async def query(thread_id: str, user_query: str):
    graph = get_summarization_graph(checkpointer)
    result = graph.invoke(
        {"user_query": user_query}, config={"configurable": {"thread_id": thread_id}}
    )
    # If paused at approval
    if "__interrupt__" in result:
        interrupt_info = result["__interrupt__"][0].value
        return {
            "status": "paused",
            "thread_id": thread_id,
            "pending_summary": interrupt_info["pending_summary"],
        }

    # Finished without pause
    return {"status": "done", "result": result}


@app.post("/resume")
async def resume(thread_id: str, is_approved: bool):
    graph = get_summarization_graph(checkpointer)
    result = graph.invoke(
        Command(resume=True, update={"is_approved": is_approved}),
        config={"configurable": {"thread_id": thread_id}},
    )

    if "__interrupt__" in result:
        interrupt_info = result["__interrupt__"][0].value
        return {
            "status": "paused",
            "thread_id": thread_id,
            "pending_summary": interrupt_info["pending_summary"],
        }

    return {"status": "done", "result": result}
