"""Smoke tests para validar instalacion. No requieren GPU ni descargas grandes."""

from __future__ import annotations


def test_import_datasets() -> None:
    import datasets

    assert datasets.__version__ >= "3.0.0"


def test_import_lm_eval() -> None:
    import lm_eval

    assert hasattr(lm_eval, "simple_evaluate")


def test_import_inspect_ai() -> None:
    from inspect_ai import task

    assert task is not None


def test_import_groq() -> None:
    from groq import Groq

    assert Groq is not None


def test_env_loaded() -> None:
    """Verifica que .env carga sin errores."""
    import os

    from dotenv import load_dotenv

    load_dotenv()
    assert os.environ.get("PATH") is not None
