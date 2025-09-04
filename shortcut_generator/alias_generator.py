
from __future__ import annotations
import subprocess
import shutil
import re
from typing import Optional

from .utils import safe_alias_name

DEFAULT_MODEL = "phi3:mini"

def _has_ollama() -> bool:
    return shutil.which("ollama") is not None

def llm_alias_suggestion(command: str, model: Optional[str] = None, timeout: int = 12) -> Optional[str]:
    if not _has_ollama():
        return None
    model = model or DEFAULT_MODEL
    system = (
        "You generate short, memorable shell alias names for commands. "
        "Rules: 2-6 lowercase letters, letters/numbers only, start with a letter. "
        "Reflect the command meaning. Output ONLY the alias."
    )
    prompt = f"Command: {command}\\nAlias:"
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=f"{system}\\n\\n{prompt}",
            text=True,
            capture_output=True,
            timeout=timeout
        )
        raw = result.stdout.strip()
        token = raw.split()[0] if raw else ""
        alias = safe_alias_name(token)
        if 2 <= len(alias) <= 24:
            return alias
    except Exception:
        return None
    return None

def rule_based_alias(command: str) -> str:
    words = re.findall(r"[a-zA-Z0-9_.:/+-]+", command)
    core = [w for w in words if not w.startswith("-") and not w.startswith("--")]
    if not core:
        core = words[:]
    first_letters = "".join(w[0] for w in core[:4]).lower()
    if len(first_letters) < 2 and core:
        w = core[0].lower()
        first_letters = (w[:4] if len(w) >= 2 else (w + "x"))[:4]
    return safe_alias_name(first_letters or "aa")

def suggest_alias(command: str, model: Optional[str] = None) -> str:
    alias = llm_alias_suggestion(command, model=model) or rule_based_alias(command)
    return alias

def make_alias_line(alias: str, command: str) -> str:
    safe_cmd = command.replace("'", "'\\''")
    return f"alias {alias}='{safe_cmd}'"
