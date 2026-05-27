"""Tests de evaluacion: parser MC y metricas SHORT."""

from __future__ import annotations

import pytest

from ai_act_rgpd_es.evaluation import (
    normalize_text,
    parse_mc_response,
    score_mc,
    score_short_exact,
    score_short_f1,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("A", "A"),
        ("a", "A"),
        (" B ", "B"),
        ("La respuesta es C.", "C"),
        ("D)", "D"),
        ("Opcion B: porque...", "B"),
        ("No lo se", None),
        ("", None),
        ("E", None),
    ],
)
def test_parse_mc_response(raw, expected):
    assert parse_mc_response(raw) == expected


def test_score_mc():
    assert score_mc("A", "A") == 1
    assert score_mc("B", "A") == 0
    assert score_mc(None, "A") == 0


def test_normalize_text():
    assert normalize_text("72 Horas.") == "72 horas"
    assert normalize_text("  Cuarenta y CINCO  dias  ") == "cuarenta y cinco dias"
    assert normalize_text("Articulo Numero 6") == "articulo numero 6"


@pytest.mark.parametrize(
    "pred,gold,aliases,expected",
    [
        ("72 horas", "72 horas", [], 1),
        ("72h", "72 horas", ["72h", "setenta y dos horas"], 1),
        ("Setenta y dos horas", "72 horas", ["setenta y dos horas"], 1),
        ("70 horas", "72 horas", ["72h"], 0),
        ("72 HORAS.", "72 horas", [], 1),
    ],
)
def test_score_short_exact(pred, gold, aliases, expected):
    assert score_short_exact(pred, gold, aliases) == expected


def test_score_short_f1_partial():
    # Match parcial: comparte algunos tokens
    score = score_short_f1("72 dias", "72 horas")
    assert 0 < score < 1


def test_score_short_f1_full_match():
    assert score_short_f1("72 horas", "72 horas") == 1.0
