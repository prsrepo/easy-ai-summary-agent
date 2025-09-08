import sqlite3, dotenv

from fastapi import FastAPI
from langgraph.types import Command, interrupt
from langgraph.checkpoint.sqlite import SqliteSaver

from react_hitl_agent.graph import get_graph

dotenv.load_dotenv()

app = FastAPI()


conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
# Simple in-memory store for checkpoints (use Redis/DB in production)
checkpointer = SqliteSaver(conn)

exec_graph = get_graph().compile(checkpointer=checkpointer)


@app.post("/query")
async def query(thread_id:str, user_query: str):
    result = exec_graph.invoke(
        {"user_query": user_query},
        config={"configurable": {"thread_id": thread_id}}
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
    result = exec_graph.invoke(
        Command(resume=True, update={"is_approved": is_approved}),
        config={"configurable": {"thread_id": thread_id}}
    )

    if "__interrupt__" in result:
        # Graph paused again (e.g., rejected and back to summarize)
        interrupt_info = result["__interrupt__"][0].value
        return {
            "status": "paused",
            "thread_id": thread_id,
            "pending_summary": interrupt_info["pending_summary"],
        }

    return {"status": "done", "result": result}
