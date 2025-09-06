from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langgraph.graph import StateGraph, END
import smtplib
from email.mime.text import MIMEText

# Shared LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Tavily search tool
search_tool = TavilySearch(max_results=3)

# Summarization chain
summary_prompt = ChatPromptTemplate.from_template(
    """
    Summarize the following web results into a concise, factual summary:
    {results}
    """
)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)

# Email sender (SMTP as placeholder)
def send_email_via_gmail(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "your_email@gmail.com"
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your_email@gmail.com", "your_app_password")
        server.send_message(msg)

# --- Define LangGraph workflow ---
class WorkflowState(dict):
    pass

# Nodes
def search_node(state: WorkflowState):
    query = state["query"]
    results = search_tool.run(query)
    state["results"] = results
    return state

def summarize_node(state: WorkflowState):
    results = state["results"]
    summary = summary_chain.run({"results": results})
    state["summary"] = summary
    return state

def approval_node(state: WorkflowState):
    print("\n--- Summary ---")
    print(state["summary"])
    feedback = input("Approve this summary? (yes/no): ").strip().lower()
    state["approved"] = feedback == "yes"
    return state

def email_node(state: WorkflowState):
    send_email_via_gmail(
        state["recipient"], f"Summary for: {state['query']}", state["summary"]
    )
    print("✅ Email sent successfully!")
    return state

# --- Build Graph ---
graph = StateGraph(WorkflowState)

# Add nodes
graph.add_node("search", search_node)
graph.add_node("summarize", summarize_node)
graph.add_node("approval", approval_node)
graph.add_node("email", email_node)

# Edges
graph.add_edge("search", "summarize")
graph.add_edge("summarize", "approval")

# Conditional edge from approval
def approval_condition(state: WorkflowState):
    if state["approved"]:
        return "approved"
    return "retry"

graph.add_conditional_edges(
    "approval",
    approval_condition,
    {
        "approved": "email",   # go to email if approved
        "retry": "summarize"   # loop back to summarization
    }
)

graph.add_edge("email", END)

# Compile workflow
workflow = graph.compile()

if __name__ == "__main__":
    query = input("Enter your query: ")
    recipient_email = input("Enter recipient email: ")

    initial_state = {"query": query, "recipient": recipient_email}
    workflow.invoke(initial_state)
