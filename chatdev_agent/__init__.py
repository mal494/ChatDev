"""ChatDev Agent package: multi-role AI workforce and orchestration runtime."""

from __future__ import annotations

import sys
from pathlib import Path

_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parent
for _path in [str(_CURRENT_DIR), str(_PROJECT_ROOT)]:
    if _path not in sys.path:
        sys.path.insert(0, _path)
