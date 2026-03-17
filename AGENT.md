# Documentation Agent Architecture

This agent is designed to navigate a project's documentation (wiki) to answer user questions using an autonomous agentic loop and function-calling capabilities.

## 1. Agentic Loop
The agent implements a reasoning loop that allows it to interact with the file system before providing a final answer.
- **Step 1:** The user's question is sent to the LLM along with tool definitions.
- **Step 2:** If the LLM requests a tool call, the agent executes the function locally.
- **Step 3:** The tool output is appended to the message history, and the agent queries the LLM again.
- **Step 4:** This repeats until the LLM provides a final text answer or the limit of 10 tool calls is reached.

## 2. Tools
The agent has access to the following tools to explore the repository:

### `list_files`
- **Description:** Lists all files and directories at a specified path.
- **Usage:** Used by the agent to discover which markdown files exist in the `wiki/` directory.

### `read_file`
- **Description:** Reads the raw content of a specific file.
- **Usage:** Used to extract information from a document once the relevant file is identified.

## 3. Security (Path Validation)
To ensure the agent cannot access sensitive files outside the project, all file operations include:
- **Absolute Path Resolution:** Paths are resolved using `os.path.abspath`.
- **Root Enforcement:** The agent verifies that the target path resides within the project's root directory using `os.path.commonpath`. Any attempt to access external files (e.g., `../.env`) results in an "Access Denied" error.

## 4. System Prompt Strategy
The system prompt instructs the LLM to:
1. First, list the files in the `wiki/` folder to identify relevant documents.
2. Read the identified files to find the exact answer.
3. Formulate a final response that includes a `source` field pointing to the specific file and section anchor (e.g., `wiki/git-workflow.md#resolving-merge-conflicts`).