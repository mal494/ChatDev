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


def _offline_llm(prompt: str) -> str:
    """Return stable, useful text for local demos and automated tests."""
    if "Create a concise implementation plan" in prompt:
        task = prompt.rsplit("Task:", 1)[-1].strip()
        return (
            f"1. Identify the inputs and expected output for: {task}\n"
            "2. Implement the smallest complete solution.\n"
            "3. Run a focused verification and report the result."
        )
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
