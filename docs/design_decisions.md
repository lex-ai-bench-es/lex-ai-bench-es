# Design Decisions — lex-ai-bench-es (Phase 1)

Documento vivo con las decisiones de diseño congeladas. Cualquier cambio
posterior requiere un ADR (Architecture Decision Record) en docs/adr/.

## D1 — Tamaño y composición del dataset

- **Total**: 300 preguntas validadas.
- **Multiple-choice (MC)**: 240 preguntas (80%).
- **Respuesta corta extractiva (SHORT)**: 60 preguntas (20%).
- **Respuesta abierta razonada**: 0. Eliminada para simplificar metodología.

Razón: balance entre profundidad analítica y simplicidad metodológica.
MC permite evaluación 100% automática; SHORT añade un ángulo de análisis
(reconocimiento vs recuperación abierta) sin necesidad de LLM-judge calibrado.

## D2 — Formato multiple-choice

- **Número de opciones**: 4 (A, B, C, D).
- **Una sola respuesta correcta** por pregunta (no multi-correct).
- **Distractores plausibles**: no opciones absurdas (tipo "Marte"). Los
  distractores deben ser conceptos jurídicos reales del mismo dominio.
- **Posición de la respuesta correcta**: aleatorizada uniformemente
  (~25% en cada posición).

## D3 — Formato respuesta corta extractiva

- Respuesta esperada: un literal corto (1–8 palabras) extraíble del texto
  normativo: número de artículo, plazo, umbral monetario, nombre de
  institución, etc.
- Cada pregunta lleva una lista de **aliases válidos** para normalización.
  Ejemplo: gold="45 días naturales", aliases=["45 días", "cuarenta y
  cinco días", "45 días naturales"].
- Evaluación: exact match sobre forma normalizada (lowercase, sin
  acentos, sin puntuación) + F1 token-level como métrica complementaria.

## D4 — Distribución por norma

- **AI Act (Reglamento UE 2024/1689)**: 50% = 150 preguntas
  (120 MC + 30 SHORT).
- **RGPD (Reglamento UE 2016/679)**: 40% = 120 preguntas
  (96 MC + 24 SHORT).
- **Intersección AI Act × RGPD**: 10% = 30 preguntas (24 MC + 6 SHORT).

## D5 — Distribución por nivel cognitivo (Bloom adaptado)

- **L1 Memorización** (artículos, plazos, definiciones literales): 40%.
- **L2 Comprensión** (qué significa, qué disposición aplica): 40%.
- **L3 Aplicación** (dado un escenario, qué obligaciones se activan): 20%.

Razón para limitar L3 al 20% sin revisor jurídico: las preguntas de
aplicación son las más propensas a errores conceptuales sutiles. Sin
experto externo, mantenemos un volumen donde podemos verificar
nosotros mismos contra el texto oficial con confianza.

## D6 — Variedad lingüística

- **Español ibérico (España)**, registro jurídico-administrativo.
- Etiquetado `language="es-ES"` en cada pregunta para permitir
  ampliaciones LATAM en versiones futuras.

## D7 — Anclaje normativo

Cada pregunta DEBE llevar:
- `norm`: "AI_ACT" | "RGPD" | "AIACT_RGPD"
- `article_refs`: lista de strings con artículo y punto exacto.
  Ej: ["Art. 6.1.b RGPD", "Art. 6.1.c RGPD"].
- `source_quote`: extracto literal del texto normativo (≤200
  caracteres) que sustenta la respuesta. Para verificación
  posterior por cualquiera.

## D8 — Splits

- **Dev público**: 60 preguntas (20%). Para iteración y debug.
- **Test público**: 120 preguntas (40%). Va al leaderboard.
- **Test privado**: 120 preguntas (40%). Servido por endpoint.

Estratificación cruzada: cada split mantiene proporciones de D4 y D5.

## D9 — Anti-contaminación

- Preguntas escritas con redacción ORIGINAL, no copy-paste del
  reglamento.
- Énfasis en L2/L3 (comprensión y aplicación) frente a L1 puro.
- Decontamination check en Fase 2: probar si modelos completan
  el prompt sin contexto (técnica Sainz et al.).

## D10 — Proceso de verificación sin revisor externo

Tres salvaguardas que sustituyen al revisor jurídico:

1. **Anclaje obligatorio**: cada pregunta tiene `article_refs` y
   `source_quote` verificables contra EUR-Lex.
2. **Doble pasada propia con espacio temporal**: escribir pregunta
   en sesión A, revisar y validar en sesión B con al menos 5 días
   de separación.
3. **Cross-check con dos LLMs independientes**: dos modelos
   diferentes (Claude y GPT, por ejemplo) reciben la pregunta + el
   texto oficial y devuelven si la pregunta es correcta y la
   respuesta gold es la apropiada. Discrepancias se revisan
   manualmente.

## D11 — Métricas reportadas

Para MC:
- Accuracy global y por estratos (D4, D5).
- Accuracy norm (proporción de la longitud, para modelos pequeños).
- Bootstrap CI 95% con N=1000 resamples.

Para SHORT:
- Exact Match (EM) sobre forma normalizada.
- F1 token-level.
- Acierto-con-aliases (proporción que matchea cualquier alias).

Para análisis comparativo:
- McNemar pareado entre cada par de modelos.
- Effect size (Cohen's h) además de p-values.

## D12 — Método de asignación de preguntas por bloque temático

El reparto por bloque combina proporcionalidad a la longitud del
articulado y ajustes cualitativos por densidad regulatoria. Se
documenta en `docs/coverage_plan_v2.md`.

**Paso 1 — Baseline proporcional**: longitud en caracteres de cada
artículo oficial (EUR-Lex, ES). Suelo de 5 preguntas/bloque.
Método largest-remainder para que la suma cuadre exacta
(150 AI Act, 120 RGPD).

**Paso 2 — Señal de discrepancia** entre baseline y reparto a ojo:
- Baja (<30%): mantener a ojo.
- MEDIA (30-50%): criterio cualitativo caso por caso.
- ALTA (>50%): ajustar hacia longitud salvo excepción justificada.

**Paso 3 — Criterio cualitativo para MEDIA**:
- Alta densidad regulatoria (obligaciones, sanciones, derechos)
  → mantener a ojo.
- Procedimental/administrativo → ajustar hacia longitud.

**Excepciones documentadas**:
- Art. 113 AI Act: parser concatenó todos los Anexos del Reglamento
  dentro del artículo (162K chars). Algoritmo inválido; se mantiene
  a ojo (5 preguntas).
- Art. 59 RGPD: parser incluyó el Capítulo VII (Arts. 60-76) en el
  texto del artículo. El bloque "Autoridades de control" se evaluó
  sobre Arts. 51-58 únicamente.

Scripts: `scripts/analyze_block_lengths.py`,
`scripts/compare_allocations.py`.

---

## D12 — Distribucion por bloque (decidida en Fase 1)

La asignacion final del numero de preguntas por bloque tematico
combina dos criterios:

1. Reparto inicial proporcional a la longitud del articulado oficial
   (chars del texto en EUR-Lex), con un suelo de 5 preguntas por
   bloque para garantizar cobertura tematica.
2. Ajustes manuales hacia arriba en bloques de alta densidad
   regulatoria (practicas prohibidas, principios, sanciones, derechos
   del interesado), donde articulos cortos generan muchas preguntas
   evaluables por su numerologia (umbrales, plazos, porcentajes) y
   por la cantidad de obligaciones por unidad de texto.

Los ajustes manuales no exceden el 30 por ciento de desviacion respecto
al reparto proporcional puro. Esta tolerancia se justifica por la
naturaleza desigual de los textos juridicos europeos: la longitud no
es proxy perfecto del contenido evaluable.

Reparto final en docs/coverage_plan.md.

El analisis de longitudes y la comparativa estan en:
- scripts/analyze_block_lengths.py
- scripts/compare_allocations.py
- data/interim/coverage_allocation.json
