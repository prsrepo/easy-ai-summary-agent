import typer
# from agent.workflow import build_graph

app = typer.Typer(help="AI Summary Agent CLI")

@app.command()
def query(question: str):
    """
    Run the AI summary agent with a query.
    Example:
      python main.py query "Hello there!"
    """
    # graph = build_graph()
    # result = graph.invoke({"question": question})
    typer.echo("\n✅ Final Result Sent:\n" + question)
    # typer.echo(result["final_summary"])

if __name__ == "__main__":
    app()
