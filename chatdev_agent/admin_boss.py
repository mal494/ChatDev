import os
import sys

# Configure UTF-8 stdout if available to prevent Windows cp1252 charmap errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure current, parent, and System/ directories are on path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for _dir in [current_dir, parent_dir, os.path.join(current_dir, "System")]:
    if _dir not in sys.path:
        sys.path.append(_dir)

try:
    from orchestrator import Orchestrator
except Exception as e:
    print(f"[!] Failed to import Orchestrator: {e}")
    raise


def run_admin_diagnosis():
    bot = Orchestrator()
    return bot.admin_diagnose()


if __name__ == "__main__":
    print("========================================")
    print("   ADMIN BOSS - SYSTEM DIAGNOSTICS      ")
    print("========================================")
    report = run_admin_diagnosis()
    print("\n[+] ADMIN REPORT:\n" + "-" * 60)
    print(report)
    print("-" * 60)
