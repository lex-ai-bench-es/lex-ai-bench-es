"""Compara reparto a ojo (coverage_plan.md original) con reparto
proporcional a longitud, y resalta diferencias > 30 por ciento."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

# Reparto "a ojo" original del coverage_plan.md
EYEBALL_AI_ACT = {
    "Disposiciones generales": 8,
    "Practicas prohibidas": 15,
    "Sistemas de alto riesgo (clasificacion)": 25,
    "Requisitos sistemas alto riesgo": 25,
    "Obligaciones proveedores y deployers": 20,
    "Autoridades notificantes y organismos": 8,
    "Modelos GPAI": 20,
    "Sandboxes regulatorios": 8,
    "Gobernanza": 6,
    "Sanciones": 10,
    "Entrada en vigor": 5,
}

EYEBALL_RGPD = {
    "Disposiciones generales y ambito": 6,
    "Principios": 12,
    "Bases juridicas": 18,
    "Derechos del interesado": 25,
    "Obligaciones responsable y encargado": 15,
    "Seguridad y brechas": 10,
    "DPIA y DPO": 10,
    "Transferencias internacionales": 12,
    "Autoridades de control": 6,
    "Recursos y sanciones": 6,
}


def compare(eyeball: dict[str, int], objective: dict[str, int], title: str) -> None:
    t = Table(title=title)
    t.add_column("Bloque", style="cyan", max_width=42)
    t.add_column("A ojo", justify="right")
    t.add_column("Por longitud", justify="right")
    t.add_column("Diff abs", justify="right")
    t.add_column("Diff %", justify="right")
    t.add_column("Senal", justify="center")

    for block in eyeball:
        ey = eyeball[block]
        obj = objective.get(block, 0)
        diff = obj - ey
        diff_pct = (diff / ey * 100) if ey else float("inf")

        # Codigo de color: rojo si diferencia > 50%, amarillo > 30%, verde resto
        if abs(diff_pct) > 50:
            signal = "[red]ALTA[/red]"
        elif abs(diff_pct) > 30:
            signal = "[yellow]MEDIA[/yellow]"
        else:
            signal = "[green]baja[/green]"

        t.add_row(
            block,
            str(ey),
            str(obj),
            f"{diff:+d}",
            f"{diff_pct:+.0f}%",
            signal,
        )
    console.print(t)


def main() -> None:
    alloc_path = Path("data/interim/coverage_allocation.json")
    if not alloc_path.exists():
        console.print("[red]Corre antes scripts/analyze_block_lengths.py[/red]")
        return

    alloc = json.loads(alloc_path.read_text(encoding="utf-8"))

    compare(EYEBALL_AI_ACT, alloc["ai_act"], "AI Act — comparativa")
    console.print()
    compare(EYEBALL_RGPD, alloc["rgpd"], "RGPD — comparativa")

    console.print(
        "\n[bold]Como interpretar:[/bold]\n"
        "  [green]baja[/green]: diff < 30 por ciento. Mantener el reparto a ojo.\n"
        "  [yellow]MEDIA[/yellow]: diff 30-50 por ciento. Decidir caso por caso.\n"
        "  [red]ALTA[/red]: diff > 50 por ciento. Ajustar hacia el objetivo."
    )


if __name__ == "__main__":
    main()
