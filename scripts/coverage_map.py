"""Genera un mapa de cobertura: cuantas preguntas hay/quedan por articulo.

Permite ver visualmente si la distribucion del dataset esta sesgada a
ciertos articulos y faltan otros importantes.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.table import Table

INTERIM = Path("data/interim")
PROCESSED = Path("data/processed")

console = Console()


def load_articles(norm_file: str) -> list[dict]:
    path = INTERIM / norm_file
    if not path.exists():
        return []
    return [json.loads(line) for line in path.open(encoding="utf-8")]


def load_questions_per_article() -> Counter:
    """Cuenta preguntas existentes por articulo (formato: 'Art. N NORM')."""
    counter: Counter = Counter()
    questions_file = PROCESSED / "questions.jsonl"
    if not questions_file.exists():
        return counter

    for line in questions_file.open(encoding="utf-8"):
        q = json.loads(line)
        for ref in q.get("article_refs", []):
            # Normalizar: "Art. 6.1.b RGPD" -> "Art. 6 RGPD"
            parts = ref.replace("Art.", "").strip().split()
            if len(parts) >= 2:
                article_main = parts[0].split(".")[0]
                norm = parts[-1]
                counter[f"Art. {article_main} {norm}"] += 1
    return counter


def main() -> None:
    counts = load_questions_per_article()

    for norm_file, norm_name in [
        ("articles_ai_act.jsonl", "AI_ACT"),
        ("articles_rgpd.jsonl", "RGPD"),
    ]:
        articles = load_articles(norm_file)
        if not articles:
            console.print(f"[yellow]No hay datos para {norm_name}[/yellow]")
            continue

        table = Table(title=f"Cobertura — {norm_name} ({len(articles)} articulos)")
        table.add_column("Articulo", style="cyan")
        table.add_column("Titulo", style="white", max_width=50)
        table.add_column("Chars", justify="right")
        table.add_column("Preguntas", justify="right", style="green")

        shown = articles[:40]
        for a in shown:
            key = f"Art. {a['article_number']} {norm_name}"
            n_q = counts.get(key, 0)
            table.add_row(
                a["article_number"],
                a["title"][:50],
                f"{a['char_count']:,}",
                str(n_q) if n_q else "-",
            )
        console.print(table)
        console.print(f"Mostrados {len(shown)} de {len(articles)} articulos.\n")


if __name__ == "__main__":
    main()
