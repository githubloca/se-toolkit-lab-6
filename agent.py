import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем секреты
load_dotenv(".env.agent.secret")

# --- Вспомогательные функции (Tools) ---

def is_safe_path(path):
    """Проверка, что агент не выходит за пределы текущей папки."""
    root = os.path.abspath(os.getcwd())
    target = os.path.abspath(os.path.join(root, path))
    return os.path.commonpath([root]) == os.path.commonpath([root, target])

def list_files(path="."):
    if not is_safe_path(path): return "Error: Access denied."
    try:
        return "\n".join(os.listdir(path))
    except Exception as e: return str(e)

def read_file(path):
    if not is_safe_path(path): return "Error: Access denied."
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e: return str(e)

# --- Описание инструментов для LLM ---

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory to discover wiki content.",
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
            "name": "read_file",
            "description": "Read the content of a file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    }
]

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    user_query = sys.argv[1]
    client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url=os.getenv("LLM_API_BASE"))
    model = os.getenv("LLM_MODEL")

    messages = [
        {"role": "system", "content": "You are a wiki assistant. Use list_files to see what is in 'wiki/' and read_file to answer. Always mention the source file path in your answer."},
        {"role": "user", "content": user_query}
    ]
    
    all_tool_calls_result = [] # Для итогового JSON
    counter = 0

    while counter < 10:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        resp_message = response.choices[0].message
        messages.append(resp_message)

        # Если LLM закончила и просто дает текст
        if not resp_message.tool_calls:
            break

        # Если LLM просит вызвать инструменты
        for tool_call in resp_message.tool_calls:
            counter += 1
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Выполняем
            if func_name == "list_files":
                result = list_files(args.get("path", "."))
            elif func_name == "read_file":
                result = read_file(args.get("path"))
            else:
                result = "Unknown tool"

            # Сохраняем для вывода
            all_tool_calls_result.append({
                "tool": func_name,
                "args": args,
                "result": result
            })

            # Возвращаем результат в LLM
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": result
            })

    # Итоговый вывод
    output = {
        "answer": resp_message.content,
        "source": "wiki/...", # Здесь в идеале нужно вытащить путь из ответа через regex или промпт
        "tool_calls": all_tool_calls_result
    }
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()