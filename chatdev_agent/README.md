# ChatDev agent demo

Run this directory directly:

```powershell
python main.py "Create a command-line todo list"
```

The default `offline` backend is deterministic and requires no credentials.
To use a provider instead, set `CHATDEV_BACKEND=ollama` (optionally set
`OLLAMA_MODEL`) or `CHATDEV_BACKEND=openai` with `OPENAI_API_KEY` and an
optional `OPENAI_MODEL`.

`agent.py` exposes the separate Ollama tool-enabled flow. Its `execute_shell`
tool runs commands without restrictions; only use it with prompts you trust.
