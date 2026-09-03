# ChatDev Agent Orchestration & Workforce

A modular multi-agent orchestration framework featuring dedicated workforce roles, full-cycle project generation, portable drive detection, and Admin Boss system diagnostics.

## Quick Start

### 1. Compact Planner/Coder Pipeline
```powershell
python main.py "Create a command-line todo list"
```

### 2. Full Multi-Agent Workforce Cycle
Runs Manager -> Architect -> Developer -> QA -> Integrator:
```powershell
python main.py --mode full "Create a simple calculator"
```

### 3. Admin Boss Diagnostics
Run automated failure analysis and health monitoring:
```powershell
python admin_boss.py
# or
python main.py --diagnose
```

## Model Providers & Backends
- **Offline (Default)**: Deterministic, requires no external servers or credentials.
- **Ollama**: Set `CHATDEV_BACKEND=ollama` (optionally set `OLLAMA_MODEL`, default `qwen2.5`).
- **OpenAI**: Set `CHATDEV_BACKEND=openai` with `OPENAI_API_KEY` (optionally `OPENAI_MODEL`, default `gpt-4o-mini`).
- **Local HTTP Endpoint**: Configure `CHATDEV_API_BASE` (e.g. `http://localhost:8080/v1`) for OpenAI-compatible completions.

## Workforce Roles
- `manager` (`ManagerAgent`): Senior Product Manager creating `requirements.md`.
- `architect` (`ArchitectAgent`): Software Architect producing JSON file maps and specifications.
- `developer` (`DeveloperAgent`): Python Developer generating implementation code.
- `executor` (`ExecutorAgent`): Execution engineer implementing instructions.
- `tester` (`TesterAgent`): Software tester validating functionality (`PASS`/`FAIL`).
- `qa` (`QAAgent`): Quality engineer executing code and hot-fixing errors.
- `integrator` (`IntegratorAgent`): Release engineer producing `requirements.txt` and `README.md`.
- `admin` (`AdminAgent`): Admin Boss agent diagnosing system errors and recommending remediation.

## Portable Storage & UI Theme
- Auto-discovers persistent storage across available drives (`AI_DATA_DRIVE`, `F:`, `E:`, `C:`, `D:`) with local fallback.
- Exported Matrix theme constants: `GREEN_CODE = "#00FF41"`, `BG_COLOR = "#0D0D0D"`, `TERMINAL_FONT = ("Courier New", 12)`.

## Running Tests
```powershell
python -m unittest discover tests
```
