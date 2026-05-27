"""Analisis del pilot: numeros clave para decidir si escalar."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console(force_terminal=True, highlight=False)


def main() -> None:
    with Path("data/interim/pilot_questions.jsonl").open(encoding="utf-8") as fh:
        questions = [json.loads(line) for line in fh if line.strip()]

    # Distribucion
    by_type = {}
    by_norm = {}
    by_bloom = {}
    by_difficulty = {}
    for q in questions:
        by_type[q["task_type"]] = by_type.get(q["task_type"], 0) + 1
        by_norm[q["norm"]] = by_norm.get(q["norm"], 0) + 1
        by_bloom[q["bloom_level"]] = by_bloom.get(q["bloom_level"], 0) + 1
        by_difficulty[q["difficulty"]] = by_difficulty.get(q["difficulty"], 0) + 1

    console.print(Panel(f"Total preguntas en pilot: {len(questions)}", style="cyan"))

    for name, dist in [
        ("Por task_type", by_type),
        ("Por norm", by_norm),
        ("Por bloom_level", by_bloom),
        ("Por difficulty", by_difficulty),
    ]:
        t = Table(title=name)
        t.add_column("Categoria")
        t.add_column("N", justify="right")
        for k, v in dist.items():
            t.add_row(k, str(v))
        console.print(t)

    # Cross-check
    cc_path = Path("data/interim/cross_check_results.jsonl")
    if cc_path.exists():
        with cc_path.open(encoding="utf-8") as fh:
            cc = [json.loads(line) for line in fh if line.strip()]
        ok = sum(1 for r in cc if r["consensus_ok"])
        rate = ok / len(cc)
        color = "green" if rate >= 0.85 else "yellow"
        console.print(
            Panel(
                f"Cross-check: {ok}/{len(cc)} preguntas con consenso de los 2 jueces\n"
                f"Tasa de aceptacion: {rate:.1%}",
                title="Cross-check LLM",
                style=color,
            )
        )

    # Decision
    console.print("\n[bold]Decision go/no-go:[/bold]")
    console.print(
        "  [green]GO[/green]      si cross-check >= 85% y distribuciones cercanas a objetivo"
    )
    console.print("  [yellow]REVISAR[/yellow]  si cross-check 70-85% o sesgos en distribucion")
    console.print("  [red]NO GO[/red]   si cross-check < 70% -- revisar guia antes de escalar")

    if cc_path.exists():
        if rate >= 0.85:
            console.print(
                f"\n[bold green]>> GO ({rate:.1%}) -- metodologia validada, escalar a 300 preguntas.[/bold green]"
            )
        elif rate >= 0.70:
            console.print(
                f"\n[bold yellow]>> REVISAR ({rate:.1%}) -- corregir preguntas NEEDS REVIEW antes de escalar.[/bold yellow]"
            )
        else:
            console.print(
                f"\n[bold red]>> NO GO ({rate:.1%}) -- revisar guia de generacion.[/bold red]"
            )


if __name__ == "__main__":
    main()
