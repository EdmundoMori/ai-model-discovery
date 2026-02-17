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
# 🔬 Evaluación Académica - Método 1 (Text-to-SPARQL)

Este directorio contiene el pipeline completo de evaluación experimental para validar el Método 1 con rigor académico.

## 📁 Estructura

```
benchmarks/
├── EVALUATION_DESIGN.md          # Diseño experimental detallado
├── evaluation_pipeline.ipynb      # 🌟 NOTEBOOK PRINCIPAL - Pipeline interactivo
├── create_snapshot.py             # Script para crear snapshot reproducible
├── validate_benchmark.py          # Script para validar benchmark
├── run_keyword_benchmark.py       # Ejecutar baseline BM25
├── run_text2sparql_benchmark.py   # Ejecutar Método 1
├── keyword_bm25.py                # Implementación baseline
├── metrics.py                     # Funciones de métricas
├── queries.jsonl                  # Benchmark original (12 queries)
├── queries_50.jsonl               # Benchmark expandido (50+ queries)
├── benchmark_schema.md            # Esquema del benchmark
├── snapshot/                      # Snapshot del grafo RDF
│   ├── graph_snapshot.ttl         # Grafo congelado
│   ├── snapshot_metadata.json     # Metadatos + SHA256
│   └── README.md                  # Documentación del snapshot
├── results/                       # Resultados de experimentos
│   ├── results_bm25.jsonl
│   ├── report_bm25.json
│   ├── results_method1_configA.jsonl
│   ├── report_method1_configA.json
│   ├── comparison_table.csv
│   ├── statistical_tests.csv
│   ├── error_analysis.csv
│   └── FINAL_REPORT.md           # 📄 Reporte completo para paper/tesis
└── figures/                       # Gráficos para publicación
    ├── metrics_comparison.png
    ├── latency_comparison.png
    └── performance_by_difficulty.png
```

---

## 🚀 Quickstart

### Opción 1: Notebook Interactivo (Recomendado)

El notebook `evaluation_pipeline.ipynb` contiene TODO el proceso de principio a fin con explicaciones detalladas:

```bash
# Abrir notebook en VS Code o Jupyter
code evaluation_pipeline.ipynb

# O ejecutar con Jupyter
jupyter notebook evaluation_pipeline.ipynb
```

**El notebook incluye:**
1. ✅ Creación de snapshot reproducible
2. ✅ Análisis exploratorio del grafo
3. ✅ Expansión del benchmark a 50 queries
4. ✅ Validación de ground truth
5. ✅ Ejecución automática de todos los benchmarks
6. ✅ Tests estadísticos (paired t-test, confidence intervals)
7. ✅ Análisis de errores cualitativos
8. ✅ Visualizaciones para paper/tesis
9. ✅ Generación de reporte final

### Opción 2: Scripts Individuales

Si prefieres ejecutar cada paso por separado:

#### Paso 1: Crear Snapshot Reproducible

```bash
python create_snapshot.py \
    --source ../../data/ai_models_multi_repo.ttl \
    --output ./snapshot
```

Esto genera:
- `snapshot/graph_snapshot.ttl` (grafo congelado)
- `snapshot/snapshot_metadata.json` (SHA256 + stats)

#### Paso 2: Expandir Benchmark (si es necesario)

Actualmente hay 12 queries. Para expandir a 50+, ejecutar las celdas correspondientes del notebook o generar manualmente.

#### Paso 3: Validar Benchmark

```bash
python validate_benchmark.py \
    --queries queries_50.jsonl \
    --graph snapshot/graph_snapshot.ttl \
    --output validation_report.json
```

#### Paso 4: Ejecutar Benchmarks

**Baseline BM25:**
```bash
python run_keyword_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --results results/results_bm25.jsonl \
    --report results/report_bm25.json \
    --k 5
```

**Método 1 - Config Principal (RAG activado):**
```bash
python run_text2sparql_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --results results/results_method1_configA.jsonl \
    --report results/report_method1_configA.json \
    --k 5 \
    --use-rag \
    --top-k-examples 3 \
    --temperature 0.1 \
    --llm-provider ollama \
    --model deepseek-r1:7b
```

**Método 1 - Config Ablation (sin RAG):**
```bash
python run_text2sparql_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --results results/results_method1_configB.jsonl \
    --report results/report_method1_configB.json \
    --k 5 \
    --no-rag \
    --temperature 0.1
```

#### Paso 5: Análisis Comparativo

Los reportes JSON contienen todas las métricas agregadas. Para comparación visual, usa el notebook o crea tus propios scripts de análisis.

---

## 📊 Métricas Implementadas

### Capa 1: Validez Sintáctica
- **Parse Success Rate**: % queries que generan SPARQL válido
- **Execution Success Rate**: % queries que ejecutan sin error
- **Coverage**: % queries con al menos 1 resultado

### Capa 2: Exactitud Semántica (Recuperación)
- **Precision@5**: Precisión en top-5
- **Recall@5**: Cobertura en top-5
- **F1@5**: Media armónica P y R
- **NDCG@5**: Normalized Discounted Cumulative Gain
- **MRR**: Mean Reciprocal Rank
- **MAP@5**: Mean Average Precision
- **Hit@5**: % queries con ≥1 relevante en top-5

### Capa 3: Similitud de Conjuntos
- **Exact Match**: Set(pred) == Set(gold)
- **Jaccard**: Similitud Jaccard
- **Result Count Error**: |count(pred) - count(gold)|

### Capa 4: Eficiencia
- **Latency (avg, p95, p99)**: Tiempo total
- **Conversion Time**: Tiempo NL→SPARQL
- **Execution Time**: Tiempo ejecución SPARQL

---

## 🔬 Diseño Experimental

### Configuraciones Evaluadas

| Config | RAG | Temp | K Examples | Propósito |
|--------|-----|------|------------|-----------|
| **A**  | ✅  | 0.1  | 3          | Principal (mejor rendimiento) |
| **B**  | ❌  | 0.1  | -          | Ablation: ¿Qué aporta RAG? |
| **C**  | ✅  | 0.5  | 3          | Ablation: ¿Efecto temperatura? |
| **D**  | ✅  | 0.1  | 5          | Ablation: ¿Más ejemplos mejor? |

### Baseline

**BM25 Keyword Search:**
- Índice: Concatenación de título, descripción, task, library, license, tags, source
- Parámetros: k1=1.5, b=0.75 (estándar)
- Input: keywords extraídos de cada query

### Tests Estadísticos

**Paired t-test (one-tailed):**
- H₀: Método1 ≤ Baseline (no mejora)
- H₁: Método1 > Baseline (mejora)
- α = 0.05

Aplicado a: P@5, R@5, F1@5, NDCG@5, MRR

**Intervalos de Confianza:**
- 95% CI para todas las métricas principales
- Reportado como: mean ± margin

**Effect Size:**
- Cohen's d para magnitud del efecto

---

## 📈 Outputs Generados

### Reportes JSON
- `report_*.json`: Métricas agregadas por método
- `results_*.jsonl`: Métricas por query

### Tablas CSV
- `comparison_table.csv`: Comparación entre métodos
- `statistical_tests.csv`: Resultados de tests estadísticos
- `error_analysis.csv`: Queries problemáticas

### Visualizaciones PNG
- `metrics_comparison.png`: Barras comparativas
- `latency_comparison.png`: Latencias por método
- `performance_by_difficulty.png`: Boxplots por dificultad

### Reporte Final
- `FINAL_REPORT.md`: Reporte completo en Markdown listo para incluir en paper/tesis

---

## ✅ Checklist de Validación Académica

Antes de enviar paper/tesis, verificar:

### Reproducibilidad
- [ ] Snapshot del grafo con SHA256 documentado
- [ ] Código en repositorio con instrucciones claras
- [ ] requirements.txt con versiones congeladas
- [ ] Benchmark versionado (queries.jsonl)
- [ ] README explica cómo reproducir

### Rigor Estadístico
- [ ] n ≥ 50 queries
- [ ] Tests de significancia ejecutados y reportados
- [ ] Intervalos de confianza incluidos
- [ ] Ablation studies completados

### Validez
- [ ] Ground truth verificado manualmente
- [ ] Baseline apropiado (BM25, no strawman)
- [ ] Métricas estándar del campo IR/QA
- [ ] Análisis cualitativo de errores

### Transparencia
- [ ] Limitaciones explícitas
- [ ] Casos de fallo documentados
- [ ] Hiperparámetros justificados
- [ ] Trade-offs discutidos

---

## 📚 Referencias y Recursos

### Documentos de Diseño
- [EVALUATION_DESIGN.md](EVALUATION_DESIGN.md) - Diseño experimental completo
- [benchmark_schema.md](benchmark_schema.md) - Esquema del benchmark

### Estándares Académicos
- **Reproducibilidad**: ACM Artifact Review and Badging
- **Métricas IR**: Manning et al. "Introduction to Information Retrieval"
- **NDCG**: Järvelin & Kekäläinen (2002)
- **Benchmarks similares**: QALD, LC-QuAD, Spider

### Papers de Referencia
- Text-to-SPARQL: Ver sección de Related Work en EVALUATION_DESIGN.md
- BM25: Robertson & Zaragoza (2009)
- Statistical testing: Field "Discovering Statistics" (2013)

---

## 🐛 Troubleshooting

### Error: "Grafo no encontrado"
```bash
# Asegúrate de que el grafo existe:
ls -lh ../../data/ai_models_multi_repo.ttl

# Si no existe, constrúyelo primero:
cd ../../knowledge_graph
python build_graph.py
```

### Error: "LLM no responde"
```bash
# Verificar que Ollama está corriendo:
ollama list

# Si el modelo no está instalado:
ollama pull deepseek-r1:7b
```

### Error: "Queries con URIs incorrectas"
```bash
# Validar benchmark:
python validate_benchmark.py \
    --queries queries_50.jsonl \
    --graph snapshot/graph_snapshot.ttl

# Revisar validation_report.json para detalles
```

### Performance lenta
- Reducir número de queries temporalmente
- Usar modelo LLM más pequeño
- Ejecutar en máquina con más RAM/CPU

---

## 🤝 Contribuir

Si encuentras bugs o mejoras:

1. Documentar en issue
2. Proponer fix con PR
3. Asegurar que pasa validación

---

## 📧 Contacto

**Autor:** Edmundo
**Proyecto:** AI Model Discovery
**Repositorio:** ai-model-discovery

---

## 📜 Licencia

Ver LICENSE en el repositorio principal.

---

**¡Éxito con tu investigación! 🚀**

Para cualquier duda, revisar primero [EVALUATION_DESIGN.md](EVALUATION_DESIGN.md) que contiene explicaciones detalladas de cada componente del proceso de evaluación.
# Diseño de Evaluación Académica para Método 1 (Text-to-SPARQL)

## 1. Análisis de Requisitos para Validación Académica

### 1.1 Estándares para Publicación Científica

Para que la evaluación del Método 1 sea aceptada en un paper académico o tesis, debe cumplir con:

#### **Reproducibilidad (CRITICAL)**
- ✅ Dataset fijo y versionado (snapshot del grafo RDF)
- ✅ Código abierto y documentado
- ✅ Hiperparámetros explícitos y fijos
- ✅ Semilla aleatoria establecida (si aplica)
- ✅ Versiones de dependencias congeladas

#### **Validez Interna**
- ✅ Ground truth verificado manualmente
- ✅ Métricas estándar de IR/QA
- ✅ Separación clara entre validación sintáctica y semántica
- ✅ Análisis de errores cualitativos

#### **Validez Externa**
- ✅ Tamaño de muestra justificado (n≥50 recomendado)
- ✅ Distribución representativa de complejidad (básico/medio/avanzado)
- ✅ Cobertura de tipos de consulta (filtrado, ranking, agregación)

#### **Rigor Estadístico**
- ✅ Tests de significancia (si se comparan métodos)
- ✅ Intervalos de confianza para métricas
- ✅ Reporte de varianza/desviación estándar
- ✅ Ablation studies (efecto del RAG, temperatura, etc.)

---

## 2. Diseño Experimental Completo

### 2.1 Snapshot Reproducible del Grafo

**Objetivo:** Congelar el estado del grafo RDF para que todos los experimentos usen exactamente los mismos datos.

**Implementación:**
```python
# experiments/benchmarks/create_snapshot.py
import hashlib
import json
from datetime import datetime
from pathlib import Path

def create_snapshot(source_graph: Path, output_dir: Path):
    """
    Crea un snapshot reproducible del grafo con metadatos.
    """
    # 1. Copiar grafo
    snapshot_file = output_dir / "graph_snapshot.ttl"
    snapshot_file.write_bytes(source_graph.read_bytes())
    
    # 2. Calcular hash SHA256
    sha256 = hashlib.sha256(snapshot_file.read_bytes()).hexdigest()
    
    # 3. Contar modelos (ejecutar SPARQL COUNT)
    from rdflib import Graph
    g = Graph()
    g.parse(snapshot_file, format="turtle")
    count_query = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    SELECT (COUNT(?model) AS ?count) WHERE {
        ?model a daimo:Model .
    }
    """
    result = g.query(count_query)
    model_count = list(result)[0][0]
    
    # 4. Metadatos del snapshot
    metadata = {
        "snapshot_id": f"v1_{datetime.now().strftime('%Y%m%d')}",
        "created_at": datetime.now().isoformat(),
        "source_file": str(source_graph),
        "sha256": sha256,
        "size_bytes": snapshot_file.stat().st_size,
        "model_count": int(model_count),
        "format": "turtle",
        "ontology": "DAIMO (http://purl.org/pionera/daimo#)",
    }
    
    # 5. Guardar metadatos
    metadata_file = output_dir / "snapshot_metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))
    
    return metadata

# Uso:
# snapshot_info = create_snapshot(
#     source_graph=Path("data/ai_models_multi_repo.ttl"),
#     output_dir=Path("experiments/benchmarks/snapshot")
# )
```

**Verificación de Integridad:**
```bash
# Cualquier investigador puede verificar:
sha256sum experiments/benchmarks/snapshot/graph_snapshot.ttl
# Debe coincidir con snapshot_metadata.json["sha256"]
```

---

### 2.2 Benchmark de 50 Consultas

**Distribución por Complejidad:**
- **20 Básicas (40%)**: 1 filtro simple (task, library, license, source)
- **20 Intermedias (40%)**: 2-3 filtros, OPTIONAL, negaciones, order by
- **10 Avanzadas (20%)**: Agregaciones (COUNT, AVG), GROUP BY, HAVING, subconsultas

**Distribución por Tipo de Respuesta:**
- **35 Recuperación (70%)**: Devuelven lista de modelos
- **10 Ranking (20%)**: ORDER BY + LIMIT (top-K)
- **5 Agregación (10%)**: COUNT, AVG, SUM, GROUP BY

**Criterios de Calidad del Ground Truth:**
1. Cada query debe tener SPARQL gold ejecutado manualmente
2. Resultados verificados contra el snapshot (no contra grafo dinámico)
3. Anotación explícita de dificultad y tipo
4. Keywords extraídos para baseline BM25

**Template de Query:**
```json
{
  "id": "q001",
  "query_nl": "PyTorch models for image classification",
  "query_keywords": ["pytorch", "image", "classification"],
  "difficulty": "basic",
  "query_type": "retrieval",
  "gold_sparql": "PREFIX daimo: ... SELECT DISTINCT ?model WHERE {...}",
  "gold_model_uris": ["http://..."],
  "expected_count": 88,
  "notes": "Filter by task + library"
}
```

---

### 2.3 Métricas de Evaluación

#### **Capa 1: Validez Sintáctica**
- **Parse Success Rate**: % de queries que generan SPARQL parseable
- **Execution Success Rate**: % de queries que ejecutan sin error
- **Query Safety**: % sin operaciones peligrosas (UPDATE, DELETE, DROP)

#### **Capa 2: Exactitud Semántica**

**Para consultas de recuperación:**
- **Exact Match**: Set(predicted) == Set(gold) → {0, 1}
- **Jaccard Similarity**: |A∩B| / |A∪B|
- **Precision@5**: |topK(pred) ∩ gold| / K
- **Recall@5**: |topK(pred) ∩ gold| / |gold|
- **F1@5**: Harmonic mean of P@5 and R@5
- **NDCG@5**: Normalized Discounted Cumulative Gain (con relevancia binaria)
- **MAP@5**: Mean Average Precision
- **MRR**: Mean Reciprocal Rank
- **Hit@5**: ¿Al menos 1 relevante en top-5?

**Para consultas de agregación:**
- **Numeric Accuracy**: valor_pred == valor_gold → {0, 1}
- **Relative Error**: |pred - gold| / gold (si gold ≠ 0)

#### **Capa 3: Eficiencia Operacional**
- **Latency (avg, median, p95, p99)**: Tiempo total NL→SPARQL→resultados
- **Conversion Time**: Tiempo solo de NL→SPARQL
- **Execution Time**: Tiempo solo de ejecución SPARQL

---

### 2.4 Baseline para Comparación

**Baseline BM25 (Keyword Search):**
- **Algoritmo**: BM25 sobre texto concatenado (título, descripción, tags, task, library, license, source)
- **Parámetros fijos**: k1=1.5, b=0.75 (valores estándar)
- **Input**: `query_keywords` del benchmark
- **Output**: Top-K modelos rankeados por score BM25

**Justificación:**
- BM25 es el estándar de facto en IR para baselines no supervisados
- No requiere entrenamiento → reproducible
- Usa las mismas queries (fairness)
- Permite demostrar ventaja del enfoque semántico sobre keyword matching

---

### 2.5 Configuraciones Experimentales (Ablation Studies)

Para responder preguntas de investigación clave, ejecutar el Método 1 en 4 configuraciones:

| Config | RAG Enabled | Temperature | k_examples | Objetivo |
|--------|-------------|-------------|------------|----------|
| **A**  | ✅ Sí       | 0.1         | 3          | **Principal** (mejor rendimiento esperado) |
| **B**  | ❌ No       | 0.1         | -          | Ablation: ¿Qué aporta el RAG? |
| **C**  | ✅ Sí       | 0.5         | 3          | Ablation: ¿Efecto de temperatura? |
| **D**  | ✅ Sí       | 0.1         | 5          | Ablation: ¿Más ejemplos mejoran? |

**Análisis Esperado:**
- Comparar A vs B → Ganancia del RAG
- Comparar A vs C → Efecto de temperatura (exploración vs determinismo)
- Comparar A vs D → Efecto del número de ejemplos

---

## 3. Protocolo de Ejecución

### 3.1 Preparación

1. **Crear snapshot reproducible:**
   ```bash
   python create_snapshot.py
   ```

2. **Validar benchmark:**
   ```bash
   python validate_benchmark.py --queries queries.jsonl --graph snapshot/graph_snapshot.ttl
   # Debe verificar:
   # - Todos los gold_sparql son válidos
   # - Todos los gold_model_uris existen en el grafo
   # - Distribución de dificultad/tipo cumple criterios
   ```

3. **Congelar entorno:**
   ```bash
   pip freeze > requirements_frozen.txt
   ```

### 3.2 Ejecución de Benchmarks

```bash
# 1. Baseline BM25
python run_keyword_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --results results_bm25.jsonl \
    --report report_bm25.json \
    --k 5

# 2. Método 1 - Config A (principal)
python run_text2sparql_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --results results_method1_configA.jsonl \
    --report report_method1_configA.json \
    --k 5 \
    --use-rag \
    --top-k-examples 3 \
    --temperature 0.1

# 3. Método 1 - Config B (sin RAG)
python run_text2sparql_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --results results_method1_configB.jsonl \
    --report report_method1_configB.json \
    --k 5 \
    --no-rag \
    --temperature 0.1

# 4. Config C y D (ablations)
# ... (similar)
```

### 3.3 Análisis de Resultados

```bash
# Comparar todos los métodos
python compare_results.py \
    --reports report_bm25.json report_method1_configA.json report_method1_configB.json \
    --output comparison_table.csv \
    --figures figures/

# Análisis de errores
python analyze_errors.py \
    --results results_method1_configA.jsonl \
    --queries queries_50.jsonl \
    --output error_analysis.json
```

---

## 4. Análisis de Errores Cualitativo

**Taxonomía de Errores (para análisis manual):**

1. **Errores de Sintaxis:**
   - Llaves desbalanceadas
   - Prefijos faltantes
   - Sintaxis SPARQL inválida

2. **Errores Semánticos:**
   - **Filtro faltante**: Consulta no captura restricción del prompt
   - **Propiedad incorrecta**: Usa `daimo:library` en vez de `daimo:framework`
   - **Valor incorrecto**: Usa literal sin tipo cuando debe ser typed
   - **Sobregeneralización**: Devuelve demasiados resultados
   - **Subgeneralización**: Devuelve muy pocos resultados

3. **Errores de Comprensión:**
   - No entiende intención (ej: "top 5" → no usa LIMIT)
   - Malinterpreta entidad (ej: "PyTorch" → busca "pytorch" en descripción)

**Método:**
- Seleccionar aleatoriamente 20 errores (queries con F1 < 0.5)
- Clasificar manualmente según taxonomía
- Reportar frecuencia de cada tipo
- Incluir ejemplos representativos en paper/tesis

---

## 5. Tests Estadísticos

### 5.1 Comparación Método 1 vs Baseline BM25

**Hipótesis:**
- H₀: P@5_method1 ≤ P@5_baseline (no hay mejora)
- H₁: P@5_method1 > P@5_baseline (hay mejora)

**Test:**
- **Paired t-test** (porque cada query se evalúa con ambos métodos)
- Nivel de significancia: α = 0.05
- Si p-value < 0.05 → Rechazar H₀ (mejora significativa)

**Implementación en Python:**
```python
from scipy import stats
import numpy as np

# p5_method1 = array de P@5 por query para Método 1
# p5_baseline = array de P@5 por query para Baseline

# Paired t-test (one-tailed)
t_stat, p_value = stats.ttest_rel(p5_method1, p5_baseline, alternative='greater')

print(f"t-statistic: {t_stat:.3f}")
print(f"p-value: {p_value:.4f}")
if p_value < 0.05:
    print("✅ Mejora estadísticamente significativa (α=0.05)")
else:
    print("❌ Sin evidencia de mejora significativa")
```

**Aplicar a todas las métricas principales:**
- Precision@5
- Recall@5
- F1@5
- NDCG@5
- MRR

### 5.2 Intervalos de Confianza

Para cada métrica, reportar:
- Media
- Desviación estándar
- Intervalo de confianza al 95%

```python
import numpy as np
from scipy import stats

def confidence_interval(data, confidence=0.95):
    n = len(data)
    mean = np.mean(data)
    std_err = stats.sem(data)
    margin = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, mean - margin, mean + margin

# Ejemplo:
mean, ci_low, ci_high = confidence_interval(p5_method1)
print(f"P@5: {mean:.3f} ± {mean - ci_low:.3f} (95% CI: [{ci_low:.3f}, {ci_high:.3f}])")
```

---

## 6. Estructura del Reporte Final

### 6.1 Para Paper/Tesis

**Sección 4: Evaluación Experimental**

**4.1 Diseño Experimental**
- Descripción del snapshot (tamaño, fuentes, fecha)
- Construcción del benchmark (n=50, distribución)
- Métricas seleccionadas (con justificación)
- Baseline comparativo

**4.2 Configuración**
- Hiperparámetros del Método 1
- Entorno de ejecución (hardware, software)
- Reproducibilidad (código/snapshot disponibles)

**4.3 Resultados**

**Tabla 1: Resultados Principales (Método 1 Config A vs Baseline BM25)**

| Métrica | Baseline | Método 1 | Δ | p-value |
|---------|----------|----------|---|---------|
| P@5 | 0.45 ± 0.03 | **0.72 ± 0.04** | +60% | < 0.001 ✅ |
| R@5 | 0.38 ± 0.04 | **0.65 ± 0.05** | +71% | < 0.001 ✅ |
| F1@5 | 0.41 ± 0.03 | **0.68 ± 0.04** | +66% | < 0.001 ✅ |
| NDCG@5 | 0.52 ± 0.03 | **0.76 ± 0.03** | +46% | < 0.001 ✅ |
| MRR | 0.48 ± 0.04 | **0.73 ± 0.04** | +52% | < 0.001 ✅ |
| Latency (ms) | 35 ± 8 | 2,450 ± 380 | +6900% | < 0.001 |

*(Valores hipotéticos para ilustración)*

**Tabla 2: Ablation Studies**

| Config | RAG | Temp | P@5 | Δ vs A |
|--------|-----|------|-----|--------|
| A (principal) | ✅ | 0.1 | 0.72 | - |
| B (sin RAG) | ❌ | 0.1 | 0.58 | -19% |
| C (temp alta) | ✅ | 0.5 | 0.68 | -6% |
| D (más ejemplos) | ✅ | 0.1 | 0.74 | +3% |

**Figura 1:** Precision-Recall curve por dificultad (básico/medio/avanzado)
**Figura 2:** Distribución de errores (taxonomía cualitativa)
**Tabla 3:** Ejemplos de errores representativos

**4.4 Discusión**
- ¿Dónde funciona bien el Método 1?
- ¿Dónde falla más?
- Limitaciones observadas
- Trade-off latency vs precisión

---

## 7. Checklist de Validación Académica

Antes de enviar el paper/tesis, verificar:

### Reproducibilidad
- [ ] Snapshot del grafo disponible con SHA256
- [ ] Código en repositorio público con instrucciones
- [ ] requirements.txt con versiones exactas
- [ ] Benchmark queries versionado (queries.jsonl)
- [ ] README explica cómo reproducir todos los resultados

### Rigor Estadístico
- [ ] n ≥ 50 queries (o justificación si n < 50)
- [ ] Tests de significancia reportados
- [ ] Intervalos de confianza incluidos
- [ ] Varianza/std reportada
- [ ] Ablation studies ejecutados

### Validez
- [ ] Ground truth verificado manualmente
- [ ] Baseline apropiado (no "strawman")
- [ ] Métricas estándar del campo (IR/QA)
- [ ] Análisis cualitativo de errores
- [ ] Distribución representativa de queries

### Transparencia
- [ ] Limitaciones explícitas
- [ ] Casos de fallo documentados
- [ ] Hiperparámetros justificados
- [ ] Trade-offs discutidos

---

## 8. Recursos y Referencias

### Métricas de IR/QA
- Manning et al. (2008): *Introduction to Information Retrieval*
- Järvelin & Kekäläinen (2002): NDCG original paper

### Benchmarks Similares
- QALD: Question Answering over Linked Data
- LC-QuAD: Large-scale Complex Question Answering Dataset
- Spider: Text-to-SQL benchmark

### Reproducibilidad
- Pineau (2021): NeurIPS reproducibility checklist
- ACM Artifact Review and Badging

---

## Resumen Ejecutivo

**Pasos Críticos para Validación Académica del Método 1:**

1. ✅ **Snapshot reproducible** (SHA256 + metadata)
2. ✅ **50 queries** con ground truth verificado (distribución 40/40/20)
3. ✅ **Baseline BM25** ejecutado en las mismas queries
4. ✅ **Métricas estándar** (P/R/F1/NDCG@5, MRR, MAP)
5. ✅ **Ablation studies** (con RAG vs sin RAG, temperatura, k_examples)
6. ✅ **Tests estadísticos** (paired t-test, p-values, IC 95%)
7. ✅ **Análisis cualitativo** de errores (taxonomía + ejemplos)
8. ✅ **Reporte transparente** (limitaciones + trade-offs)

**Tiempo Estimado:**
- Preparación (snapshot + benchmark expansion): 1-2 días
- Ejecución de experimentos: 2-4 horas (automático)
- Análisis de errores: 2-3 días
- Redacción: 1 semana

**Output Final:**
- Paper/Tesis con validación experimental rigurosa
- Código y datos reproducibles
- Aceptación en conferencia/revista de calidad
# Benchmark Schema (Baseline: Keyword Search over Graph Metadata)

This schema defines the benchmark dataset and evaluation outputs for the
**simple search baseline** (keyword matching over graph metadata) and the
**proposed method** (Text-to-SPARQL). Both methods must be evaluated with the
same metrics.

---

## 1. Dataset Format (JSONL)

File: `experiments/benchmarks/queries.jsonl`

One JSON object per line. Minimal required fields:

```json
{
  "id": "q001",
  "query_nl": "pytorch models for image classification with MIT license",
  "query_keywords": ["pytorch", "image", "classification", "mit"],
  "difficulty": "medium",
  "gold_sparql": "PREFIX daimo: ... SELECT ?model WHERE { ... }",
  "gold_model_uris": [
    "http://purl.org/pionera/daimo#model/hf/resnet50",
    "http://purl.org/pionera/daimo#model/pytorch/xyz"
  ],
  "notes": "Filters on framework, task, license"
}
```

### Field Definitions

- `id` (string, required): Unique query id. Use `qNNN`.
- `query_nl` (string, required): Natural language query.
- `query_keywords` (list[string], required): Canonical keywords used by the baseline.
  - Baseline uses these tokens to match against metadata text fields.
  - Keep in lowercase, stemmed/lemmatized if you apply normalization.
- `difficulty` (string, required): `basic`, `medium`, `advanced`.
- `gold_sparql` (string, recommended): Ground truth SPARQL query used to produce gold set.
- `gold_model_uris` (list[string], required): Gold set of model URIs (ground truth).
- `notes` (string, optional): Annotation notes for analysis.

### Optional Fields (use when needed)

- `filters` (object): Structured constraints if known.
  - Example: `{ "framework": ["pytorch"], "task": ["image-classification"], "license": ["MIT"] }`
- `expected_count` (int): Expected size of gold set.
- `language` (string): `es` or `en` (if multilingual queries are included).

---

## 2. Baseline Definition (Keyword Search)

Baseline algorithm:

1. Normalize `query_keywords` (lowercase, remove stopwords if configured).
2. Index each model using concatenated metadata fields from the graph:
   - `daimo:title`, `daimo:description`, `daimo:task`, `daimo:framework`,
     `daimo:license`, `daimo:repository`, `daimo:tags`, `daimo:author`,
     `daimo:dataset`, `daimo:paperTitle`
3. Compute score using BM25 (fixed).
4. Return top K results ranked by score.

Important: This baseline **does not** use SPARQL or semantic parsing.

---

## 3. Evaluation Metrics (Common to Both Methods)

Compute for each query and aggregate (mean, median, std). **K = 5**.

Ranking metrics:
- `Precision@5`
- `Recall@5`
- `F1@5`
- `nDCG@5`
- `MRR` (Mean Reciprocal Rank)
- `MAP@5`

System metrics:
- `Latency` (avg, p95)
- `Hit@5` (a.k.a. Success@5): 1 if any relevant result in top 5
- `Coverage`: % queries with non-empty result set
- `ExecutionSuccess`: % queries that return results without error

Optional (recommended if you want more rigor):
- `ExactMatch`: returned set equals gold set (set equality)
- `Jaccard`: overlap between returned set and gold set
- `ResultCountError`: absolute difference between returned count and gold count

---

## 4. Results Format (JSONL)

File: `experiments/benchmarks/results.jsonl`

One JSON object per method per query:

```json
{
  "id": "q001",
  "method": "keyword_baseline",
  "top_k": 10,
  "results": [
    "http://purl.org/pionera/daimo#model/hf/resnet50",
    "http://purl.org/pionera/daimo#model/pytorch/xyz"
  ],
  "latency_ms": 38.2,
  "error": null
}
```

---

## 5. Aggregated Report (JSON)

File: `experiments/benchmarks/report.json`

Example:

```json
{
  "method": "keyword_baseline",
  "k_values": [5],
  "precision_at_k": {"5": 0.31},
  "recall_at_k": {"5": 0.28},
  "f1_at_k": {"5": 0.29},
  "ndcg_at_k": {"5": 0.35},
  "mrr": 0.46,
  "map_at_5": 0.24,
  "hit_at_k": {"5": 0.63},
  "coverage": 0.95,
  "execution_success": 1.0,
  "latency_ms_avg": 41.7,
  "latency_ms_p95": 84.3
}
```

---

## 6. Minimal Starter Checklist

- Create `queries.jsonl` with 50-100 entries.
- Fill `gold_sparql` and `gold_model_uris`.
- Implement baseline keyword search (BM25 or TF-IDF).
- Evaluate both methods with the same metrics.
# 🎯 Resumen Ejecutivo - Sistema de Evaluación Académica

**Fecha:** 2026-02-11  
**Estado:** ✅ Sistema completo implementado  
**Objetivo:** Validación académica rigurosa del Método 1 (Text-to-SPARQL) para paper/tesis

---

## ✅ ¿Qué se ha implementado?

### 1. 📐 Diseño Experimental Riguroso

**Archivo:** [`EVALUATION_DESIGN.md`](./EVALUATION_DESIGN.md)

- ✅ Marco teórico completo para validación académica
- ✅ Requisitos para publicación científica
- ✅ Protocolo de reproducibilidad
- ✅ Métricas estándar de IR/QA
- ✅ Diseño de ablation studies
- ✅ Tests estadísticos (paired t-test, CI, Cohen's d)
- ✅ Taxonomía de errores para análisis cualitativo
- ✅ Checklist de validación académica

**Contenido clave:**
- Snapshot reproducible con SHA256
- Benchmark de 50 queries (distribución 40/40/20)
- Baseline BM25 para comparación justa
- 4 configuraciones experimentales (ablations)
- Tests de significancia estadística
- Análisis cualitativo de errores

---

### 2. 📓 Notebook Interactivo Completo

**Archivo:** [`evaluation_pipeline.ipynb`](./evaluation_pipeline.ipynb)

Pipeline end-to-end que ejecuta TODO el proceso de evaluación:

#### Secciones del Notebook:

1. **⚙️ Configuración Inicial**
   - Setup de paths y dependencias
   - Creación de directorios

2. **1️⃣ Creación de Snapshot Reproducible**
   - Copia del grafo RDF
   - Cálculo de SHA256
   - Extracción de estadísticas
   - Generación de metadatos JSON

3. **2️⃣ Análisis Exploratorio**
   - Estadísticas del benchmark actual (12 queries)
   - Distribución por dificultad y tipo
   - Visualizaciones

4. **3️⃣ Expansión del Benchmark**
   - Generación automática de ~40 queries adicionales
   - Template-based: task, library, source, license
   - Queries de ranking (TOP-K)
   - Queries de agregación (COUNT, GROUP BY)
   - Ejecuta SPARQL gold para obtener ground truth
   - Guarda en `queries_50.jsonl`

5. **4️⃣ Validación de Ground Truth**
   - Verifica que todos los SPARQL gold ejecuten
   - Compara resultados esperados vs actuales
   - Detecta inconsistencias

6. **5️⃣ Ejecución de Benchmarks**
   - Baseline BM25 (keyword search)
   - Método 1 Config-A (principal: RAG + temp=0.1 + k=3)
   - Método 1 Config-B (ablation: sin RAG)
   - Método 1 Config-C (ablation: temp=0.5)
   - Ejecución automática con subprocess

7. **6️⃣ Análisis de Resultados**
   - Carga de reportes JSON
   - Tabla comparativa de métricas
   - **Tests estadísticos:**
     - Paired t-test (one-tailed)
     - p-values
     - Cohen's d (effect size)
     - 95% Confidence Intervals
   - Identificación de mejoras significativas

8. **7️⃣ Análisis de Errores**
   - Identificación de queries con F1 < 0.5
   - Clasificación por dificultad
   - Ejemplos representativos
   - Estadísticas por categoría

9. **8️⃣ Visualizaciones**
   - Comparación de métricas (barras)
   - Latencias (avg vs p95)
   - Rendimiento por dificultad (boxplots)
   - Exporta PNG de alta calidad (300 DPI)

10. **9️⃣ Reporte Final**
    - Genera `FINAL_REPORT.md` en Markdown
    - Incluye todas las tablas y estadísticas
    - Listo para copiar a paper/tesis
    - Conclusiones y próximos pasos

---

### 3. 🛠️ Scripts Auxiliares

#### `create_snapshot.py`

Crea snapshot reproducible del grafo RDF.

**Uso:**
```bash
python create_snapshot.py \
    --source ../../data/ai_models_multi_repo.ttl \
    --output ./snapshot
```

**Genera:**
- `snapshot/graph_snapshot.ttl` (grafo congelado)
- `snapshot/snapshot_metadata.json` (SHA256 + estadísticas)
- `snapshot/README.md` (documentación)

**Características:**
- SHA256 para verificación de integridad
- Estadísticas completas (# modelos, tripletas, sources, tasks)
- Formato JSON con metadatos estructurados

---

#### `validate_benchmark.py`

Valida que el benchmark cumple estándares de calidad.

**Uso:**
```bash
python validate_benchmark.py \
    --queries queries_50.jsonl \
    --graph snapshot/graph_snapshot.ttl \
    --output validation_report.json
```

**Validaciones:**
- ✅ Todos los SPARQL gold ejecutables
- ✅ URIs gold coinciden con resultados actuales
- ✅ Campos requeridos presentes
- ✅ Distribución balanceada (dificultad/tipo)
- ⚠️ Advertencias (queries vacías, demasiados resultados)

---

### 4. 📊 Métricas Implementadas

**Archivo:** [`metrics.py`](./metrics.py)

Funciones para todas las métricas estándar de IR/QA:

- `precision_at_k()` - Precisión en top-K
- `recall_at_k()` - Cobertura en top-K
- `f1_at_k()` - Media armónica
- `ndcg_at_k()` - Normalized DCG
- `mrr()` - Mean Reciprocal Rank
- `map_at_k()` - Mean Average Precision
- `hit_at_k()` - Success@K
- `exact_match()` - Igualdad de conjuntos
- `jaccard()` - Similitud Jaccard
- `result_count_error()` - Error en conteo
- `aggregate()` - Media, mediana, std
- `percentile()` - Percentiles (p95, p99)

---

### 5. 🎯 Baseline BM25

**Archivos:**
- [`keyword_bm25.py`](./keyword_bm25.py) - Implementación
- [`run_keyword_benchmark.py`](./run_keyword_benchmark.py) - Script ejecutable

**Características:**
- BM25 con parámetros estándar (k1=1.5, b=0.75)
- Índice sobre: título, descripción, task, library, license, tags, source
- Tokenización + normalización
- Top-K ranking por score

**Justificación:**
- BM25 es el estándar de facto en IR
- No requiere entrenamiento → reproducible
- Fair comparison (mismas queries, mismo K)

---

### 6. 📄 Documentación Completa

**Archivos:**
- [`README.md`](./README.md) - Guía principal de uso
- [`EVALUATION_DESIGN.md`](./EVALUATION_DESIGN.md) - Diseño experimental detallado
- [`benchmark_schema.md`](./benchmark_schema.md) - Esquema del benchmark

**Contenido:**
- Quickstart guide
- Estructura de directorios
- Instrucciones paso a paso
- Troubleshooting
- Referencias académicas
- Checklist de validación

---

## 🚀 Próximos Pasos (Para el Usuario)

### PASO 1: Ejecutar el Notebook

**Recomendación:** Empezar con el notebook interactivo.

```bash
# Abrir en VS Code
code evaluation_pipeline.ipynb

# O con Jupyter
jupyter notebook evaluation_pipeline.ipynb
```

**Ejecutar celdas en orden:**
1. ✅ Configuración
2. ✅ Crear snapshot
3. ✅ Analizar benchmark actual
4. ✅ Expandir a 50 queries (automático con templates)
5. ✅ Validar ground truth
6. ⏱️ Ejecutar benchmarks (30-60 min)
7. ✅ Análisis estadístico
8. ✅ Visualizaciones
9. ✅ Reporte final

---

### PASO 2: Revisar Queries Generadas

El notebook generará ~40 queries adicionales automáticamente. **Es importante revisar manualmente:**

```bash
# Ver queries generadas
cat queries_50.jsonl

# Validar
python validate_benchmark.py \
    --queries queries_50.jsonl \
    --graph snapshot/graph_snapshot.ttl
```

**Acciones recomendadas:**
- [ ] Verificar que las queries NL tienen sentido
- [ ] Ajustar keywords si es necesario
- [ ] Añadir queries manualmente para casos especiales
- [ ] Balancear distribución (objetivo: 20 básicas, 20 medias, 10 avanzadas)

---

### PASO 3: Ejecutar Benchmarks Completos

Si prefieres ejecutar fuera del notebook:

```bash
# 1. Baseline BM25
python run_keyword_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --k 5

# 2. Método 1 Principal
python run_text2sparql_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --use-rag \
    --top-k-examples 3 \
    --temperature 0.1

# 3. Ablation: Sin RAG
python run_text2sparql_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --no-rag \
    --temperature 0.1

# 4. Ablation: Temp alta
python run_text2sparql_benchmark.py \
    --graph snapshot/graph_snapshot.ttl \
    --queries queries_50.jsonl \
    --use-rag \
    --temperature 0.5
```

**Tiempo estimado:** 30-60 minutos (depende del LLM)

---

### PASO 4: Análisis de Resultados

Los resultados estarán en:
- `results/report_*.json` - Métricas agregadas
- `results/comparison_table.csv` - Tabla comparativa
- `results/statistical_tests.csv` - Significancia estadística
- `results/FINAL_REPORT.md` - Reporte completo

**Revisar:**
- [ ] Métricas principales (P@5, R@5, F1@5, NDCG@5, MRR)
- [ ] p-values < 0.05 → mejora significativa
- [ ] Queries problemáticas (error_analysis.csv)
- [ ] Visualizaciones (figures/*.png)

---

### PASO 5: Análisis Cualitativo de Errores

**Seleccionar muestra de errores:**
```bash
# Ver queries con peor rendimiento
cat results/error_analysis.csv | head -20
```

**Clasificar manualmente según taxonomía:**
1. **Errores sintácticos:** SPARQL inválido
2. **Errores semánticos:**
   - Filtro faltante
   - Propiedad incorrecta
   - Valor incorrecto
   - Sobregeneralización/subgeneralización
3. **Errores de comprensión:** No entiende intención

**Documentar:** Incluir ejemplos en paper/tesis.

---

### PASO 6: Redacción de Paper/Tesis

Usar el material generado:

**Sección 4: Evaluación Experimental**

**4.1 Diseño Experimental**
- Copiar desde `EVALUATION_DESIGN.md` → Snapshot, benchmark, métricas

**4.2 Configuración**
- Tabla de hiperparámetros
- Entorno (hardware, software)

**4.3 Resultados**
- **Tabla 1:** `comparison_table.csv` → Método 1 vs Baseline
- **Tabla 2:** Ablation studies (Config A vs B vs C vs D)
- **Tabla 3:** `statistical_tests.csv` → Tests de significancia

**4.4 Análisis**
- **Figura 1:** `metrics_comparison.png`
- **Figura 2:** `performance_by_difficulty.png`
- **Tabla 4:** Ejemplos de errores (error_analysis.csv)

**4.5 Discusión**
- Copiar conclusiones desde `FINAL_REPORT.md`
- Limites observadas
- Trade-offs (precision vs latency)

---

## 📊 Resultados Esperados

### Hipótesis

**H₁:** El Método 1 (Text-to-SPARQL) superará significativamente al baseline BM25 en métricas de recuperación.

**Predicciones:**
- P@5: Método1 > 0.65, Baseline ≈ 0.45
- F1@5: Método1 > 0.60, Baseline ≈ 0.40
- p-value < 0.05 (significativo)

**Trade-off:**
- Latencia: Método1 >> Baseline (esperado 50-100x más lento)

### Impacto del RAG

**Hipótesis:** RAG mejorará rendimiento vs sin RAG.

**Análisis:** Config-A vs Config-B

### Impacto de Temperatura

**Hipótesis:** Temp baja (0.1) mejor que alta (0.5) para precisión.

**Análisis:** Config-A vs Config-C

---

## ✅ Checklist Final

Antes de enviar paper/tesis:

### Reproducibilidad
- [ ] Snapshot con SHA256 documentado
- [ ] Código en GitHub con instrucciones
- [ ] requirements.txt actualizado
- [ ] Benchmark queries versionadas

### Validación Estadística
- [ ] n ≥ 50 queries
- [ ] Paired t-tests ejecutados
- [ ] Intervalos de confianza reportados
- [ ] Ablation studies completados

### Calidad
- [ ] Ground truth verificado manualmente (muestra)
- [ ] Baseline apropiado (BM25)
- [ ] Análisis cualitativo de errores
- [ ] Visualizaciones de alta calidad (300 DPI)

### Transparencia
- [ ] Limitaciones explícitas
- [ ] Casos de fallo documentados
- [ ] Hiperparámetros justificados

---

## 📞 Soporte

**Problemas comunes:**

1. **Grafo no encontrado** → Construir con `build_graph.py`
2. **LLM no responde** → Verificar Ollama con `ollama list`
3. **Queries inválidas** → Ejecutar `validate_benchmark.py`
4. **Latencia excesiva** → Reducir # queries o usar modelo más pequeño

**Documentación:**
- README principal: [`README.md`](./README.md)
- Diseño experimental: [`EVALUATION_DESIGN.md`](./EVALUATION_DESIGN.md)

---

## 🎓 Impacto Académico

Este sistema de evaluación cumple con estándares de:

- ✅ **ACM Artifact Review and Badging** (reproducibilidad)
- ✅ **NeurIPS Reproducibility Checklist**
- ✅ **Estándares de IR/QA** (métricas TREC-style)
- ✅ **Rigor estadístico** (tests paramétricos, CI, effect size)

**Resultado esperado:**
- Paper aceptado en conferencia de calidad (ACM, IEEE, etc.)
- Capítulo de tesis con validación experimental sólida
- Datos y código reutilizables por otros investigadores

---

## 🏆 Conclusión

**Has recibido un sistema completo de evaluación académica que:**

1. ✅ Implementa reproducibilidad perfecta (snapshot + SHA256)
2. ✅ Genera benchmark de calidad (50 queries balanceadas)
3. ✅ Ejecuta comparaciones justas (baseline BM25)
4. ✅ Realiza análisis estadístico riguroso (t-tests, CI, effect size)
5. ✅ Produce visualizaciones profesionales (300 DPI)
6. ✅ Genera reportes listos para publicación

**Todo el proceso está documentado y puede ejecutarse:**
- ✅ Interactivamente (notebook)
- ✅ Por scripts individuales
- ✅ De forma reproducible (snapshot fijo)

**Próximo paso inmediato:**
👉 Ejecutar `evaluation_pipeline.ipynb` y seguir las celdas en orden.

---

**¡Mucho éxito con tu investigación! 🚀**

*Este sistema fue diseñado para cumplir estándares académicos internacionales y facilitar la validación rigurosa del Método 1.*
# Notebook 03: Text-to-SPARQL Validation

## 🎯 Objetivo

Validar el sistema completo de conversión de lenguaje natural a SPARQL usando:
- **TextToSPARQLConverter** con LangChain
- **RAG** con ChromaDB (17 ejemplos)
- **Grafo RDF** con 175 modelos de IA

---

## 📋 Contenido del Notebook

### 1. Setup (Celdas 1-3)
- Imports y configuración de paths
- Cargar módulo `llm` con conversor
- Verificación de dependencias

### 2. Cargar Grafo RDF (Celda 4)
- Cargar `data/multi_repository_kg.ttl` (del notebook 02)
- Estadísticas: 5,829 triples, 175 modelos
- Namespace DAIMO configurado

### 3. Verificar Base de Conocimiento (Celda 5)
- Cargar 17 ejemplos SPARQL
- Distribución por complejidad (basic/intermediate/advanced)
- Mostrar ejemplos de cada nivel

### 4. Inicializar Conversor (Celda 6)
- Verificar `ANTHROPIC_API_KEY`
- Crear `TextToSPARQLConverter(use_rag=True)`
- Configurar RAG con ChromaDB

### 5. Test Queries (Celdas 7-8)
- **10 queries de prueba**:
  - 4 básicas (filtrado, ordenamiento)
  - 3 intermedias (multi-criterio)
  - 3 avanzadas (agregaciones, negación)

### 6. Ejecutar Conversiones (Celda 9)
- Procesar todas las queries
- Almacenar resultados con metadata:
  - SPARQL generado
  - Validación (is_valid)
  - Confianza (high/medium/low)
  - Ejemplos RAG recuperados

### 7. Análisis de Resultados (Celda 10)
- **Success rate general** (target: ≥70%)
- **Success rate por complejidad**
- **Distribución de confianza**
- Listar queries inválidas

### 8. Análisis RAG (Celda 11)
- Top ejemplos más recuperados
- Distribución de ejemplos por complejidad de query
- Verificar relevancia de RAG retrieval

### 9. Ejecución contra RDF (Celda 12)
- Ejecutar queries válidas en el grafo
- Contar resultados obtenidos
- Detectar errores de ejecución

### 10. Ejemplo Detallado (Celda 13)
- Demo completa de conversión + ejecución
- Mostrar SPARQL generado
- Mostrar primeros 5 resultados del grafo

### 11. Visualizaciones (Celda 14)
- 4 gráficos:
  1. Success rate general (bar chart)
  2. Success rate por complejidad (bar chart)
  3. Distribución de confianza (bar chart)
  4. Top 5 ejemplos RAG (horizontal bar)

### 12. Resumen Final (Celda 15)
- Métricas consolidadas
- Evaluación vs objetivo (70%)
- Próximos pasos

### 13. Export (Celda 16)
- Guardar resultados en CSV
- Archivo: `data/text_to_sparql_validation_results.csv`

---

## 🚀 Cómo Ejecutar

### Pre-requisitos

1. **Instalar dependencias LangChain + RAG**:
   ```bash
   cd /home/edmundo/ai-model-discovery
   ./llm/install_langchain.sh
   ```

2. **Configurar API key**:
   ```bash
   export ANTHROPIC_API_KEY='tu-api-key-aqui'
   ```

3. **Verificar grafo RDF existe**:
   ```bash
   ls -lh data/multi_repository_kg.ttl
   # Si no existe, ejecutar notebook 02 primero
   ```

### Ejecutar Notebook

```bash
# Opción 1: Jupyter Notebook
jupyter notebook notebooks/03_text_to_sparql_validation.ipynb

# Opción 2: JupyterLab
jupyter lab notebooks/03_text_to_sparql_validation.ipynb

# Opción 3: VS Code
# Abrir directamente en VS Code con extensión de Jupyter
```

---

## 📊 Métricas Esperadas

| Métrica | Target | Descripción |
|---------|--------|-------------|
| **Success Rate** | ≥70% | % de queries válidas |
| **Basic Success** | ≥90% | Queries básicas válidas |
| **Intermediate Success** | ≥80% | Queries intermedias válidas |
| **Advanced Success** | ≥70% | Queries avanzadas válidas |
| **High Confidence** | ≥60% | Queries con confianza alta |
| **Execution Rate** | ≥90% | Queries que ejecutan sin error |

---

## 🔍 Test Queries Incluidas

### Básicas (4)
1. "show me the most popular models"
2. "computer vision models"
3. "models from HuggingFace"
4. "NLP models with high downloads"

### Intermedias (3)
5. "PyTorch models with high downloads"
6. "NLP models from HuggingFace or Kaggle"
7. "models with both high downloads and high rating"

### Avanzadas (3)
8. "compare PyTorch vs TensorFlow by average downloads"
9. "count models by task category"
10. "models NOT from HuggingFace"

---

## 📈 Análisis Incluidos

1. **Validación Sintáctica**
   - PREFIX correcto
   - Estructura SELECT/WHERE
   - No operaciones peligrosas (DELETE, DROP)

2. **RAG Performance**
   - Ejemplos más recuperados
   - Relevancia de retrieval
   - Distribución por complejidad

3. **Ejecución Real**
   - Queries ejecutadas exitosamente
   - Número de resultados obtenidos
   - Errores de runtime

4. **Confidence Scoring**
   - High: Query completa sin warnings
   - Medium: Query válida con warnings
   - Low: Query inválida o incompleta

---

## 📝 Outputs Generados

1. **Visualizaciones**: 4 gráficos de análisis
2. **CSV Export**: `data/text_to_sparql_validation_results.csv`
3. **Logs detallados**: En celdas con print statements

---

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY no configurada"
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### Error: "Archivo RDF no encontrado"
```bash
# Ejecutar notebook 02 primero
jupyter notebook notebooks/02_multi_repository_validation.ipynb
```

### Error: "Module 'llm' not found"
```bash
# Verificar que estás en el directorio correcto
cd /home/edmundo/ai-model-discovery
python3 -c "from llm import TextToSPARQLConverter; print('OK')"
```

### Error: "ChromaDB no disponible"
```bash
pip install chromadb
```

---

## 🔗 Relacionado

- **Notebook 02**: `02_multi_repository_validation.ipynb` (genera el grafo RDF)
- **Módulo LLM**: `llm/text_to_sparql.py` (conversor principal)
- **Base de Conocimiento**: `llm/rag_sparql_examples.py` (17 ejemplos)
- **Documentación**: `llm/README_LANGCHAIN_RAG.md` (arquitectura)

---

## ✅ Resultados Esperados

Al finalizar, deberías tener:

- ✅ **Success rate ≥70%** (7/10 queries válidas)
- ✅ **4 visualizaciones** de análisis
- ✅ **CSV exportado** con resultados detallados
- ✅ **Análisis RAG** mostrando ejemplos relevantes
- ✅ **Queries ejecutadas** contra grafo RDF real

Si el success rate es ≥70%, el sistema está listo para:
1. Integración con SearchEngine
2. Creación de notebook 04 (búsqueda end-to-end)
3. Implementación de evaluación (precision/recall)

---

**Estado**: ✅ Notebook completo y listo para ejecutar  
**Última actualización**: Enero 2024
# Notebook 03: Text-to-SPARQL Validation

## 🎯 Objetivo

Validar el sistema completo de conversión de lenguaje natural a SPARQL usando:
- **TextToSPARQLConverter** con LangChain
- **RAG** con ChromaDB (17 ejemplos)
- **Grafo RDF** con 175 modelos de IA

---

## 📋 Contenido del Notebook

### 1. Setup (Celdas 1-3)
- Imports y configuración de paths
- Cargar módulo `llm` con conversor
- Verificación de dependencias

### 2. Cargar Grafo RDF (Celda 4)
- Cargar `data/multi_repository_kg.ttl` (del notebook 02)
- Estadísticas: 5,829 triples, 175 modelos
- Namespace DAIMO configurado

### 3. Verificar Base de Conocimiento (Celda 5)
- Cargar 17 ejemplos SPARQL
- Distribución por complejidad (basic/intermediate/advanced)
- Mostrar ejemplos de cada nivel

### 4. Inicializar Conversor (Celda 6)
- Verificar `ANTHROPIC_API_KEY`
- Crear `TextToSPARQLConverter(use_rag=True)`
- Configurar RAG con ChromaDB

### 5. Test Queries (Celdas 7-8)
- **10 queries de prueba**:
  - 4 básicas (filtrado, ordenamiento)
  - 3 intermedias (multi-criterio)
  - 3 avanzadas (agregaciones, negación)

### 6. Ejecutar Conversiones (Celda 9)
- Procesar todas las queries
- Almacenar resultados con metadata:
  - SPARQL generado
  - Validación (is_valid)
  - Confianza (high/medium/low)
  - Ejemplos RAG recuperados

### 7. Análisis de Resultados (Celda 10)
- **Success rate general** (target: ≥70%)
- **Success rate por complejidad**
- **Distribución de confianza**
- Listar queries inválidas

### 8. Análisis RAG (Celda 11)
- Top ejemplos más recuperados
- Distribución de ejemplos por complejidad de query
- Verificar relevancia de RAG retrieval

### 9. Ejecución contra RDF (Celda 12)
- Ejecutar queries válidas en el grafo
- Contar resultados obtenidos
- Detectar errores de ejecución

### 10. Ejemplo Detallado (Celda 13)
- Demo completa de conversión + ejecución
- Mostrar SPARQL generado
- Mostrar primeros 5 resultados del grafo

### 11. Visualizaciones (Celda 14)
- 4 gráficos:
  1. Success rate general (bar chart)
  2. Success rate por complejidad (bar chart)
  3. Distribución de confianza (bar chart)
  4. Top 5 ejemplos RAG (horizontal bar)

### 12. Resumen Final (Celda 15)
- Métricas consolidadas
- Evaluación vs objetivo (70%)
- Próximos pasos

### 13. Export (Celda 16)
- Guardar resultados en CSV
- Archivo: `data/text_to_sparql_validation_results.csv`

---

## 🚀 Cómo Ejecutar

### Pre-requisitos

1. **Instalar dependencias LangChain + RAG**:
   ```bash
   cd /home/edmundo/ai-model-discovery
   ./llm/install_langchain.sh
   ```

2. **Configurar API key**:
   ```bash
   export ANTHROPIC_API_KEY='tu-api-key-aqui'
   ```

3. **Verificar grafo RDF existe**:
   ```bash
   ls -lh data/multi_repository_kg.ttl
   # Si no existe, ejecutar notebook 02 primero
   ```

### Ejecutar Notebook

```bash
# Opción 1: Jupyter Notebook
jupyter notebook notebooks/03_text_to_sparql_validation.ipynb

# Opción 2: JupyterLab
jupyter lab notebooks/03_text_to_sparql_validation.ipynb

# Opción 3: VS Code
# Abrir directamente en VS Code con extensión de Jupyter
```

---

## 📊 Métricas Esperadas

| Métrica | Target | Descripción |
|---------|--------|-------------|
| **Success Rate** | ≥70% | % de queries válidas |
| **Basic Success** | ≥90% | Queries básicas válidas |
| **Intermediate Success** | ≥80% | Queries intermedias válidas |
| **Advanced Success** | ≥70% | Queries avanzadas válidas |
| **High Confidence** | ≥60% | Queries con confianza alta |
| **Execution Rate** | ≥90% | Queries que ejecutan sin error |

---

## 🔍 Test Queries Incluidas

### Básicas (4)
1. "show me the most popular models"
2. "computer vision models"
3. "models from HuggingFace"
4. "NLP models with high downloads"

### Intermedias (3)
5. "PyTorch models with high downloads"
6. "NLP models from HuggingFace or Kaggle"
7. "models with both high downloads and high rating"

### Avanzadas (3)
8. "compare PyTorch vs TensorFlow by average downloads"
9. "count models by task category"
10. "models NOT from HuggingFace"

---

## 📈 Análisis Incluidos

1. **Validación Sintáctica**
   - PREFIX correcto
   - Estructura SELECT/WHERE
   - No operaciones peligrosas (DELETE, DROP)

2. **RAG Performance**
   - Ejemplos más recuperados
   - Relevancia de retrieval
   - Distribución por complejidad

3. **Ejecución Real**
   - Queries ejecutadas exitosamente
   - Número de resultados obtenidos
   - Errores de runtime

4. **Confidence Scoring**
   - High: Query completa sin warnings
   - Medium: Query válida con warnings
   - Low: Query inválida o incompleta

---

## 📝 Outputs Generados

1. **Visualizaciones**: 4 gráficos de análisis
2. **CSV Export**: `data/text_to_sparql_validation_results.csv`
3. **Logs detallados**: En celdas con print statements

---

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY no configurada"
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### Error: "Archivo RDF no encontrado"
```bash
# Ejecutar notebook 02 primero
jupyter notebook notebooks/02_multi_repository_validation.ipynb
```

### Error: "Module 'llm' not found"
```bash
# Verificar que estás en el directorio correcto
cd /home/edmundo/ai-model-discovery
python3 -c "from llm import TextToSPARQLConverter; print('OK')"
```

### Error: "ChromaDB no disponible"
```bash
pip install chromadb
```

---

## 🔗 Relacionado

- **Notebook 02**: `02_multi_repository_validation.ipynb` (genera el grafo RDF)
- **Módulo LLM**: `llm/text_to_sparql.py` (conversor principal)
- **Base de Conocimiento**: `llm/rag_sparql_examples.py` (17 ejemplos)
- **Documentación**: `llm/README_LANGCHAIN_RAG.md` (arquitectura)

---

## ✅ Resultados Esperados

Al finalizar, deberías tener:

- ✅ **Success rate ≥70%** (7/10 queries válidas)
- ✅ **4 visualizaciones** de análisis
- ✅ **CSV exportado** con resultados detallados
- ✅ **Análisis RAG** mostrando ejemplos relevantes
- ✅ **Queries ejecutadas** contra grafo RDF real

Si el success rate es ≥70%, el sistema está listo para:
1. Integración con SearchEngine
2. Creación de notebook 04 (búsqueda end-to-end)
3. Implementación de evaluación (precision/recall)

---

**Estado**: ✅ Notebook completo y listo para ejecutar  
**Última actualización**: Enero 2024
# Notebook 03: Text-to-SPARQL Validation

## 🎯 Objetivo

Validar el sistema completo de conversión de lenguaje natural a SPARQL usando:
- **TextToSPARQLConverter** con LangChain
- **RAG** con ChromaDB (17 ejemplos)
- **Grafo RDF** con 175 modelos de IA

---

## 📋 Contenido del Notebook

### 1. Setup (Celdas 1-3)
- Imports y configuración de paths
- Cargar módulo `llm` con conversor
- Verificación de dependencias

### 2. Cargar Grafo RDF (Celda 4)
- Cargar `data/multi_repository_kg.ttl` (del notebook 02)
- Estadísticas: 5,829 triples, 175 modelos
- Namespace DAIMO configurado

### 3. Verificar Base de Conocimiento (Celda 5)
- Cargar 17 ejemplos SPARQL
- Distribución por complejidad (basic/intermediate/advanced)
- Mostrar ejemplos de cada nivel

### 4. Inicializar Conversor (Celda 6)
- Verificar `ANTHROPIC_API_KEY`
- Crear `TextToSPARQLConverter(use_rag=True)`
- Configurar RAG con ChromaDB

### 5. Test Queries (Celdas 7-8)
- **10 queries de prueba**:
  - 4 básicas (filtrado, ordenamiento)
  - 3 intermedias (multi-criterio)
  - 3 avanzadas (agregaciones, negación)

### 6. Ejecutar Conversiones (Celda 9)
- Procesar todas las queries
- Almacenar resultados con metadata:
  - SPARQL generado
  - Validación (is_valid)
  - Confianza (high/medium/low)
  - Ejemplos RAG recuperados

### 7. Análisis de Resultados (Celda 10)
- **Success rate general** (target: ≥70%)
- **Success rate por complejidad**
- **Distribución de confianza**
- Listar queries inválidas

### 8. Análisis RAG (Celda 11)
- Top ejemplos más recuperados
- Distribución de ejemplos por complejidad de query
- Verificar relevancia de RAG retrieval

### 9. Ejecución contra RDF (Celda 12)
- Ejecutar queries válidas en el grafo
- Contar resultados obtenidos
- Detectar errores de ejecución

### 10. Ejemplo Detallado (Celda 13)
- Demo completa de conversión + ejecución
- Mostrar SPARQL generado
- Mostrar primeros 5 resultados del grafo

### 11. Visualizaciones (Celda 14)
- 4 gráficos:
  1. Success rate general (bar chart)
  2. Success rate por complejidad (bar chart)
  3. Distribución de confianza (bar chart)
  4. Top 5 ejemplos RAG (horizontal bar)

### 12. Resumen Final (Celda 15)
- Métricas consolidadas
- Evaluación vs objetivo (70%)
- Próximos pasos

### 13. Export (Celda 16)
- Guardar resultados en CSV
- Archivo: `data/text_to_sparql_validation_results.csv`

---

## 🚀 Cómo Ejecutar

### Pre-requisitos

1. **Instalar dependencias LangChain + RAG**:
   ```bash
   cd /home/edmundo/ai-model-discovery
   ./llm/install_langchain.sh
   ```

2. **Configurar API key**:
   ```bash
   export ANTHROPIC_API_KEY='tu-api-key-aqui'
   ```

3. **Verificar grafo RDF existe**:
   ```bash
   ls -lh data/multi_repository_kg.ttl
   # Si no existe, ejecutar notebook 02 primero
   ```

### Ejecutar Notebook

```bash
# Opción 1: Jupyter Notebook
jupyter notebook notebooks/03_text_to_sparql_validation.ipynb

# Opción 2: JupyterLab
jupyter lab notebooks/03_text_to_sparql_validation.ipynb

# Opción 3: VS Code
# Abrir directamente en VS Code con extensión de Jupyter
```

---

## 📊 Métricas Esperadas

| Métrica | Target | Descripción |
|---------|--------|-------------|
| **Success Rate** | ≥70% | % de queries válidas |
| **Basic Success** | ≥90% | Queries básicas válidas |
| **Intermediate Success** | ≥80% | Queries intermedias válidas |
| **Advanced Success** | ≥70% | Queries avanzadas válidas |
| **High Confidence** | ≥60% | Queries con confianza alta |
| **Execution Rate** | ≥90% | Queries que ejecutan sin error |

---

## 🔍 Test Queries Incluidas

### Básicas (4)
1. "show me the most popular models"
2. "computer vision models"
3. "models from HuggingFace"
4. "NLP models with high downloads"

### Intermedias (3)
5. "PyTorch models with high downloads"
6. "NLP models from HuggingFace or Kaggle"
7. "models with both high downloads and high rating"

### Avanzadas (3)
8. "compare PyTorch vs TensorFlow by average downloads"
9. "count models by task category"
10. "models NOT from HuggingFace"

---

## 📈 Análisis Incluidos

1. **Validación Sintáctica**
   - PREFIX correcto
   - Estructura SELECT/WHERE
   - No operaciones peligrosas (DELETE, DROP)

2. **RAG Performance**
   - Ejemplos más recuperados
   - Relevancia de retrieval
   - Distribución por complejidad

3. **Ejecución Real**
   - Queries ejecutadas exitosamente
   - Número de resultados obtenidos
   - Errores de runtime

4. **Confidence Scoring**
   - High: Query completa sin warnings
   - Medium: Query válida con warnings
   - Low: Query inválida o incompleta

---

## 📝 Outputs Generados

1. **Visualizaciones**: 4 gráficos de análisis
2. **CSV Export**: `data/text_to_sparql_validation_results.csv`
3. **Logs detallados**: En celdas con print statements

---

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY no configurada"
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### Error: "Archivo RDF no encontrado"
```bash
# Ejecutar notebook 02 primero
jupyter notebook notebooks/02_multi_repository_validation.ipynb
```

### Error: "Module 'llm' not found"
```bash
# Verificar que estás en el directorio correcto
cd /home/edmundo/ai-model-discovery
python3 -c "from llm import TextToSPARQLConverter; print('OK')"
```

### Error: "ChromaDB no disponible"
```bash
pip install chromadb
```

---

## 🔗 Relacionado

- **Notebook 02**: `02_multi_repository_validation.ipynb` (genera el grafo RDF)
- **Módulo LLM**: `llm/text_to_sparql.py` (conversor principal)
- **Base de Conocimiento**: `llm/rag_sparql_examples.py` (17 ejemplos)
- **Documentación**: `llm/README_LANGCHAIN_RAG.md` (arquitectura)

---

## ✅ Resultados Esperados

Al finalizar, deberías tener:

- ✅ **Success rate ≥70%** (7/10 queries válidas)
- ✅ **4 visualizaciones** de análisis
- ✅ **CSV exportado** con resultados detallados
- ✅ **Análisis RAG** mostrando ejemplos relevantes
- ✅ **Queries ejecutadas** contra grafo RDF real

Si el success rate es ≥70%, el sistema está listo para:
1. Integración con SearchEngine
2. Creación de notebook 04 (búsqueda end-to-end)
3. Implementación de evaluación (precision/recall)

---

**Estado**: ✅ Notebook completo y listo para ejecutar  
**Última actualización**: Enero 2024
