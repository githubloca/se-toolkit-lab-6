
## Task 3: The System Agent

### New Tool: query_api

The agent now has a `query_api` tool to communicate with the deployed backend.

**Authentication:**
- Uses `LMS_API_KEY` from `.env.docker.secret` (separate from LLM key!)
- Header format: `Authorization: Bearer {LMS_API_KEY}`
- Base URL from `AGENT_API_BASE_URL` (default: `http://localhost:42002`)

**Parameters:**
- `method`: HTTP method (GET, POST, PUT, DELETE)
- `path`: API endpoint (e.g., `/items/`, `/analytics/completion-rate?lab=lab-99`)
- `body`: Optional JSON for POST/PUT requests

**Returns:** JSON string with `status_code` and `body`.

### Tool Selection Logic

| Question Type | Tool | Example |
|--------------|------|---------|
| Live data (counts, scores) | query_api | "How many items in database?" |
| Code inspection | read_file | "What framework does backend use?" |
| Documentation | Wiki | "What are branch protection rules?" |

### Lessons Learned

1. **Model selection matters**: Free models on OpenRouter vary in stability. `microsoft/phi-4:free` worked best for function calling.

2. **NoneType handling**: LLM can return `content: null` when making tool calls. Fixed with `msg.content or ""`.

3. **Two API keys**: Critical to keep `LMS_API_KEY` (backend) separate from `LLM_API_KEY` (LLM provider).

4. **Tool descriptions drive behavior**: Clear, keyword-rich descriptions help the LLM choose the right tool.

### Final Score

| Benchmark | Score |
|-----------|-------|
| Local (`run_eval.py`) | 10/10 |
| Autochecker (hidden) | Pending |