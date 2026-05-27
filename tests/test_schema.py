"""Tests del schema. Cubren los validators criticos."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_act_rgpd_es.schema import (
    Question,
)


def _base_mc_question(**overrides) -> dict:
    base = {
        "id": "laibe-0001",
        "question": "Cual es la base juridica del RGPD para procesar nominas de empleados?",
        "task_type": "MC",
        "options": {
            "A": "El consentimiento explicito del empleado",
            "B": "El cumplimiento de una obligacion legal del responsable",
            "C": "El interes legitimo del empleador",
            "D": "La proteccion de intereses vitales del empleado",
        },
        "correct_option": "B",
        "gold_explanation": "El tratamiento de datos para nominas se basa en obligacion legal (Art. 6.1.c) y ejecucion del contrato (Art. 6.1.b), no en consentimiento.",
        "norm": "RGPD",
        "article_refs": ["Art. 6.1.b RGPD", "Art. 6.1.c RGPD"],
        "source_quote": "El tratamiento solo sera licito si se cumple al menos una de las siguientes condiciones: ... b) el tratamiento es necesario para la ejecucion de un contrato",
        "bloom_level": "L2",
        "difficulty": "medium",
        "created_by": "autor1",
        "created_at": "2026-06-15",
    }
    base.update(overrides)
    return base


def _base_short_question(**overrides) -> dict:
    base = {
        "id": "laibe-0002",
        "question": "Cual es el plazo maximo para notificar una brecha de seguridad de datos personales a la autoridad de control segun el RGPD?",
        "task_type": "SHORT",
        "gold_answer": "72 horas",
        "aliases": ["72h", "setenta y dos horas", "72 horas"],
        "gold_explanation": "El Art. 33.1 RGPD establece la notificacion sin dilacion indebida y, a mas tardar, 72 horas despues de tener constancia.",
        "norm": "RGPD",
        "article_refs": ["Art. 33.1 RGPD"],
        "source_quote": "el responsable del tratamiento la notificara a la autoridad de control... sin dilacion indebida y, de ser posible, a mas tardar 72 horas despues",
        "bloom_level": "L1",
        "difficulty": "easy",
        "created_by": "autor1",
        "created_at": "2026-06-15",
    }
    base.update(overrides)
    return base


def test_valid_mc_question():
    q = Question.model_validate(_base_mc_question())
    assert q.task_type == "MC"
    assert q.correct_option == "B"


def test_valid_short_question():
    q = Question.model_validate(_base_short_question())
    assert q.task_type == "SHORT"
    assert q.gold_answer == "72 horas"


def test_mc_without_options_rejected():
    with pytest.raises(ValidationError, match="MC requiere 'options'"):
        Question.model_validate(_base_mc_question(options=None))


def test_mc_with_gold_answer_rejected():
    with pytest.raises(ValidationError, match="MC no debe tener 'gold_answer'"):
        Question.model_validate(_base_mc_question(gold_answer="foo"))


def test_short_without_gold_rejected():
    with pytest.raises(ValidationError, match="SHORT requiere 'gold_answer'"):
        Question.model_validate(_base_short_question(gold_answer=None))


def test_short_with_options_rejected():
    bad = _base_short_question(
        options={"A": "x", "B": "y", "C": "z", "D": "w"},
        correct_option="A",
    )
    with pytest.raises(ValidationError, match="SHORT no debe tener 'options'"):
        Question.model_validate(bad)


def test_duplicate_mc_options_rejected():
    bad = _base_mc_question(options={"A": "misma", "B": "misma", "C": "z", "D": "w"})
    with pytest.raises(ValidationError, match="distintas"):
        Question.model_validate(bad)


def test_invalid_id_format_rejected():
    with pytest.raises(ValidationError):
        Question.model_validate(_base_mc_question(id="bad-id"))


def test_invalid_article_ref_rejected():
    with pytest.raises(ValidationError, match="debe contener 'Art.'"):
        Question.model_validate(_base_mc_question(article_refs=["RGPD 6"]))


def test_extra_fields_rejected():
    bad = _base_mc_question()
    bad["unexpected_field"] = "boom"
    with pytest.raises(ValidationError):
        Question.model_validate(bad)
