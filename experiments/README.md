# Experimentos y Evaluación

Este directorio contendrá los scripts de evaluación y análisis para las diferentes fases del proyecto.

## Estado: 📅 Planificado para Fase 5 (Semana 8)

## Experimentos Planificados

### 1. Evaluación de Text-to-SPARQL

**Archivo**: `eval_text_to_sparql.py`

Métricas:
- Exactitud sintáctica (queries válidas)
- Exactitud semántica (resultados correctos)
- Cobertura de conceptos
- Tiempo de respuesta

Dataset de prueba:
- 50 consultas naturales anotadas
- Ground truth SPARQL correspondiente

### 2. Comparación de Métodos de Búsqueda

**Archivo**: `compare_search_methods.py`

Comparar:
- Método 1: Non-federated
- Método 2: Federated
- Método 3: Cross-repository

Métricas:
- Precision@K
- Recall@K
- F1-Score
- Latencia

### 3. Análisis de Cobertura

**Archivo**: `coverage_analysis.py`

Evaluar:
- % modelos con metadatos completos
- Distribución de tareas
- Cobertura de licencias
- Calidad de mapeo a DAIMO

### 4. Análisis de Popularidad vs Relevancia

**Archivo**: `popularity_vs_relevance.py`

Investigar:
- Correlación entre descargas y relevancia
- Sesgo de popularidad en ranking
- Diversidad de resultados

## Formato de Resultados

Los experimentos generarán:

- **CSV/JSON**: Resultados tabulados
- **Gráficos**: Visualizaciones (matplotlib/seaborn)
- **Reportes**: Markdown con análisis

Ejemplo:
```
experiments/
  results/
    eval_text_to_sparql_2026-01-26.json
    coverage_analysis_2026-01-26.csv
  figures/
    precision_recall_curve.png
    task_distribution.png
```

## Benchmarks

### Test Suite para Text-to-SPARQL

Categorías de consultas:
1. **Simple**: Filtro por una propiedad
2. **Compuesta**: Múltiples filtros
3. **Agregación**: COUNT, AVG, etc.
4. **Comparativa**: Ranking, TOP-K
5. **Provenance**: Modelos derivados, datasets

Ejemplo:
```json
{
  "id": 1,
  "query_nl": "Top 5 modelos de clasificación de imágenes con licencia MIT",
  "query_sparql": "PREFIX daimo: ...",
  "difficulty": "medium",
  "expected_results": 5
}
```

## Reproducibilidad

Todos los experimentos incluirán:
- Seed fijo para aleatoriedad
- Versión de dependencias (Poetry lock)
- Configuración explícita en YAML
- Scripts de ejecución automatizados

## Referencias Académicas

Los resultados se documentarán siguiendo estándares de:
- ACL (para NLP/LLM)
- ISWC (para Semantic Web)
- MLSys (para infraestructura ML)
