"""Verifica conectividad y latencia del juez Groq Llama-3.3-70B."""

from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from groq import Groq
from rich import print

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

PROMPT_TEST = """Eres un evaluador experto en regulacion europea de proteccion de datos.

Pregunta: Cual es la base juridica del RGPD para el tratamiento de datos cuando una
empresa procesa datos de sus empleados para gestionar nominas?

Respuesta del modelo evaluado: "Consentimiento del trabajador."

Evalua si la respuesta es correcta segun el RGPD. Devuelve un JSON con:
- score: 0 (incorrecto), 1 (parcialmente correcto), 2 (correcto)
- reasoning: explicacion breve en espanol

Responde SOLO con el JSON, sin texto adicional."""


def main() -> None:
    print("[bold]Test del juez Groq Llama-3.3-70B[/bold]\n")

    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": PROMPT_TEST}],
        temperature=0.0,
        max_tokens=512,
    )
    elapsed = time.perf_counter() - t0

    content = response.choices[0].message.content
    usage = response.usage

    print(f"[green]Respuesta recibida en {elapsed:.2f}s[/green]")
    print(f"Tokens: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}")
    print(f"\n[bold]Contenido:[/bold]\n{content}")


if __name__ == "__main__":
    main()
