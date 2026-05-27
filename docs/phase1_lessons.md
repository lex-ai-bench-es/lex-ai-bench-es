# Phase 1 Lessons Learned

## Que ha funcionado

**Schema Pydantic como guardian de calidad.**
El schema con validadores propios (`options_must_differ`, `mc_requires_options`,
`article_refs_format`) captura errores estructurales antes de que lleguen al pipeline.
Las 20 preguntas del pilot pasaron validacion en el primer intento tras corregir
el formato de `Anexo III.4` (no contenia "Art.", rechazado por el validador).
Esto justifica el coste de definir el schema en Fase 1 en lugar de usar dicts crudos.

**Cross-check LLM como sustituto parcial del revisor juridico.**
Con 2 jueces (llama-3.3-70b-versatile y qwen/qwen3-32b) se obtuvo una tasa de
aceptacion del 95% (19/20). El unico disenso identifico una imprecision real:
la pregunta laibe-0013 citaba "Art. 99" cuando el anclaje normativo correspondia
al "Art. 99.3". La imprecision fue corregida antes de usar la pregunta en el pilot
de evaluacion. El juez mas estricto (qwen3) fue mas util que el mas permisivo
(llama-70b), lo que sugiere usar siempre al menos un modelo con tendencia critica.

**Pipeline end-to-end robusto.**
El flujo completo (carga JSONL -> validacion schema -> formateo prompt ->
llamada API -> parseo respuesta -> scoring -> reporte) funciono sin errores
en la primera ejecucion tras resolver el problema de autenticacion de la API.
La separacion en modulos (schema.py, prompts.py, evaluation.py) facilito el
debugging: el fallo de qwen3 se aislo en el parser MC sin tocar el resto.

**Deteccion temprana del problema de thinking tokens.**
Los modelos razonadores (qwen/qwen3-32b) anteponen bloques <think>...</think>
a su respuesta. Con max_tokens=10 la respuesta se cortaba antes de llegar a la
letra MC. La solucion (_THINKING_MODELS + _strip_thinking + max_tokens=2048 para
esos modelos) esta implementada en run_pilot.py y llm_cross_check.py y es
reutilizable en Fase 2 sin cambios adicionales.

**Distribucion del pilot alineada con los objetivos del diseno.**
Las 20 preguntas cumplieron las restricciones de D1-D5 exactamente:
MC/SHORT 80%/20%, RGPD/AI_ACT/interseccion 50%/40%/10%, Bloom L1/L2/L3 sin
sesgos extremos. Esto valida que la guia de generacion (annotation_guide.md) es
operativa como instruccion.


## Que NO ha funcionado

**Aliases insuficientes para respuestas SHORT.**
laibe-0004 (principio de limitacion de la finalidad) obtuvo EM=0 con Llama-3.1-8B
porque el modelo respondio "Principio de finalidad (articulo 5 del RGPD)" --
respuesta correcta en sustancia pero no en forma. El F1=0.5 captura el acierto
parcial, pero el EM=0 infravalora la calidad del modelo. La lista de aliases era
demasiado corta. Para Fase 2: generar aliases de forma mas sistematica, incluyendo
variantes sin articulo de referencia, con y sin "principio de".

laibe-0013 (porcentaje de multa) obtuvo EM=0 porque Llama alucinó "20%" en lugar
de "7%". Este es un error genuino del modelo, no un problema de aliases.
Sin embargo, el cross-check (jueces) no lo detecto como problema de la pregunta
porque la pregunta y el gold son correctos. La alucinacion es un dato valioso:
los umbrales numericos del AI Act (7%, 3%, 1.5%) son un punto de fallo para
modelos pequenos.

**qwen-2.5-32b descatalogado sin aviso previo.**
El modelo configurado como segundo modelo del pilot habia sido retirado del
catalogo de Groq. El pipeline lo capturo con un error 400 controlado (no rompio
el loop), pero obliga a mantener una lista de modelos verificada antes de cada
ejecucion en Fase 2. Solucion: anadir un paso de verificacion de catalogo al
inicio de run_pilot.py.

**Problema de codificacion Windows en Rich console.**
El caracter unicode checkmark (U+2713) no es soportado por el renderer legacy
de Windows (cp1252). Afecto a validate_dataset.py. Solucion: usar
Console(force_terminal=True) y caracteres ASCII en lugar de simbolos Unicode
en todos los scripts de reporting.


## Ajustes a la guia de generacion para Fase 2

1. **Aliases sistematicos en SHORT.** Para cada pregunta SHORT, generar
   al menos 5 aliases que cubran: forma canonica legal, forma abreviada,
   forma numerica (si aplica), forma sin acento, forma con sinonimo comun.

2. **Precision en referencias de articulo en el enunciado.** Si la pregunta
   menciona un articulo en el texto, debe coincidir con el nivel de detalle
   de article_refs (Art. 99.3, no Art. 99). Anadir este punto al checklist
   de annotation_guide.md.

3. **Evitar preguntas sobre umbrales numericos unicos en SHORT.**
   Los numeros concretos (porcentajes, plazos en dias) son los puntos de fallo
   mas frecuentes para modelos pequenos Y los mas sensibles a alucinacion.
   Para Fase 2: usar MC para umbrales numericos con distractores plausibles,
   reservar SHORT para nombres de principios, instituciones y plazos muy
   conocidos (72 horas, 1 mes).

4. **Verificar catalogo de modelos al inicio de cada ejecucion.**
   Anadir llamada a client.models.list() al arranque de run_pilot.py y
   llm_cross_check.py para detectar modelos descatalogados antes de empezar.


## Metricas de referencia del pilot

| Metrica                              | Valor         |
|--------------------------------------|---------------|
| Accuracy MC — llama-3.1-8b-instant   | 93.75% (15/16)|
| Accuracy MC — qwen/qwen3-32b         | 100%  (16/16) |
| EM SHORT — llama-3.1-8b-instant      | 50%   (2/4)   |
| EM SHORT — qwen/qwen3-32b            | 75%   (3/4)   |
| F1 SHORT — llama-3.1-8b-instant      | 0.625         |
| F1 SHORT — qwen/qwen3-32b            | 0.875         |
| Latencia media — llama-3.1-8b        | 0.16 s/pregunta|
| Latencia media — qwen/qwen3-32b      | 4.19 s/pregunta|
| Tasa aceptacion cross-check          | 95.0% (19/20) |
| Preguntas corregidas tras cross-check| 1 (laibe-0013)|

Distribuciones por categoria: ver output de scripts/pilot_analysis.py.
Resultados raw por modelo: results/pilot/*.json.


## Observaciones sobre los modelos evaluados

**llama-3.1-8b-instant:** rendimiento sorprendentemente alto en MC (93.75%)
para un modelo de 8B. El unico fallo fue el umbral de 10^25 FLOPs para riesgo
sistemico en modelos GPAI (Art. 51.1.a AI Act) -- conocimiento muy especifico y
reciente. En SHORT, el modelo alucinó "20%" en lugar de "7%" para la multa maxima
del Art. 99.3, lo que sugiere que los umbrales numericos del AI Act no estan bien
representados en su preentrenamiento.

**qwen/qwen3-32b:** 100% en MC y 75% en SHORT. Mas lento (4x) pero mas preciso.
El modo de razonamiento interno (<think>) requiere manejo especifico en el pipeline.
Su juicio como revisor en el cross-check fue mas estricto que llama-70b, lo que
lo hace preferible como juez en lugar de como modelo evaluado.


## Tiempo invertido (estimado)

| Tarea                                    | Tiempo estimado |
|------------------------------------------|-----------------|
| Diseno schema, prompts y evaluation.py   | 2 h             |
| Analisis de longitudes y reparto bloques | 3 h             |
| Guia de anotacion y plantillas           | 1 h             |
| Escritura 20 preguntas piloto            | 2 h             |
| Pipeline end-to-end + debugging          | 2 h             |
| Cross-check y analisis go/no-go          | 1 h             |
| **Total Fase 1**                         | **~11 h**       |
