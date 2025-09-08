# AI Summarization Agent
This project contains approach on how to build an ReAct AI agent using LangGraph. please find the flow below
```mermaid
flowchart TD
    A[User Input] --> B[Web Search Tool]
    B --> C[Summarize Learnings]
    C --> D[Human Review]

    D -->|Reject| B
    D -->|Accept| E[Send to Gmail MCP]

    E --> F[Send Email]
    F --> G[Email Sent ✅]
```

### Prerequisites of the project
* copy the .env.sample file and create .env file with the values
* gmail tool setup,
  * create client auth credentials
  * run gmail_auth.py (this will generate the token.json file which will be used to send email)

### Following if the flow of the graph
![LangGraph Flow](graph.png)

### To run the project
```commandline
make run
```

