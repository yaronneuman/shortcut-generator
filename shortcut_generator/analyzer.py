from __future__ import annotations

from collections import Counter

from .utils import is_trivial, score_command, normalize_command


def top_candidates(commands: list[str], top_n: int = 8, min_count: int = 2) -> list[tuple[str, int, float]]:
    counts = Counter(normalize_command(c) for c in commands if c.strip())
    items: list[tuple[str, int, float]] = []
    for cmd, cnt in counts.items():
        if cnt < min_count:
            continue
        if is_trivial(cmd):
            continue
        complexity = score_command(cmd)
        combined = cnt * 2.0 + complexity
        items.append((cmd, cnt, combined))
    items.sort(key=lambda x: x[2], reverse=True)
    return items[:top_n]
