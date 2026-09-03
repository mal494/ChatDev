"""Configuration and model-provider adapters for the standalone demo."""

from __future__ import annotations

import os
import sys
from collections.abc import Callable

try:
    from dotenv import load_dotenv
except ImportError:  # The offline demo must work without optional dependencies.
    def load_dotenv() -> bool:
        return False


load_dotenv()
SUPPORTED_BACKENDS = {"offline", "ollama", "openai"}


class BackendConfigurationError(RuntimeError):
    """Raised when a selected model provider cannot be used."""


def log(message: str) -> None:
    """Write operational messages without mixing them into CLI results."""
    print(f"[chatdev_agent] {message}", file=sys.stderr)


# --- DRIVE CONFIGURATION & PORTABLE PATHS ---
def _resolve_base_dir() -> tuple[str, str]:
    """Find a valid drive and base directory with automatic fallback."""
    explicit_data_dir = os.getenv("CHATDEV_DATA_DIR")
    if explicit_data_dir:
        drive_letter = os.path.splitdrive(os.path.abspath(explicit_data_dir))[0] or "F:"
        return drive_letter, os.path.abspath(explicit_data_dir)

    configured_drive = os.getenv("AI_DATA_DRIVE")
    candidate_drives = [configured_drive] if configured_drive else ["E:", "F:", "D:", "C:"]
    for d in candidate_drives:
        if d and os.path.exists(d):
            drive_root = d if d.endswith(("\\", "/")) else f"{d}\\"
            return d, os.path.abspath(os.path.join(drive_root, "AI_Data"))

    # Fallback to local workspace directory
    current_drive = os.path.splitdrive(os.path.abspath(__file__))[0] or "F:"
    local_ai_data = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "AI_Data"))
    return current_drive, local_ai_data


DRIVE, BASE_DIR = _resolve_base_dir()
REPO_PATH = os.path.join(BASE_DIR, "OmniSolve_Repo")
MEMORY_FILE = os.path.join(BASE_DIR, "memory.txt")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")

# Ensure the Portable Drive folders exist
for folder in [BASE_DIR, REPO_PATH, LOGS_DIR]:
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        pass

# --- THEME (Matrix Green) ---
GREEN_CODE = "#00FF41"
BG_COLOR = "#0D0D0D"
TERMINAL_FONT = ("Courier New", 12)

# --- ROLE SYSTEM PROMPTS ---
ROLE_SYSTEM_PROMPTS: dict[str, str] = {
    "manager": (
        "You are a Senior Product Manager. "
        "Break down the user request into a detailed 'requirements.md'. "
        "Output Markdown only."
    ),
    "architect": (
        "You are a Senior Software Architect. "
        "Task: Design the file structure for a Python project. "
        "Output ONLY a JSON object mapping filenames to instructions. "
        "RULES: "
        "1. Use standard Python project structure (e.g., src/main.py, src/game.py). "
        "2. DO NOT create separate files for 'documentation', 'design', 'feedback', or 'testing' as .py files. "
        "3. Keep the file count low (max 3-5 files) for simple requests. "
        "4. Ensure 'src/main.py' exists as the entry point. "
        "5. MERGE related functionality into single files (e.g., put game over logic inside game.py)."
    ),
    "developer": (
        "You are an Expert Python Developer. "
        "Write the code for the requested file. "
        "Output ONLY the code block. Do not converse."
    ),
    "executor": (
        "You are an Execution & Implementation Engineer. "
        "ONLY implement the provided plan or file instructions. "
        "Do not change requirements or architecture. "
        "Output ONLY the code block, with no commentary."
    ),
    "tester": (
        "You are a Software Tester. "
        "Your sole responsibility is to run the built software and judge if it works. "
        "Return PASS or FAIL with a short reason."
    ),
    "qa": (
        "You are a QA Engineer. "
        "Run the code. If it fails, fix it. "
        "If it passes, say 'PASS' and nothing else."
    ),
    "integrator": (
        "You are a DevOps Release Engineer. "
        "Task 1: Output a 'requirements.txt' file. "
        "RULES: "
        "- Read the code imports."
        "- Output ONLY the library names (e.g., 'requests', 'pandas')."
        "- If no external libraries are used, output NOTHING (empty string)."
        "- DO NOT include comments, headers, or markdown formatting."
        
        "Task 2: Output a 'README.md'."
        "RULES: "
        "- Include 'Installation' and 'Run' sections."
    ),
    "admin": (
        "You are the Admin Boss Agent. "
        "Your job is to monitor other agents and diagnose failures. "
        "Analyze logs, recent errors, and system health signals. "
        "Return a concise report with:"
        "1) Detected failures or risks,"
        "2) Likely root causes,"
        "3) Recommended actions."
    ),
}


def _offline_llm(prompt: str) -> str:
    """Return stable, useful text for local demos and automated tests."""
    if "Create a concise implementation plan" in prompt:
        task = prompt.rsplit("Task:", 1)[-1].strip()
        return (
            f"1. Identify the inputs and expected output for: {task}\n"
            "2. Implement the smallest complete solution.\n"
            "3. Run a focused verification and report the result."
        )
    if "Senior Product Manager" in prompt or "requirements.md" in prompt:
        return "# Requirements\n\n## Overview\nProject specification breakdown.\n\n## Core Features\n- Primary functionality\n- Verification tests\n"
    if "Senior Software Architect" in prompt or "Design the file structure" in prompt:
        return '{"src/main.py": "Main entry point with CLI execution loop.", "src/core.py": "Core business logic functions."}'
    if "Admin Boss Agent" in prompt or "Diagnose failing agents" in prompt:
        return (
            "Admin diagnostic report:\n"
            "1) Detected failures or risks: None detected; systems operational in offline mode.\n"
            "2) Likely root causes: Local execution verified with mock backend.\n"
            "3) Recommended actions: Ready for production workflows or live model connection."
        )
    if "Software Tester" in prompt:
        return "PASS - Basic verification check completed successfully."
    if "QA Engineer" in prompt:
        return "PASS"
    if "DevOps Release Engineer" in prompt:
        return "requests\nrich\n"
    if "Expert Python Developer" in prompt or "Execution & Implementation Engineer" in prompt:
        return '```python\nprint("Generated code successfully.")\n```'
    return (
        "Implementation outline:\n"
        "- Follow the supplied plan in small, testable steps.\n"
        "- Keep interfaces simple and report any assumptions.\n"
        "- Verify the completed behavior with a focused check."
    )


def make_llm() -> Callable[[str], str]:
    """Build a prompt-to-response function for the configured backend."""
    backend = os.getenv("CHATDEV_BACKEND", "offline").strip().lower()
    if backend not in SUPPORTED_BACKENDS:
        options = ", ".join(sorted(SUPPORTED_BACKENDS))
        raise BackendConfigurationError(
            f"Unsupported CHATDEV_BACKEND={backend!r}. Choose one of: {options}."
        )

    if backend == "offline":
        return _offline_llm

    if backend == "ollama":
        model = os.getenv("OLLAMA_MODEL", "qwen2.5").strip()
        if not model:
            raise BackendConfigurationError("OLLAMA_MODEL must not be empty.")
        try:
            import ollama
        except ImportError as exc:
            raise BackendConfigurationError(
                "Ollama support is not installed. Install the dependencies in requirements.txt."
            ) from exc

        def llm(prompt: str) -> str:
            try:
                response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
                return response["message"]["content"]
            except Exception as exc:
                raise BackendConfigurationError(
                    f"Unable to contact Ollama using model {model!r}: {exc}"
                ) from exc

        return llm

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise BackendConfigurationError(
            "OPENAI_API_KEY is required when CHATDEV_BACKEND=openai."
        )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    if not model:
        raise BackendConfigurationError("OPENAI_MODEL must not be empty.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise BackendConfigurationError(
            "OpenAI support is not installed. Install the dependencies in requirements.txt."
        ) from exc
    client = OpenAI(api_key=api_key)

    def llm(prompt: str) -> str:
        try:
            response = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            if not content:
                raise BackendConfigurationError("OpenAI returned an empty response.")
            return content
        except BackendConfigurationError:
            raise
        except Exception as exc:
            raise BackendConfigurationError(
                f"Unable to contact OpenAI using model {model!r}: {exc}"
            ) from exc

    return llm
