"""Valida que todas las preguntas del pilot cumplen el schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError
from rich.console import Console

from ai_act_rgpd_es.schema import Question

console = Console(force_terminal=True, highlight=False)


def main(path: str = "data/interim/pilot_questions.jsonl") -> int:
    p = Path(path)
    if not p.exists():
        console.print(f"[red]No existe {path}[/red]")
        return 1

    errors = 0
    ok = 0
    for i, line in enumerate(p.open(encoding="utf-8"), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            Question.model_validate(data)
            ok += 1
        except json.JSONDecodeError as e:
            console.print(f"[red]Linea {i}: JSON invalido — {e}[/red]")
            errors += 1
        except ValidationError as e:
            console.print(f"[red]Linea {i} (id={data.get('id', '?')}): schema invalido[/red]")
            for err in e.errors():
                console.print(f"  → {err['loc']}: {err['msg']}")
            errors += 1

    if errors == 0:
        console.print(f"[green]OK {ok} preguntas validas[/green]")
    else:
        console.print(f"[red]ERROR {errors} errores / {ok} validas[/red]")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data/interim/pilot_questions.jsonl"))
