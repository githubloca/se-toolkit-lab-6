import pytest
import sys
import os

# 👇 Добавь эти строки в начало файла
# Добавляем корень проекта в Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Теперь импорт сработает
from agent import run_agent


def test_framework_question_uses_read_file():
    """Question about framework should trigger read_file tool."""
    question = "What Python web framework does this project use?"
    result = run_agent(question)
    
    tool_calls = result.get("tool_calls", [])
    assert any(call.get("tool") == "read_file" for call in tool_calls), \
        f"Expected read_file, got: {[c.get('tool') for c in tool_calls]}"


def test_item_count_question_uses_query_api():
    """Question about item count should trigger query_api tool."""
    question = "How many items are in the database?"
    result = run_agent(question)
    
    tool_calls = result.get("tool_calls", [])
    assert any(call.get("tool") == "query_api" for call in tool_calls), \
        f"Expected query_api, got: {[c.get('tool') for c in tool_calls]}"