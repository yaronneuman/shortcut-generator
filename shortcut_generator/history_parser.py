from __future__ import annotations

from pathlib import Path

from .utils import normalize_command


def read_history(shell: str) -> list[str]:
    home = Path.home()
    if shell == "zsh":
        path = home / ".zsh_history"
        return _parse_zsh_history(path)
    else:
        path = home / ".bash_history"
        return _parse_bash_history(path)


def _parse_zsh_history(path: Path) -> list[str]:
    cmds: list[str] = []
    if not path.exists():
        return cmds
    for line in path.read_text(errors="ignore").splitlines():
        if ";" in line:
            cmd = line.split(";", 1)[1]
        else:
            cmd = line
        cmd = normalize_command(cmd)
        if cmd:
            cmds.append(cmd)
    return cmds


def _parse_bash_history(path: Path) -> list[str]:
    cmds: list[str] = []
    if not path.exists():
        return cmds
    for line in path.read_text(errors="ignore").splitlines():
        cmd = normalize_command(line)
        if cmd:
            cmds.append(cmd)
    return cmds
