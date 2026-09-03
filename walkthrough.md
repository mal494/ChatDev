# Walkthrough: Workforce Integration, Portable Config, and Admin Diagnostics

We analyzed the three provided code modules (`admin_boss.py`, `config.py`, and `agent.py`) and integrated them cleanly into [`chatdev_agent`](file:///f:/ChatDev/ChatDev/chatdev_agent).

## Summary of Changes

### 1. Environment & Portable Storage ([`config.py`](file:///f:/ChatDev/ChatDev/chatdev_agent/config.py))
- **Portable Drive Detection**: Dynamically discovers available drives (`AI_DATA_DRIVE`, `F:`, `E:`, `C:`, `D:`) and resolves paths with proper trailing drive delimiters to prevent Windows drive-relative path errors.
- **Persistent Folders**: Safely initializes `BASE_DIR`, `REPO_PATH`, `MEMORY_FILE`, and `LOGS_DIR`.
- **Matrix Theme Constants**: Added `GREEN_CODE = "#00FF41"`, `BG_COLOR = "#0D0D0D"`, and `TERMINAL_FONT = ("Courier New", 12)`.
- **Workforce System Prompts**: Defined `ROLE_SYSTEM_PROMPTS` mapping 8 specialized agent roles.

### 2. Multi-Role Agent Workforce ([`agent.py`](file:///f:/ChatDev/ChatDev/chatdev_agent/agent.py) and [`agents/`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/))
- **Unified `Agent` Class**:
  - Implements role-based system prompts, verbose logging of incoming tasks and responses, and multi-attempt retries.
  - Supports dual execution: direct HTTP `/chat/completions` API calls and fallback to `chatdev_agent`'s model backends (`offline`, `ollama`, `openai`).
- **Dedicated Role Modules**:
  - [`ManagerAgent`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/manager.py): Product specification & `requirements.md` generator.
  - [`ArchitectAgent`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/architect.py): Project structure & JSON file mapper.
  - [`DeveloperAgent`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/developer.py): Python code block generator.
  - [`ExecutorAgent`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/executor.py): Instruction-only implementation agent.
  - [`TesterAgent`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/tester.py): Software test runner and PASS/FAIL evaluator.
  - [`QAAgent`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/qa.py): Code execution and hot-fix engineer.
  - [`IntegratorAgent`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/integrator.py): Release engineer generating `requirements.txt` and `README.md`.
  - [`AdminAgent`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/admin.py): System diagnostics and failure root-cause analyzer.
- **Export Registry**: All roles exported in [`agents/__init__.py`](file:///f:/ChatDev/ChatDev/chatdev_agent/agents/__init__.py).

### 3. Orchestrator & Admin Diagnostics ([`orchestrator.py`](file:///f:/ChatDev/ChatDev/chatdev_agent/orchestrator.py) and [`admin_boss.py`](file:///f:/ChatDev/ChatDev/chatdev_agent/admin_boss.py))
- **`Orchestrator`**:
  - Coordinates the 8 workforce roles.
  - Includes `wait_for_brain()`, `_collect_log_snippets()`, `run_qa_check()`, and `run_full_cycle()`.
  - Implements `admin_diagnose()` to analyze brain health and recent logs, producing actionable diagnostics.
- **`admin_boss.py`**:
  - Provides a standalone CLI entry point executing `run_admin_diagnosis()` with formatted report output and Windows cp1252 character-encoding safety.

### 4. CLI & Message Bus Integration ([`main.py`](file:///f:/ChatDev/ChatDev/chatdev_agent/main.py) and [`core/bus.py`](file:///f:/ChatDev/ChatDev/chatdev_agent/core/bus.py))
- Added `--diagnose` / `--admin` CLI flag to run Admin Boss diagnostics directly.
- Added `--mode full` for end-to-end multi-agent project generation alongside the default `--mode compact` planner/coder flow.

### 5. Utilities ([`utils.py`](file:///f:/ChatDev/ChatDev/chatdev_agent/utils.py))
- Added `save_file`, `read_file`, `get_project_files`, `extract_code_block`, `extract_json_safe`, `run_python_script` (subprocess with timeout), and `log_event` (file + console logging).

---

## Verification Results

### Automated Unit Tests
Executed the entire test suite in [`chatdev_agent/tests/`](file:///f:/ChatDev/ChatDev/chatdev_agent/tests/):
```powershell
python -m unittest discover tests
```
**Result**:
```
Ran 18 tests in 11.601s
OK
```
All 18 tests passed, covering configuration, theme constants, all 8 workforce roles, fallback mechanisms, `Orchestrator`, and `admin_diagnose()`.

### CLI Executions Verified
1. **Admin Boss Direct Run**:
   ```powershell
   python admin_boss.py
   ```
   *Result*: Displays banner and diagnostics report with exit code 0.

2. **Main CLI Diagnostics**:
   ```powershell
   python main.py --diagnose
   ```
   *Result*: Successfully executes `run_admin_diagnosis()` with exit code 0.

3. **Standard Compact Mode**:
   ```powershell
   python main.py "Create a command-line todo list"
   ```
   *Result*: Successfully generates plan and implementation.

4. **Full Workforce Cycle**:
   ```powershell
   python main.py --mode full "Create a simple calculator"
   ```
   *Result*: Orchestrates PM -> Architect -> Developer -> QA -> Integrator, producing project files in persistent storage with exit code 0.
