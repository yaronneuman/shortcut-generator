# AI Shortcut Analyzer (Offline)

Analyze your shell history and suggest aliases using a local tiny Ollama model, with a rule-based fallback if Ollama isn't installed.

## Features
- Parses `~/.zsh_history` or `~/.bash_history`
- Ranks frequently used + complex commands
- Generates short alias names via **Ollama** (default model: `phi3:mini`)
- Manages aliases in a dedicated `~/.shortcuts.generated` file, keeping your RC file clean.
- Adds a single, safe `source` command to your shell's RC file.
- Never requires internet once the model is pulled.

## Install

1) (Optional) Install [Ollama](https://ollama.com/):
```bash
brew install ollama   # macOS (or use your OS package)
brew services start ollama
ollama pull deepseek-r1:8b
```

2) Install this package:
```bash
pip install .
```

## Usage

### Interactive Analysis

Run an interactive analysis of your shell history:
```bash
shortcut-generator
```
This guides you through suggested aliases. If you choose not to apply them immediately, they are saved to a temporary file (e.g., `/tmp/aliases-XXXX.sh`), and the path is printed.

To apply the aliases, either use the `--apply` flag or confirm at the prompt:
```bash
shortcut-generator --apply
```
This will create or update `~/.shortcuts.generated` with your aliases and ensure your shell's RC file is configured to load them.

### Applying Aliases from a File

You can apply aliases directly from a file, such as one saved from a previous session. This will add them to your `~/.shortcuts.generated` file.

```bash
# Apply aliases saved from a previous run
shortcut-generator /tmp/aliases-XXXX.sh
```

The file should contain one alias command per line, for example:
```sh
alias gco='git checkout'
alias gst='git status'
```

### Other Options

Tune how many suggestions you see and the minimum occurrences:
```bash
shortcut-generator --top 10 --min-count 3
```

Use a different local model:
```bash
shortcut-generator --model llama3.2:1b
```

## Alias Management

This tool keeps your shell's configuration clean by separating generated aliases into their own file.

1.  **Alias File**: All your accepted aliases are stored in `~/.shortcuts.generated`.
2.  **RC File**: Your main shell RC file (e.g., `~/.zshrc`, `~/.bashrc`) is modified only once to add a block that sources the alias file:

```sh
# >>> shortcut-generator source >>>
source "/Users/your_user/.shortcuts.generated"
# <<< shortcut-generator source <<<
```

- Obvious dangerous patterns (like `rm -rf /`) are skipped during analysis.
- A backup of your RC file is created if it's modified.

## Uninstall

1.  Remove the `shortcut-generator source` block from your RC file (e.g., `~/.zshrc`).
2.  Delete the alias file: `rm ~/.shortcuts.generated`.
3.  Uninstall the package: `pip uninstall shortcut-generator`.
