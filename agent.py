#!/usr/bin/env python3
"""Task 1: Call an LLM from Code - Simple CLI agent."""

import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env.agent.secret
env_path = Path(__file__).parent / ".env.agent.secret"
load_dotenv(env_path)

LLM_API_BASE = os.getenv("LLM_API_BASE")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3-coder-plus")


def call_llm(question: str) -> dict:
    """Send question to LLM and get response."""
    import requests
    
    url = f"{LLM_API_BASE}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        
        return {"answer": answer, "tool_calls": []}
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return {"answer": f"Error: {str(e)}", "tool_calls": []}


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    result = call_llm(question)
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
