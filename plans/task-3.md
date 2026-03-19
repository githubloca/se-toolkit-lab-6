# Plan for Task 3: The System Agent

## Implementation Plan

### 1. Tool Schema (`query_api`)
- **Name:** `query_api`
- **Parameters:**
  - `method` (string, required): HTTP method (GET, POST, PUT, DELETE)
  - `path` (string, required): API endpoint path (e.g., `/items/`, `/analytics/completion-rate`)
  - `body` (string, optional): JSON body for POST/PUT requests
- **Returns:** JSON string with `status_code` and `body`

### 2. Authentication
- Read `LMS_API_KEY` from environment variable (`.env.docker.secret`)
- Use in header: `Authorization: Bearer {LMS_API_KEY}`
- Read `AGENT_API_BASE_URL` from env (default: `http://localhost:42002`)

### 3. System Prompt Update
- Add clear rules for when to use each tool:
  - Wiki tools → project documentation and guidelines
  - `read_file` → source code inspection, bug diagnosis
  - `query_api` → live data (counts, scores), system facts (ports, framework via API)

### 4. Environment Variables
- All config from env vars, no hardcoded values
- Separate keys: `LLM_API_KEY` (`.env.agent.secret`) vs `LMS_API_KEY` (`.env.docker.secret`)

## Benchmark Diagnosis

| Run | Score | First Failures | Fix Applied |
|-----|-------|----------------|-------------|
| 1st | 3/10 | • "How many items..." → agent didn't call `query_api`<br>• "What port..." → 401 auth error<br>• "/analytics/completion-rate" → wrong path format | • Improved tool description: added "item counts, scores" keywords<br>• Fixed auth header: `Authorization: Bearer {LMS_API_KEY}`<br>• Added query param example: `?lab=lab-99` |
| 2nd | 7/10 | • "Explain request lifecycle" → agent gave generic answer<br>• "Bug in validation logic" → read wrong file | • Updated system prompt: "For code bugs, use `read_file` on `src/` paths"<br>• Added rule: "If API returns error, read source to diagnose" |
| Final | 10/10 | None | - |

## Iteration Strategy
1. Run `uv run run_eval.py`
2. If agent doesn't call tool → improve tool description in schema
3. If auth fails (401/403) → check header format and env var
4. If timeout → reduce max iterations
5. Repeat until 10/10