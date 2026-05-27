# Paper outline — lex-ai-bench-es

**Target venue (primary)**: NeurIPS 2026 Datasets and Benchmarks Track (deadline mayo-junio)
**Target venue (backup)**: ACL Rolling Review -> ACL/EMNLP/NAACL 2026 Resources track
**Length target**: 9 pages main + unlimited appendix

## Sections

### 1. Introduction (1 page)
- Hook: EU regulatory landscape, AI Act + GDPR
- Gap: no Spanish-language regulatory benchmark for open-source LLMs
- Contributions (5 bullets)

### 2. Related work (0.75 page)
- Spanish/Iberian benchmarks: IberBench, IberoBench, La Leaderboard
- Legal benchmarks: LegalBench, LawBench, LegiLM
- Safety/compliance: Safety Compliance benchmark, "Can We Trust AI to Govern AI?"
- Red-teaming: AdvBench, HarmBench, multilingual jailbreaks

### 3. Dataset construction (1.5 pages)
- Sources (EUR-Lex official texts)
- Taxonomy: norm x Bloom level x format
- Pipeline: LLM-assisted generation -> manual rewrite -> double annotation
- Inter-annotator agreement (Cohen kappa reported)
- Decontamination check
- Splits: dev / public-test / private-test

### 4. Evaluation methodology (1.5 pages)
- Models evaluated (8)
- Inference setup (vLLM, FP16, temperatures, seeds)
- Metrics per task type
- LLM-judge: Llama-3.3-70B via Groq, calibration vs humans
- Uncertainty quantification (bootstrap)

### 5. Red-teaming methodology (1 page)
- AdvBench-ES construction
- Categories (ALERT taxonomy)
- ASR, refusal quality, safety classifier

### 6. Results (2 pages)
- Main table: accuracy per model x task type x norm
- Ablations: 0-shot vs 5-shot, ES vs EN prompt
- LLM-judge calibration (kappa human-LLM)
- Red-teaming heatmap

### 7. Analysis (1 page)
- Where do models fail? (error clusters)
- Spanish vs English degradation
- Open-source vs Spanish-specific models

### 8. Limitations (0.5 page)
- Single language variant (Iberian Spanish)
- Two norms only
- Judge is an LLM (limited human verification)
- No case law

### 9. Ethical considerations (0.5 page)
- Red-teaming dataset gated release
- Not a substitute for legal advice

### 10. Conclusion + future work (0.25 page)

### Appendices
- A. Annotation guide
- B. Prompts (eval + judge)
- C. Per-model detailed results
- D. Dataset card (datasheet for datasets)
- E. Reproducibility checklist
