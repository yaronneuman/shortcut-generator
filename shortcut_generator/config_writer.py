
from __future__ import annotations
from pathlib import Path
import time
import re
import os

SHORTCUTS_FILENAME = ".shortcuts.generated"
SOURCE_BLOCK_HEADER = "# >>> shortcut-generator source >>>"
SOURCE_BLOCK_FOOTER = "# <<< shortcut-generator source <<<"

def get_shortcuts_path() -> Path:
    return Path.home() / SHORTCUTS_FILENAME

def ensure_source_in_rc(rc_path: Path, shortcuts_path: Path):
    if not rc_path.exists():
        rc_path.parent.mkdir(parents=True, exist_ok=True)
        rc_path.touch()

    original_content = rc_path.read_text(errors="ignore")
    source_line = f"source \"{str(shortcuts_path)}\""
    source_block = f"\n{SOURCE_BLOCK_HEADER}\n{source_line}\n{SOURCE_BLOCK_FOOTER}\n"

    # Check if our source block or a legacy block is already there
    if SOURCE_BLOCK_HEADER in original_content or "# >>> shortcut-generator start >>>" in original_content:
        # Potentially update legacy block to new format in the future, for now, do nothing.
        return

    new_content = original_content + ("" if original_content.endswith("\n") else "\n") + source_block
    
    if original_content != new_content:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup = rc_path.with_suffix(rc_path.suffix + f".bak-{timestamp}")
        backup.write_text(original_content)
        rc_path.write_text(new_content)

def add_alias_line(shortcuts_path: Path, alias_line: str):
    shortcuts_path.parent.mkdir(parents=True, exist_ok=True)
    original_lines = shortcuts_path.read_text(errors="ignore").splitlines() if shortcuts_path.exists() else []
    
    alias_name_match = re.match(r"alias\s+([a-zA-Z0-9_-]+)=", alias_line)
    if not alias_name_match:
        return # Not a valid alias line

    alias_name = alias_name_match.group(1)
    new_lines = []
    found = False

    for line in original_lines:
        if re.match(rf"^alias\s+{re.escape(alias_name)}=", line):
            new_lines.append(alias_line) # Replace existing
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(alias_line)

    new_content = "\n".join(new_lines) + "\n"
    
    if "\n".join(original_lines) + "\n" != new_content:
        shortcuts_path.write_text(new_content)
