from __future__ import annotations

import re
import shutil
import subprocess
from typing import Optional

from .utils import safe_alias_name

DEFAULT_MODEL = "deepseek-r1:8b"


def _has_ollama() -> bool:
    return shutil.which("ollama") is not None


def llm_alias_suggestion(command: str, model: Optional[str] = None, timeout: int = 12) -> Optional[str]:
    if not _has_ollama():
        return None
    model = model or DEFAULT_MODEL
    system = ("""
You generate short, memorable shell alias names for commands.
<Alias Rules>
    - 3-6 lowercase letters
    - letters/numbers only
    - start with a letter.
    - You can use abbreviations
    - You can short one of the words and keep other word complete, but don't keep all words
    - Reflect the command meaning
</Alias Rules>
<Command Rules>
    - Consider if all the arguments are relevance or not
</Command Rules>
<Output Format>
    - Output ONLY the alias.
</Output Format>
<Examples for good aliases>
alias restart='exec bash -l'
alias settings2='bash ~/conf/copy_settings'
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias make='make -j8'
alias sa='$QOSMOS_SDK_ROOT/examples/session_attributes/session_attributes'
alias wdiff=do_wdiff
alias ctags='ctags --c++-kinds=+p+l -R'
alias ssh='bash ~/conf/myssh.sh'
alias user2='bash ~/conf/create_user.sh'
alias clssh='rm -r ~/.ssh/tmp/*'
alias cid2='bash ~/conf/copy_id_to'
alias mkey='ssh-keygen'
alias proxy_to='ssh -R 8000:localhost:9000'
alias kamino='ssh kamino.local'
alias hkamino='ssh office.lightcyber.com -p 220'
alias gtoconf='cd ~/conf'
alias clpycs='find . -name '*.pyc' -delete'
alias disable_traps='sudo kextunload -c com.paloaltonetworks.driver.kproc-ctrl'
alias tunnel_to="sudo ssh -L 80:localhost:80 -L 443:localhost:443"
alias gog="cd ~/gonzo"
alias be="cd ~/git/be3"
alias xdm="cd ~/git/xdm"
alias xql="cd ~/git/xql-content"
alias gst="git status"
alias grst="git reset"
alias g="git"
alias ipy="cd ~/gonzo && ./ipygonzo"
alias leap="cd ~/work/leap"
alias gg="cd ~/git/"
alias ops="cd ~/git/tenants-config-prod/"
alias clean_ds_store="find ./ -name \".DS_Store\" -type f -delete"
</examples>"""
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
