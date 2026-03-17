# Agent Task 1

Simple CLI agent that communicates with an LLM and returns JSON.

- **LLM Provider**: OpenRouter (OpenAI-compatible)
- **Model**: mistralai/mistral-7b-instruct:free (configurable via .env)
- **Output Format**: Strict JSON `{"answer": "...", "tool_calls": []}`
- **Execution**: `uv run agent.py "question"`
