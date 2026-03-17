# Implementation Plan - Task 2: Documentation Agent

## 1. Tool Definitions (JSON Schemas)
I will implement two tools using the OpenAI-compatible function calling format:

- **`list_files`**: 
  - Purpose: List entries in a directory to help the agent discover wiki pages.
  - Parameters: `path` (string) - relative path from the project root.
- **`read_file`**: 
  - Purpose: Read the content of a specific markdown file to extract answers.
  - Parameters: `path` (string) - relative path to the file.

## 2. Agentic Loop Logic
The agent will follow a `while` loop (up to 10 iterations):
1. **Send** the current message history + tool definitions to the LLM.
2. **Check** for `tool_calls` in the response.
3. **If tool calls exist**:
   - For each tool call, execute the corresponding Python function (`list_files` or `read_file`).
   - Append the tool's output to the message history with the `role: "tool"` and the specific `tool_call_id`.
   - Repeat the loop.
4. **If no tool calls**:
   - The LLM has provided the final answer.
   - Extract the `answer` and the `source` (file path + anchor).
   - Return the final JSON and exit.

## 3. Path Security
To prevent Directory Traversal attacks (e.g., `../../etc/passwd`):
- I will use `os.path.abspath()` to resolve the absolute path of the requested file.
- I will verify that the resolved path starts with the absolute path of the project's root directory.
- If the path is outside the project root, the tool will return an "Access Denied" error instead of executing.

## 4. Final Output Format
The final output will be a strict JSON containing:
- `answer`: The text found in the wiki.
- `source`: The specific file and section (e.g., `wiki/git-workflow.md#resolving-merge-conflicts`).
- `tool_calls`: A full log of all tools used during the loop.