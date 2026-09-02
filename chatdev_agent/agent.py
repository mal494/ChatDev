"""Optional Ollama agent with the existing unrestricted shell tool."""

from __future__ import annotations

import json
import os

from tools import TOOLS


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
    """Run one Ollama exchange, executing any shell tool calls it requests.

    This is intentionally separate from the safe offline CLI path. The tool is
    unrestricted to preserve the behavior requested for this optional flow.
    """
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
