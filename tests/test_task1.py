import subprocess
import json
import os

def test_agent_json_format():
    # Запускаем агента через python (или uv run)
    # Передаем простой вопрос
    process = subprocess.run(
        ["python3", "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True
    )
    
    # Проверяем код возврата
    assert process.returncode == 0, f"Agent failed with error: {process.stderr}"
    
    # Проверяем, что на выходе валидный JSON
    try:
        output = json.loads(process.stdout.strip())
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {process.stdout}"
    
    # Проверяем обязательные поля из задания
    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be a list"

if __name__ == "__main__":
    test_agent_json_format()
    print("Test passed!")