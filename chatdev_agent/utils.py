"""Core utilities for ChatDev agent: file operations, code execution, and logging."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime

from config import LOGS_DIR, log


def log_event(message: str, level: str = "INFO") -> None:
    """Write an event to console and the dated system log file."""
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M:%S")
        log_file = os.path.join(LOGS_DIR, f"system_{date_str}.log")
        formatted_msg = f"[{time_str}] [{level}] {message}"
        log(formatted_msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except Exception:
        log(f"[{level}] {message}")


def save_file(filepath: str, content: str) -> bool:
    """Save text to a file, ensuring parent directory exists."""
    try:
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        log_event(f"Failed to save {filepath}: {e}", "ERROR")
        return False


def read_file(filepath: str) -> str | None:
    """Safely read text from a file."""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        log_event(f"Failed to read {filepath}: {e}", "ERROR")
        return None


def get_project_files(project_path: str, extension: str = ".py") -> list[str]:
    """Recursively list all files with a given extension in a directory."""
    file_list: list[str] = []
    if not os.path.exists(project_path):
        return file_list
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(extension):
                file_list.append(os.path.join(root, file))
    return file_list


def extract_code_block(text: str, language: str = "python") -> str:
    """Extract code from markdown backticks or return text if already code."""
    pattern = rf"```(?:{language})?\s*\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return max(matches, key=len).strip()

    # Fallback if no markdown blocks
    if "def " in text or "import " in text or "class " in text:
        return text.strip()
    return ""


def extract_json_safe(text: str) -> dict:
    """Extract and parse a JSON object from raw LLM output."""
    try:
        match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
        candidate = match.group(1) if match else text

        start = candidate.find("{")
        end = candidate.rfind("}") + 1
        if start != -1 and end > start:
            json_str = candidate[start:end]
            return json.loads(json_str)

        if "{" in candidate and "}" in candidate:
            return json.loads(candidate.replace("'", '"'))
    except Exception as e:
        log_event(f"Failed to extract JSON: {e}", "WARN")

    return {}


def run_python_script(script_path: str, args: list[str] | None = None, timeout: int = 30) -> dict:
    """Execute a python script in a subprocess with timeout."""
    abs_script_path = os.path.abspath(script_path)
    command = [sys.executable, abs_script_path] + (args or [])
    cwd = os.path.dirname(abs_script_path) or None
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution timed out ({timeout}s limit reached).",
            "exit_code": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
        }
