import dotenv
from langchain_core.messages import HumanMessage

from reasoning_agent.graph import get_graph

dotenv.load_dotenv()


if __name__ == '__main__':
    print("Starting the flow of execution")
    flow = get_graph()
    app = flow.compile()
    # app.get_graph().draw_mermaid_png(output_file_path="flow.png")
    res = app.invoke({
        "messages": [HumanMessage(
            content="What is the weather like in Bangalore? list it and then triple it"
        )]
    })
    print(res["messages"][-1].content)
