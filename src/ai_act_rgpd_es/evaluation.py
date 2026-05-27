"""Logica de evaluacion: parseo de respuestas y metricas.

Critico para reproducibilidad. Si cambias la normalizacion, los numeros
del paper cambian. Cualquier modificacion -> bump version + ADR.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

EVAL_VERSION = "1.0"


def normalize_text(text: str) -> str:
    """Normalizacion estricta: lowercase, sin acentos, sin puntuacion extra."""
    text = text.lower().strip()
    # quitar acentos
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    # colapsar espacios
    text = re.sub(r"\s+", " ", text)
    # quitar puntuacion al inicio/final
    text = text.strip(".,;:!?-()[]{}\"'")
    return text


# ===== MC =====

_MC_LETTER_RE = re.compile(r"\b([ABCD])\b", flags=re.IGNORECASE)


def parse_mc_response(raw: str) -> str | None:
    """Extrae la letra (A/B/C/D) de la respuesta del modelo.

    Estrategia:
    1. Si la respuesta es exactamente una letra A-D (con/sin espacios), devolverla.
    2. Si no, buscar la PRIMERA letra A-D delimitada por word boundary.
    3. Si no aparece ninguna, None.
    """
    stripped = raw.strip().upper()
    if len(stripped) == 1 and stripped in "ABCD":
        return stripped
    match = _MC_LETTER_RE.search(raw)
    return match.group(1).upper() if match else None


def score_mc(predicted_letter: str | None, correct_letter: str) -> int:
    return 1 if predicted_letter == correct_letter else 0


# ===== SHORT =====


def score_short_exact(
    predicted: str,
    gold: str,
    aliases: Iterable[str] = (),
) -> int:
    """1 si normalize(predicted) match normalize(gold) o alguno de los aliases."""
    pred_norm = normalize_text(predicted)
    candidates = [normalize_text(gold)] + [normalize_text(a) for a in aliases]
    return 1 if pred_norm in candidates else 0


def score_short_f1(predicted: str, gold: str, aliases: Iterable[str] = ()) -> float:
    """F1 token-level contra el mejor (gold o alias)."""
    candidates = [gold, *aliases]
    return max(_token_f1(predicted, c) for c in candidates)


def _token_f1(pred: str, gold: str) -> float:
    pred_tokens = normalize_text(pred).split()
    gold_tokens = normalize_text(gold).split()
    if not pred_tokens or not gold_tokens:
        return 0.0
    common = set(pred_tokens) & set(gold_tokens)
    if not common:
        return 0.0
    p = len(common) / len(pred_tokens)
    r = len(common) / len(gold_tokens)
    return 2 * p * r / (p + r)
