# Archivo de Resultados y Queries Antiguas

Este directorio contiene archivos obsoletos y versiones anteriores de resultados y queries que han sido reemplazados por versiones más actuales.

## Archivos Archivados

### Resultados Obsoletos (de /results)
- `results_method1_enhanced_FINAL_zero_syntax_errors.jsonl` (Feb 15, 2026)
- `results_method1_enhanced_v3.jsonl` (Feb 14, 2026)
- `results_method1_enhanced_v3_ontology_bm25.jsonl` (Feb 15, 2026)
- `results_method1_enhanced_v4_zero_errors.jsonl` (Feb 15, 2026)

**Razón**: Estos archivos son versiones intermedias. Las versiones actuales y oficiales están en:
- `../results/results_method1_enhanced_v3.jsonl`
- `../results/results_bm25_baseline_v3.jsonl`
- `../results/results_llm_only_v3.jsonl`

### Queries Antiguas
- `queries.jsonl` - Dataset inicial con ~12 queries
- `queries_original_12.jsonl` - Backup del dataset original

**Razón**: Reemplazados por `../queries_90.jsonl` que contiene 90 queries categorizadas para evaluación académica rigurosa.

## Archivos Activos (NO archivados)

Los siguientes archivos están actualmente en uso:
- `../queries_90.jsonl` - Benchmark actual (90 queries)
- `../results/results_*_v3.jsonl` - Resultados de evaluación actual
- `../evaluation_pipeline_v3.ipynb` - Pipeline de evaluación actual

## Política de Archivado

Los archivos se mueven aquí en lugar de eliminarse para:
1. Mantener historial de desarrollo
2. Permitir comparaciones con versiones anteriores si es necesario
3. Reproducibilidad de experimentos históricos

**Fecha de archivado**: 17 de febrero, 2026
