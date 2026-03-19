import os
import sys
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные из файлов, как того требует задание
load_dotenv(".env.agent.secret")
load_dotenv(".env.docker.secret")

# LLM Config
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_BASE = os.getenv("LLM_API_BASE")
LLM_MODEL = os.getenv("LLM_MODEL")

# API Config
LMS_API_KEY = os.getenv("LMS_API_KEY")
AGENT_API_BASE_URL = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")

# --- Инструменты ---

def read_file(path: str):
    """Читает файлы проекта (wiki или исходный код)."""
    try:
        # Убираем кавычки, если модель их добавила
        clean_path = path.strip().replace("'", "").replace('"', "")
        with open(clean_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

def query_api(method: str, path: str, body: str = None):
    """Вызывает API бэкенда для получения живых данных."""
    url = f"{AGENT_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    headers = {
        "X-API-Key": LMS_API_KEY, # Авторизация строго по ТЗ
        "Content-Type": "application/json"
    }
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            data=body.encode('utf-8') if body else None,
            timeout=15
        )
        return json.dumps({"status_code": response.status_code, "body": response.text}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status_code": 500, "body": str(e)})

# --- Схемы для LLM ---

tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read project files, wiki, or source code.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_api",
            "description": "Call the system API for live facts (item counts, status, framework).",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["GET", "POST"]},
                    "path": {"type": "string", "description": "e.g. '/items/' or '/analytics/'"},
                    "body": {"type": "string", "description": "Optional JSON string"}
                },
                "required": ["method", "path"]
            }
        }
    }
]

# --- Агентический цикл ---

def run_agent(question):
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE)
    
    messages = [
        {
            "role": "system", 
            "content": (
                "You are a System Agent. For documentation/rules, use `read_file`. "
                "For live system data (counts, scores, ports, framework), use `query_api`. "
                "If API fails, use `read_file` to find the bug in the code."
            )
        },
        {"role": "user", "content": question}
    ]
    
    all_tool_calls = []
    source_file = None

    for _ in range(10):
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        
        if not msg.tool_calls:
            # Финальный ответ
            return {
                "answer": (msg.content or "").strip(),
                "source": source_file, # Путь к файлу, если читали Wiki
                "tool_calls": all_tool_calls
            }

        messages.append(msg)
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            
            if name == "read_file":
                source_file = args.get("path")
                result = read_file(source_file)
            elif name == "query_api":
                result = query_api(**args)
            else:
                result = "Error: Unknown tool"

            all_tool_calls.append({"tool": name, "args": args, "result": result})
            
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    return {"answer": "Timeout", "source": source_file, "tool_calls": all_tool_calls}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(run_agent(sys.argv[1]), ensure_ascii=False))