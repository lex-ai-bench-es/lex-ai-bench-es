"""Schema del dataset lex-ai-bench-es.

Cada pregunta debe validar contra `Question`. La validacion es estricta:
campos extra rechazados, tipos rigurosos, constraints semanticos.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Norm(str, Enum):
    AI_ACT = "AI_ACT"
    RGPD = "RGPD"
    AIACT_RGPD = "AIACT_RGPD"


class TaskType(str, Enum):
    MC = "MC"  # multiple choice 4 opciones
    SHORT = "SHORT"  # respuesta corta extractiva


class BloomLevel(str, Enum):
    L1 = "L1"  # memorizacion
    L2 = "L2"  # comprension
    L3 = "L3"  # aplicacion


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Split(str, Enum):
    DEV = "dev"
    TEST_PUBLIC = "test_public"
    TEST_PRIVATE = "test_private"


class MCOptions(BaseModel):
    """Opciones de un MC. Exactamente 4."""

    model_config = ConfigDict(extra="forbid")

    A: str = Field(..., min_length=1, max_length=300)
    B: str = Field(..., min_length=1, max_length=300)
    C: str = Field(..., min_length=1, max_length=300)
    D: str = Field(..., min_length=1, max_length=300)

    @model_validator(mode="after")
    def options_must_differ(self) -> MCOptions:
        opts = [self.A, self.B, self.C, self.D]
        if len(set(opts)) != 4:
            raise ValueError("Las 4 opciones deben ser distintas entre si")
        return self


class Question(BaseModel):
    """Una pregunta del benchmark."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    # Identidad
    id: str = Field(..., pattern=r"^laibe-\d{4}$")  # laibe-0001, laibe-0002, ...
    version: str = Field(default="0.1.0")

    # Contenido
    question: str = Field(..., min_length=20, max_length=1000)
    task_type: TaskType

    # Para MC
    options: MCOptions | None = None
    correct_option: str | None = Field(None, pattern=r"^[ABCD]$")

    # Para SHORT
    gold_answer: str | None = Field(None, min_length=1, max_length=200)
    aliases: list[str] = Field(default_factory=list)

    # Explicacion (siempre obligatoria)
    gold_explanation: str = Field(..., min_length=20, max_length=2000)

    # Anclaje normativo (siempre obligatorio)
    norm: Norm
    article_refs: list[str] = Field(..., min_length=1)
    source_quote: str = Field(..., min_length=20, max_length=500)

    # Metadatos taxonomicos
    bloom_level: BloomLevel
    difficulty: Difficulty
    language: str = Field(default="es-ES", pattern=r"^es-[A-Z]{2}$")

    # Trazabilidad
    created_by: str = Field(..., min_length=1)
    created_at: str  # ISO 8601: 2026-06-15
    reviewed_by: str | None = None
    reviewed_at: str | None = None

    # Split y notas
    split: Split | None = None
    annotator_notes: str | None = None

    @model_validator(mode="after")
    def mc_requires_options(self) -> Question:
        if self.task_type == TaskType.MC.value:
            if self.options is None or self.correct_option is None:
                raise ValueError("MC requiere 'options' y 'correct_option'")
            if self.gold_answer is not None:
                raise ValueError("MC no debe tener 'gold_answer'")
        return self

    @model_validator(mode="after")
    def short_requires_gold(self) -> Question:
        if self.task_type == TaskType.SHORT.value:
            if self.gold_answer is None:
                raise ValueError("SHORT requiere 'gold_answer'")
            if self.options is not None or self.correct_option is not None:
                raise ValueError("SHORT no debe tener 'options' ni 'correct_option'")
        return self

    @field_validator("article_refs")
    @classmethod
    def article_refs_format(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("article_refs no puede estar vacio")
        for ref in v:
            if "Art." not in ref:
                raise ValueError(
                    f"article_ref '{ref}' debe contener 'Art.' (ej: 'Art. 6.1.b RGPD')"
                )
        return v
