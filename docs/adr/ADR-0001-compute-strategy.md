# ADR-0001: Estrategia de computo

## Status
Accepted (Fase 0)

## Context
Necesitamos correr ~10M tokens de inferencia distribuidos en 8 modelos x 500 preguntas
x ~4 condiciones (0-shot, 5-shot, prompt ES, prompt EN).

Estimacion de costes:
- GPU A100 spot (RunPod ~0.70$/h): ~20h totales = ~14$ para todos los modelos.
- Colab/Kaggle free: 0$, pero hay que ir modelo a modelo en sesiones de 3-4h.
- Groq free tier (juez): 500k tokens/dia de Llama-3.3-70B, suficiente en ~4 dias.

## Decision
- Fases 0, 1, 2: sin GPU. CPU local + Groq free para el juez.
- Fase 3 (implementacion): Colab T4 free para smoke tests del pipeline.
- Fase 4 (evaluacion): Colab/Kaggle si la paciencia lo permite; alternativa A100 spot
  si se necesita reproducibilidad estricta en un unico entorno (~14$ total).

## Consequences
- Si usamos Colab/Kaggle, documentamos la GPU exacta asignada en cada sesion.
- El coste total del proyecto queda entre 0 y 20$.
