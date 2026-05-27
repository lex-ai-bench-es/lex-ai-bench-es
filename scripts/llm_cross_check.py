"""Cross-check de preguntas: dos LLMs externos juzgan si cada pregunta
es correcta y la respuesta gold es la apropiada, dada la source_quote.

Output: data/interim/cross_check_results.jsonl
Discrepancias se marcan para revision manual.
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

from ai_act_rgpd_es.schema import Question

load_dotenv()
console = Console()

JUDGES = [
    "llama-3.3-70b-versatile",
    "qwen/qwen3-32b",
]

_THINKING_MODELS = {"qwen/qwen3-32b"}
_THINKING_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

PILOT_PATH = Path("data/interim/pilot_questions.jsonl")
OUT_PATH = Path("data/interim/cross_check_results.jsonl")


PROMPT_TEMPLATE = """Eres un revisor experto en regulacion europea (AI Act, RGPD).

Te paso una pregunta de un benchmark y la cita literal del texto normativo
en que se basa. Tu trabajo es decir si la pregunta esta bien formulada y
si la respuesta marcada como correcta es realmente la apropiada.

PREGUNTA:
{question}

{options_block}

RESPUESTA MARCADA COMO CORRECTA:
{gold}

EXPLICACION DEL GOLD:
{explanation}

ANCLAJE NORMATIVO:
- Articulos referenciados: {refs}
- Cita literal del articulo: "{source_quote}"

Responde SOLO con un JSON valido con esta estructura exacta:
{{
  "question_well_formed": true/false,
  "gold_answer_correct": true/false,
  "issue": "descripcion breve del problema si lo hay, o null"
}}"""


def build_prompt(q: Question) -> str:
    if q.task_type == "MC":
        opts = q.options.model_dump()
        options_block = (
            f"OPCIONES:\nA) {opts['A']}\nB) {opts['B']}\n" f"C) {opts['C']}\nD) {opts['D']}"
        )
        gold = f"{q.correct_option}) {opts[q.correct_option]}"
    else:
        options_block = ""
        gold = q.gold_answer or ""

    return PROMPT_TEMPLATE.format(
        question=q.question,
        options_block=options_block,
        gold=gold,
        explanation=q.gold_explanation,
        refs=", ".join(q.article_refs),
        source_quote=q.source_quote,
    )


def judge_with_model(client: Groq, model: str, prompt: str) -> dict:
    max_tokens = 2048 if model in _THINKING_MODELS else 400
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    if model in _THINKING_MODELS:
        raw = _THINKING_RE.sub("", raw).strip()
    return json.loads(raw)


def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    questions = [
        Question.model_validate(json.loads(line))
        for line in PILOT_PATH.open(encoding="utf-8")
        if line.strip()
    ]

    console.print(
        f"[bold]Cross-check de {len(questions)} preguntas con {len(JUDGES)} jueces[/bold]\n"
    )

    results = []
    for q in questions:
        prompt = build_prompt(q)
        judgments = {}
        for judge in JUDGES:
            try:
                j = judge_with_model(client, judge, prompt)
                judgments[judge] = j
                time.sleep(1)
            except Exception as e:
                logger.warning(f"{q.id} con {judge}: {e}")
                judgments[judge] = {"error": str(e)}

        agreements = [
            j.get("question_well_formed") and j.get("gold_answer_correct")
            for j in judgments.values()
            if "error" not in j
        ]
        consensus_ok = all(agreements) if agreements else False

        results.append(
            {
                "id": q.id,
                "consensus_ok": consensus_ok,
                "judgments": judgments,
            }
        )

        marker = "ok" if consensus_ok else "NEEDS REVIEW"
        console.print(f"  {q.id}: {marker}")

    OUT_PATH.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in results),
        encoding="utf-8",
    )

    n_review = sum(1 for r in results if not r["consensus_ok"])
    console.print(f"\nResultado: {len(results) - n_review}/{len(results)} ok")
    if n_review:
        console.print(f"{n_review} preguntas marcadas para revision manual.")
        console.print(f"Detalles en {OUT_PATH}")


if __name__ == "__main__":
    main()
