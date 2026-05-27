"""Plantillas de prompts versionadas.

Si modificas algo aqui, sube la version y deja la version vieja como
PROMPT_MC_V1_0 (con el numero), etc.
"""

from __future__ import annotations

PROMPT_VERSION = "1.0"


PROMPT_MC_ES_0SHOT = """Responde a la siguiente pregunta de regulacion europea. Selecciona la unica opcion correcta entre A, B, C, D. Responde SOLO con la letra de la opcion correcta, sin justificacion.

Pregunta: {question}

A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

Respuesta:"""


PROMPT_SHORT_ES_0SHOT = """Responde a la siguiente pregunta de regulacion europea. La respuesta es una expresion corta (plazo, numero de articulo, nombre de institucion, etc.). Responde SOLO con la expresion, sin justificacion ni explicacion.

Pregunta: {question}

Respuesta:"""


def format_mc(question: str, options: dict[str, str]) -> str:
    """Formatea un prompt MC 0-shot listo para enviar al modelo."""
    return PROMPT_MC_ES_0SHOT.format(
        question=question,
        option_a=options["A"],
        option_b=options["B"],
        option_c=options["C"],
        option_d=options["D"],
    )


def format_short(question: str) -> str:
    """Formatea un prompt SHORT 0-shot listo para enviar al modelo."""
    return PROMPT_SHORT_ES_0SHOT.format(question=question)


INFERENCE_DEFAULTS = {
    "MC": {
        "temperature": 0.0,
        "top_p": 1.0,
        "max_new_tokens": 5,
        "seed": 42,
        "repetition_penalty": 1.0,
    },
    "SHORT": {
        "temperature": 0.0,
        "top_p": 1.0,
        "max_new_tokens": 30,
        "seed": 42,
        "repetition_penalty": 1.0,
    },
}
