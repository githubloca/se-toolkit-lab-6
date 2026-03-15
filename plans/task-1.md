# Task 1: Call an LLM from Code - Implementation Plan

## LLM Provider
- **Provider:** OpenRouter (или Qwen Code API)
- **Model:** meta-llama/llama-3.3-70b-instruct:free (или qwen3-coder-plus)
- **API Base:** https://openrouter.ai/api/v1 (или http://<VM-IP>:4000/v1)

## Architecture
1. Read LLM credentials from `.env.agent.secret`
2. Parse question from command-line argument
3. Send POST request to LLM API (/v1/chat/completions)
4. Parse response and extract answer
5. Output JSON with `answer` and `tool_calls` fields

## Implementation Details
- Use `python-dotenv` to load environment variables
- Use `requests` for API calls
- Output: single JSON line to stdout, logs to stderr

## Testing
- 1 regression test: run agent.py, parse stdout, verify JSON structure
