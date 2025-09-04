
from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Tuple

TRIVIAL_COMMANDS = {
    "ls","cd","pwd","clear","history","exit","whoami","date","time",
    "cat","echo","vi","vim","nano","code","open","touch"
}

DANGEROUS_PATTERNS = [
    r"rm\\s+-rf\\s+/\\b",
    r":\\s*\\(\\)\\{\\s*:\\s*\\|\\s*:\\s*;\\s*\\}\\s*;\\s*:",  # fork bomb
]

def detect_shell_and_rc() -> Tuple[str, Path]:
    shell = os.environ.get("SHELL","").strip()
    home = Path.home()
    if shell.endswith("zsh"):
        return "zsh", home/".zshrc"
    if shell.endswith("bash"):
        return "bash", home/".bashrc"
    return "zsh", home/".zshrc"

def is_trivial(cmd: str) -> bool:
    parts = cmd.strip().split()
    if not parts:
        return True
    if len(parts) == 1 and parts[0] in TRIVIAL_COMMANDS:
        return True
    if parts[0] == "cd" and len(parts) == 2:
        return True
    return False

def looks_dangerous(cmd: str) -> bool:
    c = " ".join(cmd.strip().split())
    for pat in DANGEROUS_PATTERNS:
        if re.search(pat, c):
            return True
    return False

def normalize_command(cmd: str) -> str:
    s = cmd.strip().rstrip(";").replace("\\t"," ")
    s = " ".join(s.split())
    return s

def safe_alias_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_-]", "", name)
    if not name or not name[0].isalpha():
        name = "a" + name
    return name[:24]

def score_command(cmd: str) -> float:
    length = len(cmd)
    pipes = cmd.count("|")
    opts = len([t for t in cmd.split() if t.startswith("-")])
    return length*0.6 + pipes*2 + opts*1.2
