# Plantillas de prompts — evaluacion

Versionadas. Cualquier cambio aqui requiere bump de version y
documentacion en el changelog del paper.

## Version: 1.0 (Fase 1)

---

## Prompt MC — version es-ES, 0-shot

```
Responde a la siguiente pregunta de regulacion europea. Selecciona la
unica opcion correcta entre A, B, C, D. Responde SOLO con la letra de
la opcion correcta, sin justificacion.

Pregunta: {question}

A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

Respuesta:
```

## Prompt MC — version es-ES, 5-shot

Mismo prompt, precedido de 5 ejemplos del split DEV con su respuesta
correcta. Los 5 ejemplos se eligen aleatoriamente con seed fijo (42).

## Prompt SHORT — version es-ES, 0-shot

```
Responde a la siguiente pregunta de regulacion europea. La respuesta es
una expresion corta (plazo, numero de articulo, nombre de institucion,
etc.). Responde SOLO con la expresion, sin justificacion ni explicacion.

Pregunta: {question}

Respuesta:
```

## Prompt SHORT — version es-ES, 5-shot

Igual que MC 5-shot pero con ejemplos SHORT del DEV.

---

## Parametros de inferencia

| Parametro | Valor |
|---|---|
| temperature | 0.0 |
| top_p | 1.0 |
| max_new_tokens (MC) | 5 |
| max_new_tokens (SHORT) | 30 |
| seed | 42 |
| repetition_penalty | 1.0 |

## Notas

- Todos los prompts en espanol. La ablacion EN se hace traduciendo el
  prompt mecanicamente pero manteniendo question y options en espanol.
- El prompt NO menciona "Union Europea" ni "AI Act" explicitamente para
  no dar pistas. La normativa se infiere del contenido.
- Para SHORT, max_tokens deliberadamente bajo: forzamos respuestas cortas.
