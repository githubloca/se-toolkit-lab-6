import os
import sys
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
import time

# Исправляем кодировку для Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Загружаем секреты
load_dotenv(".env.agent.secret")
load_dotenv(".env.docker.secret")

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_BASE = os.getenv("LLM_API_BASE")
LLM_MODEL = os.getenv("LLM_MODEL")
LMS_API_KEY = os.getenv("LMS_API_KEY")
AGENT_API_BASE_URL = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")

# --- Вспомогательные функции (Tools) ---

def list_files(path: str = "."):
    try:
        files = []
        for root, _, filenames in os.walk(path):
            for name in filenames:
                rel_path = os.path.relpath(os.path.join(root, name), ".")
                files.append(rel_path.replace("\\", "/"))
        return json.dumps(files[:100])
    except Exception as e:
        return f"Error listing files: {e}"

def read_file(path: str) -> str:
    if not path: return "Error: No path"
    p = str(path).strip().replace("'", "").replace('"', "").lstrip("./")
    options = [p, f"wiki/{p}", f"src/{p}", f"backend/{p}", p.split('/')[-1]]
    for opt in options:
        if os.path.exists(opt) and os.path.isfile(opt):
            try:
                with open(opt, "r", encoding="utf-8") as f:
                    return f.read()
            except: continue
    return f"Error: File '{path}' not found."

def query_api(method: str, path: str, body: str = None, include_auth: bool = None) -> str:
    auth_enabled = (include_auth is not False)
    url = f"{AGENT_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    
    if auth_enabled:
        headers["Authorization"] = f"Bearer {LMS_API_KEY}"
    
    print(f"\n[DEBUG] Request to: {path} | Auth Enabled: {auth_enabled}", file=sys.stderr)

    try:
        resp = requests.request(
            method=method.upper(), url=url,
            headers=headers,
            data=body.encode('utf-8') if body else None, 
            timeout=10
        )
        return json.dumps({"status": resp.status_code, "body": resp.text}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files to find wiki or source code.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "default": "."}}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file content (wiki or code).",
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
            "description": "Call API. MUST set include_auth=false to test access without a token.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {"type": "string"},
                    "path": {"type": "string"},
                    "body": {"type": "string"},
                    "include_auth": {"type": "boolean"} 
                },
                "required": ["method", "path", "include_auth"]
            }
        }
    }
]

def run_agent(query):
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE)
    messages = [
        {
            "role": "system", 
            "content": (
                "You are a Senior Backend Developer. To solve endpoint crashes:\n"
                "1. DO NOT guess labs. Use 'list_files' to find the router (check backend/app/api/).\n"
                "2. Use 'read_file' to examine the logic. Look for sorting or access to missing keys.\n"
                "3. Once you see the bug, call 'query_api' ONCE to confirm.\n"
                "4. Your final answer MUST include the 'source' path to the file with the bug.\n"
                "5. BE FAST. Use max 5 steps."
            )
        },
        {"role": "user", "content": query}
    ]
    
    history = []
    source_file = None
    used_calls = set()

    for _ in range(15):
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL, 
                messages=messages, 
                tools=tools,
                timeout=40
            )
        except Exception as e:
            if "429" in str(e):
                time.sleep(15)
                continue 
            return {"answer": f"LLM Error: {e}", "source": source_file, "tool_calls": history}
        
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return {
                "answer": (msg.content or "").strip(), 
                "source": source_file, 
                "tool_calls": history
            }
        
        for tc in msg.tool_calls:
            name = tc.function.name
            args_str = tc.function.arguments
            
            try:
                args = json.loads(args_str)
            except:
                args = {}

            if name == "list_files":
                res = list_files(args.get("path", "."))
            elif name == "read_file":
                path_val = args.get("path")
                res = read_file(path_val)
                if res and not res.startswith("Error"):
                    source_file = path_val 
            elif name == "query_api":
                res = query_api(args.get("method", "GET"), args.get("path", "/"), args.get("body"), args.get("include_auth"))
            else:
                res = "Unknown tool"

            history.append({"tool": name, "args": args, "result": res})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(res)})

    return {"answer": "Limit reached", "source": source_file, "tool_calls": history}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(run_agent(sys.argv[1]), ensure_ascii=False))