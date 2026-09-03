"""Multi-role agent workforce implementation and optional tool-enabled agent flow."""

from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests

# Ensure chatdev_agent and project root directories are in sys.path
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parent
for _path in [str(_CURRENT_DIR), str(_PROJECT_ROOT)]:
    if _path not in sys.path:
        sys.path.insert(0, _path)

from config import ROLE_SYSTEM_PROMPTS, _offline_llm, make_llm
from chatdev_agent.tools import TOOLS
from chatdev_agent.utils import log_event


class Agent:
    """Workforce agent supporting role-based prompts, HTTP completion endpoints, and fallback LLM adapters."""

    def __init__(
        self,
        role: str,
        config: dict[str, Any] | None = None,
        llm: Callable[[str], str] | None = None,
    ) -> None:
        self.role = role
        self.config = config or {}
        self.llm = llm
        roles_map = self.config.get("roles", {})
        self.model_name = roles_map.get(role, "user") if isinstance(roles_map, dict) else "user"
        self.api_base = self.config.get("api_base", os.getenv("CHATDEV_API_BASE", "http://localhost:8080/v1"))
        self.api_key = self.config.get("api_key", os.getenv("CHATDEV_API_KEY", "local"))
        self.api_url = f"{self.api_base}/chat/completions"
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        return ROLE_SYSTEM_PROMPTS.get(self.role, "You are a helpful AI.")

    def think(self, user_input: str, context: str = "", max_retries: int = 2) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"CONTEXT: {context}\n\nTASK: {user_input}" if context else f"TASK: {user_input}"},
        ]

        # --- VERBOSE LOGGING START ---
        print(f"\n\n[{self.role.upper()} INCOMING TASK]:\n{'-'*40}")
        print(f"{user_input[:500]}..." if len(user_input) > 500 else user_input)
        print(f"{'-'*40}\n")
        # -----------------------------

        # 1. If explicit llm adapter provided, use it directly
        if self.llm is not None:
            prompt = f"{self.system_prompt}\nContext: {context}\nTask: {user_input}"
            content = self.llm(prompt)
            print(f"[{self.role.upper()} RESPONSE]:\n{'-'*40}")
            print(f"{content[:500]}..." if len(content) > 500 else content)
            print(f"{'-'*40}\n")
            return content

        # 2. HTTP /chat/completions attempt with retries
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 8192,
            "stream": False,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=2)
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]

                # --- VERBOSE LOGGING END ---
                print(f"[{self.role.upper()} RESPONSE]:\n{'-'*40}")
                print(f"{content[:500]}..." if len(content) > 500 else content)
                print(f"{'-'*40}\n")
                # ---------------------------
                return content
            except Exception as e:
                log_event(f"Agent {self.role} attempt {attempt+1} failed: {e}", "WARN")
                if attempt < max_retries - 1:
                    time.sleep(0.2)

        # 3. Graceful fallback to project's configured backend (e.g. offline / ollama / openai)
        prompt = f"{self.system_prompt}\nContext: {context}\nTask: {user_input}"
        try:
            fallback_llm = make_llm()
            content = fallback_llm(prompt)
            print(f"[{self.role.upper()} RESPONSE (Backend Fallback)]:\n{'-'*40}")
            print(f"{content[:500]}..." if len(content) > 500 else content)
            print(f"{'-'*40}\n")
            return content
        except Exception:
            # Fallback to local offline deterministic engine if live provider is not reachable
            content = _offline_llm(prompt)
            print(f"[{self.role.upper()} RESPONSE (Offline Fallback)]:\n{'-'*40}")
            print(f"{content[:500]}..." if len(content) > 500 else content)
            print(f"{'-'*40}\n")
            return content


TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "execute_shell",
        "description": "Run a shell command.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
}


def run_agent(user_input: str, model: str | None = None) -> str:
    """Run one Ollama exchange, executing any shell tool calls it requests."""
    try:
        import ollama
    except ImportError as exc:
        raise RuntimeError("Ollama support is not installed.") from exc

    selected_model = model or os.getenv("OLLAMA_MODEL", "qwen2.5")
    messages: list[dict[str, object]] = [
        {"role": "system", "content": "You are a ChatDev-style agent with tool access."},
        {"role": "user", "content": user_input},
    ]
    response = ollama.chat(model=selected_model, messages=messages, tools=[TOOL_SPEC])
    message = response["message"]

    for call in message.get("tool_calls", []):
        function = call["function"]
        name = function["name"]
        arguments = function["arguments"]
        if isinstance(arguments, str):
            arguments = json.loads(arguments)
        if name not in TOOLS:
            raise RuntimeError(f"Unsupported tool requested by model: {name}")
        result = TOOLS[name](**arguments)
        messages.append({"role": "tool", "name": name, "content": result})

    if message.get("tool_calls"):
        response = ollama.chat(model=selected_model, messages=messages)
        message = response["message"]

    return message["content"]
