import os
import json
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Настройка клиента (используем переменные окружения)
client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
MODEL = os.getenv("MODEL_NAME", "mistralai/mistral-7b-instruct:free")

def is_safe_path(path):
    """Проверяет, что путь находится внутри текущей папки проекта."""
    root = os.path.abspath(os.getcwd())
    target = os.path.abspath(os.path.join(root, path))
    return os.path.commonpath([root]) == os.path.commonpath([root, target])

# --- Реализация инструментов ---

def list_files(path="."):
    if not is_safe_path(path):
        return "Error: Access denied. Path is outside project root."
    try:
        entries = os.listdir(path)
        return "\n".join(entries)
    except Exception as e:
        return f"Error: {str(e)}"

def read_file(path):
    if not is_safe_path(path):
        return "Error: Access denied. Path is outside project root."
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

# --- Описание инструментов для LLM ---

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from project root"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the project repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file"}
                },
                "required": ["path"]
            }
        }
    }
]

def run_agent(question):
    messages = [
        {"role": "system", "content": "You are a documentation assistant. Use list_files to find wiki files and read_file to answer. Always provide the source in the format: wiki/filename.md#section-anchor"},
        {"role": "user", "content": question}
    ]
    
    all_tool_calls = []
    counter = 0

    while counter < 10:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        messages.append(message)

        # Если модель не хочет вызывать инструменты — выходим из цикла
        if not message.tool_calls:
            break

        # Выполняем каждый вызов инструмента
        for tool_call in message.tool_calls:
            counter += 1
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Логика выполнения
            if function_name == "list_files":
                result = list_files(args.get("path", "."))
            elif function_name == "read_file":
                result = read_file(args.get("path"))
            else:
                result = "Error: Unknown tool"

            # Сохраняем для финального вывода
            all_tool_calls.append({
                "tool": function_name,
                "args": args,
                "result": result
            })

            # Отправляем результат обратно модели
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": result
            })

    # Формируем итоговый JSON
    final_output = {
        "answer": message.content or "I couldn't find the answer.",
        "source": "None" if not all_tool_calls else "Check tool calls for paths", # Модель должна сама вписать это в идеале
        "tool_calls": all_tool_calls
    }
    
    # Пытаемся вытащить source из текста, если модель его там написала
    return json.dumps(final_output, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No question provided"}))
    else:
        print(run_agent(sys.argv[1]))