**Goal**: Create a CLI agent that communicates with an LLM via OpenRouter and returns a structured JSON response.

**Architecture**:
1. **Environment**: Use `.env.agent.secret` to store `LLM_API_KEY`, `LLM_API_BASE`, and `LLM_MODEL`.
2. **Library**: Use the `openai` Python library (standard for OpenAI-compatible APIs like OpenRouter).
3. **Input**: Question passed as the first command-line argument (`sys.argv[1]`).
4. **Processing**:
   - Load environment variables.
   - Initialize the OpenAI client.
   - Send a system prompt to the LLM to ensure it only returns the answer text.
5. **Output**:
   - Success: A single JSON line to `stdout`: `{"answer": "...", "tool_calls": []}`.
   - Debug/Errors: All non-JSON output goes to `stderr`.

**Selected Stack**:
- Provider: OpenRouter
- Model: `qwen/qwen-2.5-72b-instruct:free` (as a fallback `google/gemini-2.0-flash-lite-preview-02-05:free`)
