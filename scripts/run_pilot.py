"""Pipeline end-to-end del pilot.

Evalua las 20 preguntas piloto sobre 1-2 modelos pequenos via Groq API.
Imprime metricas por modelo y guarda outputs raw para auditoria.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from loguru import logger
from rich.console import Console
from rich.table import Table

from ai_act_rgpd_es.evaluation import (
    parse_mc_response,
    score_mc,
    score_short_exact,
    score_short_f1,
)
from ai_act_rgpd_es.prompts import format_mc, format_short
from ai_act_rgpd_es.schema import Question

load_dotenv()
console = Console()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

PILOT_PATH = Path("data/interim/pilot_questions.jsonl")
RESULTS_DIR = Path("results/pilot")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Modelos disponibles en Groq free tier para pilot
MODELS = [
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b",
]


def load_pilot() -> list[Question]:
    questions = []
    for line in PILOT_PATH.open(encoding="utf-8"):
        line = line.strip()
        if line:
            questions.append(Question.model_validate(json.loads(line)))
    return questions


_THINKING_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

# Modelos con razonamiento interno visible: necesitan más tokens y post-proceso
_THINKING_MODELS = {"qwen/qwen3-32b"}


def _effective_max_tokens(model: str, base: int) -> int:
    return 2048 if model in _THINKING_MODELS else base


def _strip_thinking(raw: str) -> str:
    return _THINKING_RE.sub("", raw).strip()


def query_model(model: str, prompt: str, max_tokens: int) -> tuple[str, float]:
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=_effective_max_tokens(model, max_tokens),
        seed=42,
    )
    elapsed = time.perf_counter() - t0
    raw = resp.choices[0].message.content.strip()
    if model in _THINKING_MODELS:
        raw = _strip_thinking(raw)
    return raw, elapsed


def evaluate_model(model: str, questions: list[Question]) -> dict:
    results = []
    for q in questions:
        if q.task_type == "MC":
            prompt = format_mc(q.question, q.options.model_dump())
            raw, latency = query_model(model, prompt, max_tokens=10)
            predicted = parse_mc_response(raw)
            score = score_mc(predicted, q.correct_option)
            results.append(
                {
                    "id": q.id,
                    "task_type": "MC",
                    "norm": q.norm,
                    "bloom": q.bloom_level,
                    "raw": raw,
                    "predicted": predicted,
                    "correct": q.correct_option,
                    "score": score,
                    "latency_s": latency,
                }
            )
        else:  # SHORT
            prompt = format_short(q.question)
            raw, latency = query_model(model, prompt, max_tokens=30)
            score_em = score_short_exact(raw, q.gold_answer, q.aliases)
            score_f1 = score_short_f1(raw, q.gold_answer, q.aliases)
            results.append(
                {
                    "id": q.id,
                    "task_type": "SHORT",
                    "norm": q.norm,
                    "bloom": q.bloom_level,
                    "raw": raw,
                    "gold": q.gold_answer,
                    "score_em": score_em,
                    "score_f1": round(score_f1, 3),
                    "latency_s": latency,
                }
            )
        logger.info(f"{q.id}: ok")
    return {"model": model, "results": results}


def summarize(report: dict) -> dict:
    results = report["results"]
    mc = [r for r in results if r["task_type"] == "MC"]
    sh = [r for r in results if r["task_type"] == "SHORT"]
    return {
        "model": report["model"],
        "n_mc": len(mc),
        "n_short": len(sh),
        "acc_mc": sum(r["score"] for r in mc) / len(mc) if mc else 0,
        "em_short": sum(r["score_em"] for r in sh) / len(sh) if sh else 0,
        "f1_short": sum(r["score_f1"] for r in sh) / len(sh) if sh else 0,
        "avg_latency": sum(r["latency_s"] for r in results) / len(results),
    }


def main() -> None:
    questions = load_pilot()
    console.print(f"[bold]Pilot: {len(questions)} preguntas[/bold]\n")

    summaries = []
    for model in MODELS:
        console.print(f"\n[cyan]Evaluando {model}...[/cyan]")
        try:
            report = evaluate_model(model, questions)
        except Exception as e:
            console.print(f"[red]Error con {model}: {e}[/red]")
            continue

        # Guardar raw
        out = RESULTS_DIR / f"{model.replace('/', '_')}.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        console.print(f"  Raw guardado en {out}")

        summaries.append(summarize(report))

    # Tabla
    table = Table(title="Pilot — resumen")
    table.add_column("Model", style="cyan")
    table.add_column("MC acc", justify="right", style="green")
    table.add_column("SHORT EM", justify="right", style="green")
    table.add_column("SHORT F1", justify="right", style="green")
    table.add_column("Latencia (s)", justify="right")

    for s in summaries:
        table.add_row(
            s["model"],
            f"{s['acc_mc']:.2%}",
            f"{s['em_short']:.2%}",
            f"{s['f1_short']:.3f}",
            f"{s['avg_latency']:.2f}",
        )
    console.print(table)


if __name__ == "__main__":
    main()
