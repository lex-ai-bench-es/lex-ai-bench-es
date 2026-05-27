# Guia de generacion de preguntas — lex-ai-bench-es

Documento operativo. Aplicable a cada pregunta escrita.

## Principio fundamental

Cada pregunta DEBE poder responderse y verificarse SOLO con el texto
oficial de EUR-Lex. No vale interpretar, no vale meter doctrina, no
vale mezclar legislacion nacional (LOPDGDD) salvo en preguntas
explicitamente marcadas como interseccion.

## Reglas duras (no negociables)

1. **Una sola respuesta correcta.** Si dos opciones de un MC son
   defendibles, la pregunta esta mal formulada.

2. **Anclaje preciso.** Cada pregunta lleva al menos un
   `article_refs` (formato `Art. N.x.y NORMA`) y un `source_quote`
   con texto literal extraido del articulo.

3. **Redaccion original.** La pregunta NO puede ser copy-paste
   verbatim del articulo. El texto del articulo va en `source_quote`,
   no en `question`. Esto es critico para anti-contaminacion.

4. **Distractores plausibles.** En MC, los distractores deben ser
   conceptos del mismo dominio que un humano no experto podria
   confundir. No "Marte" como distractor de "responsable del
   tratamiento".

5. **No truco linguistico.** La pregunta no debe depender de un
   matiz de redaccion ambiguo. Si necesitas leer dos veces la
   pregunta para saber que pide, esta mal escrita.

6. **Idioma neutro.** Evita modismos espanoles, refranes, o
   construcciones muy informales. Espanol juridico-administrativo.

## Reglas blandas (preferibles)

- Variar el tipo de "quien": no todas las preguntas con sujeto
  "responsable del tratamiento". Mezclar deployer, proveedor,
  interesado, autoridad, encargado.

- Variar el tipo cognitivo dentro del bloque. Si haces 5 preguntas
  del Art. 5 RGPD, no las 5 L1.

- Para SHORT, preferir respuestas con bajo ambiguedad lexica:
  numeros, plazos, articulos. Evitar respuestas que admitan muchas
  parafrasis ("derecho de oposicion" vs "derecho a oponerse").

## Checklist por pregunta (mental, rapida)

Cuando escribes una pregunta, antes de meterla al dataset:

- [ ] Tiene `article_refs` con al menos 1 ref formato `Art. N.x NORMA`.
- [ ] Tiene `source_quote` con texto literal del articulo.
- [ ] La pregunta NO contiene el `source_quote` verbatim.
- [ ] Si MC: las 4 opciones son distintas y solo 1 es correcta.
- [ ] Si MC: la respuesta correcta no es siempre B (revisar distribucion
      al final del bloque de generacion).
- [ ] Si SHORT: `gold_answer` tiene aliases razonables anotados.
- [ ] El `bloom_level` esta justificado por la naturaleza de la pregunta:
  - L1: preguntan QUE dice literalmente la norma.
  - L2: preguntan QUE SIGNIFICA o QUE IMPLICA un concepto.
  - L3: dan un escenario y preguntan QUE APLICA.

## Anti-patrones (descartar al verlos)

- "Todas las anteriores" / "Ninguna de las anteriores" como opcion.
  Descarta la pregunta.
- Preguntas cuya respuesta cambia entre AI Act y Acta Espanola
  (LOPDGDD) si no esta marcada como interseccion.
- Preguntas sobre fechas que ya pasaron (ej: "cuando entra en vigor
  el AI Act") salvo que esten en bloque de "Aplicacion y entrada en
  vigor".
- Preguntas sobre la version anterior del RGPD (Directiva 95/46).
- Preguntas con respuesta que depende de jurisprudencia o doctrina
  del EDPB. Solo texto del Reglamento.

## Proceso de doble pasada propia

1. Sesion A: escribes el bloque de preguntas (ej: 30 preguntas
   sobre RGPD principios). Las anotas con `created_at`.
2. ESPERAS al menos 5 dias calendario.
3. Sesion B: relees cada pregunta SIN mirar tus notas previas y la
   resuelves mentalmente. Cualquier duda -> abres el articulo en
   EUR-Lex y verificas. Si tu respuesta no coincide con `correct_option`
   o `gold_answer`, marca la pregunta como "needs_review" y la
   reescribes.
4. Cualquier pregunta que falle el step 3 va a un log:
   `data/interim/needs_review.jsonl`.

## Cross-check con LLMs (opcional pero recomendado)

Pasa la pregunta + `source_quote` por dos LLMs distintos pidiendoles que
juzguen si la pregunta es correcta y la respuesta gold es la apropiada.
Discrepancias -> revision manual.

Script disponible en `scripts/llm_cross_check.py` (Paso 1.10).
