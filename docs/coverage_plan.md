# Plan de cobertura — version razonada (post-analisis longitudes)

## Metodologia de asignacion

El reparto de preguntas por bloque combina dos criterios:

1. **Proporcionalidad a la longitud del articulado**: medida en
   caracteres del texto oficial extraido de EUR-Lex (script
   `analyze_block_lengths.py`). Se aplica suelo minimo de 5 preguntas
   por bloque y metodo largest-remainder para que la suma cuadre exacta.

2. **Densidad regulatoria cualitativa**: ajustes manuales para
   bloques cortos en chars pero densos en obligaciones, derechos,
   sanciones, o numerologia evaluable (umbrales, plazos, porcentajes).

Criterios de ajuste por magnitud de discrepancia entre reparto a ojo
y reparto proporcional:

- **Señal baja** (<30%): mantener reparto a ojo.
- **Señal MEDIA** (30-50%): desempatar con criterio cualitativo.
  Alta densidad regulatoria (obligaciones, sanciones, derechos) ->
  mantener a ojo. Procedimental/administrativo -> ajustar hacia longitud.
- **Señal ALTA** (>50%): ajustar hacia longitud salvo justificacion
  expresa (artefacto de datos o contenido de escasa evaluabilidad L2/L3).

Nota metodologica sobre artefactos de datos: el articulo 113 del AI Act
presentaba 162.422 chars en el JSONL porque el parser concateno todos los
Anexos del Reglamento dentro de dicho articulo. Su asignacion se mantiene
a ojo (5 preguntas), ignorando el valor del algoritmo (19). Efecto parcial
similar en Art. 59 RGPD (52K chars por inclusion del Cap. VII); la
asignacion del bloque "Autoridades de control" se determino contando solo
Arts. 51-58 con contenido sustantivo.

## Reparto final — AI Act (150 preguntas: 120 MC + 30 SHORT)

| Bloque | Articulos | Preguntas | Señal | Justificacion |
|---|---|---|---|---|
| Disposiciones generales | 1-4 | 10 | MEDIA | Arts. 2 (ambito, exclusiones) y 3 (60+ definiciones) tienen alta densidad L1/L2; +2 sobre a ojo |
| Practicas prohibidas | 5 | 15 | baja | 8 practicas prohibidas distintas, alto valor evaluable L2/L3; mantener a ojo |
| Sistemas de alto riesgo (clasif) | 6-7 + Anexo III | 15 | ALTA | Solo 2 arts. (48K chars); a ojo (25) sobreestimaba; 15 evita saturacion con variaciones repetitivas de clasificacion |
| Requisitos sistemas alto riesgo | 8-15 | 25 | MEDIA | 8 obligaciones tecnicas distintas (riesgo, datos, docs, logs, transparencia, supervision, robustez); maxima densidad regulatoria |
| Obligaciones proveedores y deployers | 16-27 | 20 | baja | Mantener a ojo |
| Autoridades notificantes y organismos | 28-39 | 10 | ALTA | 12 arts. procedimentales; ajuste moderado (+2) sobre a ojo, por debajo del algoritmo (14) |
| Modelos GPAI | 51-56 | 20 | baja | Mantener a ojo |
| Sandboxes regulatorios | 57-63 | 11 | ALTA | Arts. 59 (datos personales en sandbox), 60 (pruebas reales) y 63 (PYMEs) con sustancia evaluable; tope bajo el algoritmo (16) por caracter mixto |
| Gobernanza | 64-69 | 9 | MEDIA | Institucional-procedimental (Oficina IA, Consejo IA, foro consultivo); regla ajuste hacia algoritmo |
| Sanciones | 99 | 10 | MEDIA | 3 niveles de multa (35M/15M/7,5M o 7%/3%/1,5%) + 11 criterios de graduacion; numerologia rica; mantener a ojo |
| Entrada en vigor | 113 | 5 | ALTA* | *Algoritmo invalido (162K chars por concatenacion de Anexos); 5 preguntas L1 de plazos de aplicacion escalonada |

**Total AI Act: 150** (120 MC + 30 SHORT segun D1)

## Reparto final — RGPD (120 preguntas: 96 MC + 24 SHORT)

| Bloque | Articulos | Preguntas | Señal | Justificacion |
|---|---|---|---|---|
| Disposiciones generales y ambito | 1-3 | 6 | baja | Mantener a ojo |
| Principios | 5 | 10 | MEDIA | 7 principios nombrados con alta densidad conceptual; -2 sobre a ojo por concentracion en articulo unico |
| Bases juridicas | 6-10 | 12 | MEDIA | Arts. 6 (6 bases) y 9 (categorias especiales) muy evaluables; a ojo (18) sobreestimaba; 12 cubre calidad sin redundancia. Reduccion absorbe incremento de bloques ALTA |
| Derechos del interesado | 12-23 | 25 | baja | Mantener a ojo |
| Obligaciones responsable y encargado | 24-31 | 15 | baja | Mantener a ojo |
| Seguridad y brechas | 32-34 | 10 | baja | Mantener a ojo |
| DPIA y DPO | 35-39 | 10 | baja | Mantener a ojo |
| Transferencias internacionales | 44-50 | 12 | baja | Mantener a ojo |
| Autoridades de control | 51-59 | 11 | ALTA | Arts. 55 (competencia), 56 (one-stop-shop), 57 (funciones), 58 (poderes) muy testables; a ojo (6) infraestimaba |
| Recursos y sanciones | 77-84 | 9 | ALTA | Art. 83 (multas 2%/4%, criterios de graduacion) muy evaluable; Art. 82 (responsabilidad) sustantivo; a ojo (6) claramente bajo |

**Total RGPD: 120** (96 MC + 24 SHORT segun D1)

## Reparto final — Interseccion AI Act x RGPD (30 preguntas)

Distribuido tematicamente:

| Tema de interseccion | Preguntas |
|---|---|
| Tratamiento de datos en entrenamiento de IA | 6 |
| Decisiones automatizadas (Art. 22 RGPD vs alto riesgo AI Act) | 6 |
| Sandboxes regulatorios y proteccion de datos | 5 |
| DPIA en sistemas de IA de alto riesgo | 5 |
| Transparencia en ambas normas | 4 |
| Sanciones acumulativas | 4 |

**Total interseccion: 30**

## Validacion posterior

Tras Fase 2 (generacion de las 300 preguntas), comparar:

- Distribucion real (preguntas generadas) vs este plan.
- Tolerancia: +/-20% por bloque sin justificacion adicional.
- Desviaciones mayores se documentan en el changelog del dataset.
