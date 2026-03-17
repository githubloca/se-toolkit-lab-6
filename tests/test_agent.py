import subprocess
import json
import os

def test_agent_output_structure():
    # Запускаем скрипт с тестовым вопросом
    cmd = ["python3", "agent.py", "Hello"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Проверяем, что скрипт не упал
    assert result.returncode == 0

    # Проверяем, что на выходе валидный JSON
    data = json.loads(result.stdout.strip())

    # Проверяем наличие полей из задания
    assert "answer" in data
    assert "tool_calls" in data
    assert isinstance(data["tool_calls"], list)

if __name__ == "__main__":
    test_agent_output_structure()
    print("Test passed!")