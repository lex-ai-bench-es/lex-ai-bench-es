"""Analisis de longitud por bloque tematico.

Cuenta caracteres del articulado de cada bloque, calcula proporciones,
y propone un reparto de preguntas basado en esa proporcion (con un
suelo minimo para evitar bloques con 0 preguntas).
"""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ai_act_rgpd_es.blocks import AI_ACT_BLOCKS, RGPD_BLOCKS

INTERIM = Path("data/interim")
console = Console()

# Total de preguntas por norma (de design_decisions.md)
N_AI_ACT = 150
N_RGPD = 120

# Suelo minimo por bloque para no dejar ningun bloque sin cubrir
MIN_PER_BLOCK = 5


def load_articles(filename: str) -> dict[str, dict]:
    """Devuelve {article_number: article_dict}."""
    path = INTERIM / filename
    if not path.exists():
        console.print(f"[red]No existe {path}. Corre antes scripts/parse_norms.py[/red]")
        return {}
    return {
        a["article_number"]: a for a in (json.loads(line) for line in path.open(encoding="utf-8"))
    }


def block_stats(blocks: dict[str, list[str]], articles: dict[str, dict]) -> list[dict]:
    """Por cada bloque calcula chars totales y articulos cubiertos."""
    stats = []
    for block_name, art_nums in blocks.items():
        present = [num for num in art_nums if num in articles]
        missing = [num for num in art_nums if num not in articles]
        total_chars = sum(articles[num]["char_count"] for num in present)
        stats.append(
            {
                "block": block_name,
                "n_articles_planned": len(art_nums),
                "n_articles_found": len(present),
                "missing": missing,
                "chars": total_chars,
            }
        )
    return stats


def allocate_questions(stats: list[dict], total_questions: int, min_per_block: int) -> list[dict]:
    """Asigna preguntas proporcionalmente a chars, con suelo minimo.

    Algoritmo:
    1. Cada bloque recibe min_per_block como suelo.
    2. El resto se reparte proporcionalmente a chars.
    3. Redondeo: largest remainder method para que sume exactamente total.
    """
    n_blocks = len(stats)
    reserved = n_blocks * min_per_block
    if reserved > total_questions:
        raise ValueError(
            f"min_per_block * n_blocks ({reserved}) > total ({total_questions}). "
            f"Reduce min_per_block o aumenta total."
        )
    remaining = total_questions - reserved
    total_chars = sum(s["chars"] for s in stats)

    if total_chars == 0:
        # fallback: reparto igualitario
        per_block = remaining // n_blocks
        for s in stats:
            s["allocated"] = min_per_block + per_block
        return stats

    # Proporcional con largest remainder
    floats = [(s, remaining * s["chars"] / total_chars) for s in stats]
    floors = [(s, int(f)) for s, f in floats]
    remainders = sorted(
        ((s, f - int(f)) for s, f in floats),
        key=lambda x: x[1],
        reverse=True,
    )
    allocated_extra = remaining - sum(fl for _, fl in floors)
    extra_set = {id(s) for s, _ in remainders[:allocated_extra]}

    for s, fl in floors:
        s["allocated"] = min_per_block + fl + (1 if id(s) in extra_set else 0)
    return stats


def render_table(title: str, stats: list[dict], total_questions: int) -> None:
    total_chars = sum(s["chars"] for s in stats)
    t = Table(title=f"{title} — total {total_questions} preguntas")
    t.add_column("Bloque", style="cyan", max_width=42)
    t.add_column("Articulos\n(plan/encontrados)", justify="center")
    t.add_column("Chars", justify="right")
    t.add_column("% chars", justify="right")
    t.add_column("Preguntas\nasignadas", justify="right", style="green")
    t.add_column("% preguntas", justify="right")

    for s in stats:
        pct_chars = s["chars"] / total_chars * 100 if total_chars else 0
        pct_q = s["allocated"] / total_questions * 100
        t.add_row(
            s["block"],
            f"{s['n_articles_planned']}/{s['n_articles_found']}",
            f"{s['chars']:,}",
            f"{pct_chars:.1f}%",
            str(s["allocated"]),
            f"{pct_q:.1f}%",
        )
    t.add_row(
        "[bold]TOTAL[/bold]",
        "",
        f"[bold]{total_chars:,}[/bold]",
        "100.0%",
        f"[bold]{sum(s['allocated'] for s in stats)}[/bold]",
        "100.0%",
    )
    console.print(t)

    # Avisar de bloques con articulos faltantes
    missing_blocks = [s for s in stats if s["missing"]]
    if missing_blocks:
        console.print("\n[yellow]Bloques con articulos no encontrados en el parseado:[/yellow]")
        for s in missing_blocks:
            console.print(f"  - {s['block']}: faltan {s['missing']}")
        console.print(
            "[dim]Probable causa: el parser no extrajo bien algun articulo. "
            "Revisa data/interim/articles_*.jsonl o reparsea.[/dim]"
        )


def main() -> None:
    ai_act_articles = load_articles("articles_ai_act.jsonl")
    rgpd_articles = load_articles("articles_rgpd.jsonl")

    if not ai_act_articles or not rgpd_articles:
        return

    ai_stats = allocate_questions(
        block_stats(AI_ACT_BLOCKS, ai_act_articles),
        N_AI_ACT,
        MIN_PER_BLOCK,
    )
    rgpd_stats = allocate_questions(
        block_stats(RGPD_BLOCKS, rgpd_articles),
        N_RGPD,
        MIN_PER_BLOCK,
    )

    render_table("AI Act", ai_stats, N_AI_ACT)
    console.print()
    render_table("RGPD", rgpd_stats, N_RGPD)

    # Guardar a JSON para uso posterior
    out = {
        "ai_act": {s["block"]: s["allocated"] for s in ai_stats},
        "rgpd": {s["block"]: s["allocated"] for s in rgpd_stats},
        "metadata": {
            "method": "proportional_to_article_length_with_min_floor",
            "min_per_block": MIN_PER_BLOCK,
            "total_ai_act": N_AI_ACT,
            "total_rgpd": N_RGPD,
        },
    }
    out_path = Path("data/interim/coverage_allocation.json")
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"\n[green]Guardado en {out_path}[/green]")


if __name__ == "__main__":
    main()
