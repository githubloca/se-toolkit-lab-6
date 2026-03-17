import os
import pytest
from agent import list_files, read_file, is_safe_path

def test_list_files_returns_string():
    # Проверяем, что функция возвращает строку (список файлов)
    result = list_files(".")
    assert isinstance(result, str)
    assert "agent.py" in result  # Файл точно должен быть в корне

def test_read_file_content():
    # Проверяем чтение существующего файла
    result = read_file("AGENT.md")
    assert isinstance(result, str)
    assert len(result) > 0

def test_security_traversal():
    # Проверяем защиту от выхода за пределы папки (Task 2 requirement)
    # Пытаемся выйти вверх по директории
    result = read_file("../../../etc/passwd")
    assert "Error: Access denied" in result or "Error" in result

def test_is_safe_path_logic():
    # Проверка внутренней логики безопасности
    assert is_safe_path("wiki/test.md") is True
    assert is_safe_path("/etc/passwd") is False
    assert is_safe_path("../outside.py") is False