```mermaid
flowchart TD
    A[User Input] --> B[Web Search Tool]
    B --> C[Summarize Learnings]
    C --> D[Human Review]
    
    D -->|Reject| B
    D -->|Accept| E[MCP Server]
    
    E --> F{Post Summary}
    F --> G[Gmail]
    F --> H[Slack]
```