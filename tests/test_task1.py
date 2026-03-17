import subprocess
import json
import pytest

def test_agent_output():
    # Запускаем агент с простым вопросом
    # Используем sys.executable для запуска через текущий интерпретатор
    result = subprocess.run(
        ["python3", "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True
    )
    
    # 1. Проверяем, что агент завершился без ошибок
    assert result.returncode == 0
    
    # 2. Пытаемся распарсить вывод (stdout)
    try:
        data = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        pytest.fail("Agent output is not valid JSON")
    
    # 3. Проверяем наличие обязательных полей из задания
    assert "answer" in data, "JSON must contain 'answer' field"
    assert "tool_calls" in data, "JSON must contain 'tool_calls' field"
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"

if __name__ == "__main__":
    test_agent_output()
    print("Test passed locally!")
