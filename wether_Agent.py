
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# ----------------------------------
# 1. CONFIGURATION
# ----------------------------------

MODEL = "	gemini-3-flash-preview"

# Change this to your actual project folder
WORKSPACE = Path(r"C:\Users\YourName\Desktop\MyProject").resolve()

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("Please set GEMINI_API_KEY first.")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ----------------------------------
# 2. WORKSPACE SECURITY
# ----------------------------------

def safe_path(path: str) -> Path:
    """Only allow access inside the selected project folder."""

    target = (WORKSPACE / path).resolve()

    if not target.is_relative_to(WORKSPACE):
        raise ValueError("Access outside project folder is blocked.")

    return target


# ----------------------------------
# 3. TOOL: LIST PROJECT FILES
# ----------------------------------

def list_files() -> str:
    """List files and folders in the project."""

    ignored = {".git", "node_modules", ".venv", "__pycache__"}

    results = []

    for path in WORKSPACE.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue

        if len(results) >= 200:
            results.append("...file listing truncated")
            break

        relative = path.relative_to(WORKSPACE)
        results.append(str(relative))

    return "\n".join(results) or "Project is empty."


# ----------------------------------
# 4. TOOL: READ FILE
# ----------------------------------

def read_file(path: str) -> str:
    """Read an existing file from the project.

    Args:
        path: Relative path of the file.
    """

    target = safe_path(path)

    if not target.is_file():
        return "File does not exist."

    if target.stat().st_size > 200_000:
        return "File is too large to read."

    return target.read_text(encoding="utf-8")


# ----------------------------------
# 5. TOOL: CREATE OR EDIT FILE
# ----------------------------------

def write_file(path: str, content: str) -> str:
    """Create a new file or modify an existing project file.

    Args:
        path: Relative file path.
        content: Complete file content.
    """

    target = safe_path(path)

    if len(content) > 100_000:
        return "Content too large."

    if target.exists() and not target.is_file():
        return "Target is not a regular file."

    action = "Overwrite" if target.exists() else "Create"

    print(f"\nAgent wants to {action}: {path}")

    approval = input("Allow? (y/n): ").strip().lower()

    if approval != "y":
        return "File operation rejected by user."

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return f"Successfully saved: {path}"


# ----------------------------------
# 6. TOOL: RUN TERMINAL COMMAND
# ----------------------------------

def run_command(command: str) -> str:
    """Run an approved development command in the project.

    Args:
        command: Terminal command to execute.
    """

    import shlex

    # Never accept shell chaining or redirection
    dangerous = ["&&", "||", ";", "|", ">", "<", "`", "$", "\n"]

    if any(symbol in command for symbol in dangerous):
        return "Blocked: shell operators are not allowed."

    parts = shlex.split(command, posix=True)

    if not parts:
        return "Empty command."

    executable = parts[0].lower()

    allowed = {"python", "pytest", "node", "npm", "git"}

    if executable not in allowed:
        return "Command not allowed."

    # Restrict Git operations
    if executable == "git":
        if len(parts) < 2 or parts[1] not in {
            "status", "diff", "log", "add", "commit", "push"
        }:
            return "Git operation not allowed."

    # Ask before executing ANY terminal command
    print(f"\nAgent wants to execute: {command}")

    approval = input("Allow command? (y/n): ").strip().lower()

    if approval != "y":
        return "Command rejected by user."

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=120
        )

        return (
            f"Exit code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout[-10000:]}\n"
            f"STDERR:\n{result.stderr[-10000:]}"
        )

    except subprocess.TimeoutExpired:
        return "Command timed out after 120 seconds."

    except Exception as error:
        return f"Command failed: {error}"


# ----------------------------------
# 7. GIVE TOOLS TO GEMINI
# ----------------------------------

tools = [
    list_files,
    read_file,
    write_file,
    run_command
]

SYSTEM_PROMPT = """
You are MiniCursor, an AI coding agent.

You work inside the user's existing project.

Rules:
1. Understand the user's request before making changes.
2. Inspect existing project files before editing.
3. Reuse the existing project architecture and conventions.
4. Use read_file to inspect code.
5. Use write_file to create or update files.
6. Use run_command to run tests and development commands.
7. Read command output and fix errors when appropriate.
8. Never claim a file was created or a test passed without
   checking the tool result.
9. Do not attempt to access files outside the project.
10. Never expose API keys, passwords, or secrets.
11. Never claim a Git push succeeded unless the command
    actually succeeds.
12. Explain what you changed when finished.
"""


# ----------------------------------
# 8. CREATE AGENT CHAT
# ----------------------------------

chat = client.chats.create(
    model=MODEL,
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=tools,
        temperature=0.2
    )
)


# ----------------------------------
# 9. AGENT LOOP
# ----------------------------------

print("\nMiniCursor is ready!")
print(f"Workspace: {WORKSPACE}")
print("Type 'exit' to quit.\n")

while True:

    user_input = input("You: ").strip()

    if user_input.lower() in {"exit", "quit"}:
        print("MiniCursor stopped.")
        break

    if not user_input:
        continue

    try:
        response = chat.send_message(user_input)
        print("\nMiniCursor:", response.text or "[No text response]", "\n")

    except Exception as error:
        print("\nAgent error:", error, "\n")
