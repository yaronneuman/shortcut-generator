
import typer
from typing import Optional
import tempfile
import os

from .utils import detect_shell_and_rc, looks_dangerous
from .history_parser import read_history
from .analyzer import top_candidates
from .alias_generator import suggest_alias, make_alias_line
from .config_writer import add_alias_line, get_shortcuts_path, ensure_source_in_rc

app = typer.Typer(add_completion=True, help="AI Shortcut Analyzer (offline)")

@app.command()
def analyze(
    top: int = typer.Option(3, "--top", "-t", help="Number of suggestions to show"),
    min_count: int = typer.Option(3, "--min-count", "-m", help="Minimum repeats to consider"),
    model: Optional[str] = typer.Option(None, "--model", "-M", help="Ollama model (default: phi3:mini)"),
    apply: bool = typer.Option(False, "--apply", "-a", help="Append accepted aliases to your shell RC and save"),
    alias_file: Optional[str] = typer.Argument(None, help="File with aliases to apply. If provided, --apply is implied."),
):
    shell, rc_path = detect_shell_and_rc()
    typer.echo(f"Detected shell: {shell}  |  RC file: {rc_path}")
    shortcuts_path = get_shortcuts_path()

    accepted = []
    is_interactive = not alias_file

    if is_interactive:
        history = read_history(shell)
        if not history:
            typer.echo("No history found or file is empty.")
            raise typer.Exit(code=1)

        candidates = top_candidates(history, top_n=top, min_count=min_count)
        if not candidates:
            typer.echo("No suitable candidates found (try lowering --min-count).")
            raise typer.Exit(code=0)

        for i, (cmd, cnt, score) in enumerate(candidates, start=1):
            typer.echo(f"\n{i}) Command (x{cnt}): {cmd}")
            if looks_dangerous(cmd):
                typer.secho("   Skipping: command looks dangerous.", fg=typer.colors.RED)
                continue
            alias = suggest_alias(cmd, model=model)
            alias_line = make_alias_line(alias, cmd)
            typer.echo(f"   Suggested alias: {alias}")
            choice = typer.prompt("   Add this alias? (N/y/edit)", default="N").strip().lower()
            if choice.lower() in ("y", "yes"):
                accepted.append(alias_line)
            elif choice.lower() in ("edit", "e"):
                new_alias = typer.prompt("   Enter alias name", default=alias).strip()
                alias_line = make_alias_line(new_alias, cmd)
                accepted.append(alias_line)
            else:
                typer.echo("   Skipped.")
    else: # alias_file is provided
        try:
            with open(alias_file, 'r') as f:
                accepted = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        except FileNotFoundError:
            typer.secho(f"Error: Input file not found: {alias_file}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    if not accepted:
        typer.echo("\nNo aliases to process.")
        raise typer.Exit(code=0)

    typer.echo("\nProposed alias lines:")
    for line in accepted:
        typer.echo("  " + line)

    should_apply = apply or alias_file
    if not should_apply and is_interactive:
        should_apply = typer.confirm("\nApply these aliases now?", default=False)

    if should_apply:
        ensure_source_in_rc(rc_path, shortcuts_path)
        for line in accepted:
            add_alias_line(shortcuts_path, line)
        typer.secho(f"\nSaved {len(accepted)} alias(es) to {shortcuts_path}", fg=typer.colors.GREEN)
        typer.echo(f"Your RC file ({rc_path}) has been configured to source it.")
        typer.echo("Please restart your shell or run: " + f"source {rc_path}")
    else:
        # This part only runs in interactive mode without --apply
        fd, tmp_path = tempfile.mkstemp(suffix=".sh", prefix="aliases-", dir="/tmp")
        with os.fdopen(fd, 'w') as tmp_file:
            for line in accepted:
                tmp_file.write(line + '\n')
        typer.echo(f"\nAliases saved to a temporary file. To apply them later, run:")
        typer.secho(f"  shortcut-generator {tmp_path}", fg=typer.colors.YELLOW)


def main():
    app()


if __name__ == '__main__':
    main()
