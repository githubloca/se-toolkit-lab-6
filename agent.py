import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv

# Явно загружаем файл с секретами
load_dotenv(".env.agent.secret")

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"question\"", file=sys.stderr)
        sys.exit(1)

    user_query = sys.argv[1]
    
    # Получаем настройки из .env.agent.secret
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL")

    # Печатаем инфо в stderr для отладки (не попадет в ответ)
    print(f"DEBUG: Using model {model}", file=sys.stderr)
    print(f"DEBUG: Endpoint {api_base}", file=sys.stderr)

    # Инициализация клиента
    client = OpenAI(
        api_key=api_key,
        base_url=api_base,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": user_query}
            ],
            timeout=60.0
        )

        answer = response.choices[0].message.content.strip()

        # Результат строго по формату лабы
        output = {
            "answer": answer,
            "tool_calls": []
        }

        # Вывод в stdout
        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        print(f"CRITICAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()