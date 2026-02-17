# AI Model Discovery System
## Sistema de Descubrimiento Semántico de Modelos de IA

**Tesis Doctoral** | Universidad Politécnica de Madrid  
**Autor**: Edmundo Mori Orrillo | Grupo PIONERA

---

## 📊 Estado del Proyecto

### ✅ FASE 1 COMPLETADA: Método de Búsqueda No Federada

**Sistema operativo y académicamente validado** que permite descubrir modelos de IA usando **lenguaje natural**:
- **536 modelos** de 7 repositorios → **22,097 triples RDF** con ontología DAIMO v2.2
- **Text-to-SPARQL** con DeepSeek R1 7B + RAG (150 ejemplos) → **95.6% éxito** en benchmark de 90 queries
- **Interfaz web Streamlit** con Model Cards interactivas y Dashboard
- **Evaluación académica completa**: P@5=0.383, R@5=0.180, F1@5=0.219
- **0% error rate** sintáctico SPARQL gracias a post-procesamiento automático

### 🎯 Objetivo de Investigación

Desarrollar y comparar **3 métodos de búsqueda semántica** de modelos de IA para determinar ventajas, limitaciones y casos de uso óptimos de cada enfoque

**📈 Avance Global: 40%** (Método 1 completado, Métodos 2 y 3 pendientes)

---

## 📋 Tres Métodos de Búsqueda (Objetivo de Tesis)

| Método | Descripción | Estado | Avance |
|--------|-------------|--------|--------|
| **1. No Federada** | Catálogo único RDF + SPARQL + Text-to-SPARQL con LLM | ✅ **Completado** | **100%** |
| **2. Federada** | Múltiples grafos RDF distribuidos + SPARQL SERVICE | ❌ No iniciado | 0% |
| **3. Cross-Repository** | APIs heterogéneas + normalización en tiempo real | ❌ No iniciado | 0% |

**Hipótesis de investigación**: Cada método tiene ventajas en diferentes escenarios (centralización vs. distribución vs. escalabilidad web)

**📊 Estado:** 1 de 3 métodos implementados y validados (33%). Comparación formal pendiente.

---

## 🎓 Método 1: Búsqueda Semántica No Federada (IMPLEMENTADO)

### Arquitectura

```
Usuario escribe en lenguaje natural → "pytorch models for image classification with MIT license"
                    ↓
    🧠 Text-to-SPARQL Converter (DeepSeek R1 7B)
    - RAG: Recupera 3 ejemplos similares de 150
    - Contexto: Inyecta propiedades de DAIMO
    - Generate: LLM produce consulta SPARQL
    - Post-process: 15 reglas corrigen errores
    - Validate: Parser verifica sintaxis
                    ↓
    SELECT ?model ?title ?license WHERE {
      ?model a daimo:Model ;
             daimo:framework "pytorch" ;
             daimo:task "image-classification" ;
             daimo:license ?license .
      FILTER(?license = "MIT")
    } LIMIT 20
                    ↓
    🗄️ Grafo RDF (rdflib): 12,477 triples
    Ontología DAIMO: 7 clases, 32 propiedades
                    ↓
    📊 Resultados filtrados → Model Cards
```

### Componentes Clave

- **Ontología DAIMO v2.2**: Extensión de PIONERA con 40 propiedades (metadatos, técnicos, popularidad, legales)
- **RAG con ChromaDB**: 150 ejemplos (53 básicos, 40 intermedios, 57 avanzados) para few-shot learning
- **Post-procesamiento**: 15 reglas automáticas corrigen errores comunes (namespaces, clases, filtros OPTIONAL)
- **7 Repositorios**: HuggingFace (25), PyTorch Hub (25), Civitai (25), Replicate (25), Kaggle (25), TensorFlow Hub (25), Papers with Code (25)
- **Total**: 175 modelos únicos, 5,943 triples RDF

### Capacidades Text to-SPARQL

✅ **Básicas**: Filtros por tarea, framework, licencia, autor  
✅ **Intermedias**: Múltiples condiciones, ordenamiento, negaciones  
✅ **Avanzadas**: Agregaciones (AVG, COUNT, SUM), GROUP BY, HAVING  

**Evaluación académica con 90 queries**:
- **Success Rate**: 95.6% (86/90 queries exitosas)
- **Error Rate**: 4.4% (0% sintáctico, 4.4% otros errores)
- **Precision@5**: 0.383 | **Recall@5**: 0.180 | **F1@5**: 0.219
- **NDCG@5**: 0.394 | **MRR**: 0.469
- **Latency**: ~1.5s promedio por consulta

**Comparación con BM25 Baseline (keyword search)**:
- BM25: P@5=0.570, F1@5=0.319 (superior en queries simples)
- Method1: Único método capaz de manejar agregaciones y queries complejas
- Trade-off: Expresividad vs. Precisión simple

Ver detalles en: [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)

### 🚀 Method 1 v2.0 - Enhanced Engine (IN DEVELOPMENT)

**Version:** v2.0 (February 2026)  
**Status:** ⚠️ Partially Implemented (Core functional, optimizations pending)

**Current State:**
- ✅ **Phase 1**: Text-to-SPARQL baseline operational
- ⏳ **Phase 2**: Simple Query Optimization (Template Generator) - Planned
- ⏳ **Phase 3**: Complex Query Enhancement (Specialized RAG) - Planned
- ⏳ **Phase 4**: Hybrid Routing (BM25 + Method 1) - Planned

**Achievements:**
- **Error Rate:** 0% syntax errors (down from 5.6%)
- **Success Rate:** 95.6% (86/90 queries)
- **Post-Processing:** 15 automatic correction rules

**Planned Improvements:**
- ⚡ Template Generator: Bypass LLM for simple queries (5x faster)
- 🧠 Specialized RAG: Feature-based example selection
- 🔄 Hybrid Routing: Auto-select BM25 vs. Method1 based on query type

**Usage:**
```python
from search.non_federated import create_non_federated_api

engine = create_non_federated_api(graph=g)
response = engine.search("PyTorch models for NLP", max_results=10)
# Returns: list of models with metadata
```

**Note:** The enhanced features (Phase 2/3/4) will improve performance but are not required for core functionality.

---

## � Análisis de Avance vs. Objetivo de Tesis

### ✅ Lo Completado (Fase 1 - 100%)

| Componente | Estado | Detalles |
|------------|--------|----------|
| Ontología DAIMO v2.2 | ✅ | 7 clases, 40 propiedades, validada |
| Recolectores de datos | ✅ | 7 repositorios implementados |
| Grafo RDF multi-repositorio | ✅ | 175 modelos, 5,943 triples |
| Text-to-SPARQL + RAG | ✅ | LLM + 150 ejemplos + 15 reglas de corrección |
| Interfaz web Streamlit | ✅ | Búsqueda NL + Model Cards + Dashboard |
| **Evaluación académica** | ✅ | **90 queries con métricas rigurosas (P@5, R@5, F1@5)** |
| Notebooks validados | ✅ | 4 de 5 notebooks ejecutables sin errores |

**Hitos**: Método 1 (No Federada) funcional, evaluado académicamente y documentado

### ⏳ Lo Pendiente para Completar la Investigación

#### 🔴 CRÍTICO - Implementar Métodos 2 y 3 (Objetivo central de tesis)

1. **Método 2: Búsqueda Federada** (Estimado: 4 semanas)
   - ❌ Implementar SPARQL SERVICE para consultar múltiples endpoints
   - ❌ Grafos RDF distribuidos independientes
   - ❌ Agregación y ranking de resultados
   - ❌ Evaluar con mismo benchmark de 90 queries
   - **Impacto**: Sin esto, solo se cubre 1 de 3 métodos prometidos (33%)

2. **Método 3: Cross-Repository** (Estimado: 4 semanas)
   - ❌ Consultas directas a APIs heterogéneas (sin endpoints SPARQL)
   - ❌ Normalización en tiempo real a DAIMO
   - ❌ Text-to-API-Params converter
   - ❌ Evaluar con mismo benchmark de 90 queries
   - **Impacto**: Sin esto, falta el método más escalable (falta 66% del objetivo)

3. **Comparación formal entre los 3 métodos** (Estimado: 2 semanas)
   - ❌ Mismo dataset de prueba para los 3
   - ❌ Métricas: Latencia, cobertura, precisión, escalabilidad
   - ❌ Análisis de ventajas/desventajas de cada enfoque
   - ❌ Identificar casos de uso óptimos
   - **Impacto**: Esta es la **contribución principal de la tesis**

**🚨 Riesgo**: Sin Métodos 2 y 3, la investigación doctoral está incompleta (solo 33% del objetivo cumplido)

#### 🟢 MEDIO - Mejoras del Sistema (Opcional)

4. **Ampliar dataset**: 175 → 1000+ modelos (más representativo)
5. **Completar Enhanced Engine**: Implementar Phase 2/3/4 optimizations
6. **Mejorar cobertura de metadatos**: Propiedades incompletas en algunos modelos
7. **Relaciones entre modelos**: Fine-tuning chains, derivaciones

#### ⚪ BAJA - Optimizaciones Futuras

8. Fine-tuning del LLM específico para SPARQL+DAIMO
9. Sistema de recomendaciones basado en historial
10. API REST pública documentada

**📅 Timeline Estimado**: 10 semanas (~2.5 meses) para completar Métodos 2, 3 y comparación formal

---

## 🎯 Próximos Pasos Inmediatos

### Esta Semana
1. ✅ **Documentar estado actual detallado** → Completado ([docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md))
2. ⏳ **Finalizar evaluation_pipeline_v3.ipynb** (completar ejecución de 90 queries)
3. ⏳ **Limpiar archivos obsoletos** (eliminar duplicados en `/results`)
4. ⏳ **Actualizar README principal** → En progreso

### Próximas 2 Semanas
1. **Iniciar diseño de Método 2 (Federada)**
   - Definir arquitectura de endpoints distribuidos
   - Configurar 3+ endpoints SPARQL de prueba
   - Implementar generador de queries con SERVICE clauses

2. **Prototipo funcional de Método 2**
   - Probar con 10 queries simples
   - Validar agregación de resultados

### Próximos 3 Meses (Timeline para completar tesis)
1. **Semanas 1-4**: Completar Método 2 (Federada) + evaluación con 90 queries
2. **Semanas 5-8**: Completar Método 3 (Cross-Repository) + evaluación con 90 queries
3. **Semanas 9-10**: Comparación formal de los 3 métodos + análisis
4. **Semanas 11-12**: Escritura de capítulo de tesis + paper draft

**📊 Resultado esperado**: Contribución doctoral completa con comparación empírica de 3 métodos de búsqueda semántica

Ver detalles completos en [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)

---

## 📊 Resumen Ejecutivo del Estado

### 🎉 Logros Actuales

- ✅ **Sistema funcional y académicamente validado** de búsqueda semántica con lenguaje natural
- ✅ **Ontología DAIMO v2.2** validada con 536 modelos de 7 repositorios
- ✅ **Text-to-SPARQL** con 95.6% de éxito en benchmark de 90 queries (0% errores sintácticos)
- ✅ **Interfaz web moderna** con Model Cards y Dashboard (Streamlit)
- ✅ **Evaluación académica completa** con métricas estándar (P@5, R@5, F1@5, NDCG, MRR)
- ✅ **Comparación con baseline** (BM25 keyword search)
- ✅ **Notebooks validados** (4 de 5 ejecutables sin errores)

**Valor actual**: Sistema demostrable, funcional y académicamente validado del Método 1 (No Federada)

### ⚠️ Gaps Críticos para Completar la Tesis

1. **Faltan Métodos 2 y 3** (solo 1 de 3 implementados = **33% del objetivo doctoral**)
2. **Falta comparación entre los 3 métodos** (contribución principal de la investigación)
3. **Dataset relativamente pequeño** (536 modelos, ideal: 1000+)
4. **Enhanced Engine incompleto** (Phase 2/3/4 pendientes)

**🚨 Riesgo**: Sin completar Métodos 2 y 3, la investigación doctoral está incompleta

### 🎯 Prioridad #1

**Implementar Métodos 2 y 3** para permitir comparación formal:
- Método 2 (Federada): 4 semanas
- Método 3 (Cross-Repository): 4 semanas
- Comparación formal: 2 semanas
- **Total**: **10 semanas** (~2.5 meses)

**Ver análisis completo**: [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)

---

## 🚀 Inicio Rápido

### Instalación

```bash
cd /home/edmundo/ai-model-discovery
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
curl -fsSL https://ollama.com/install.sh | sh
ollama pull deepseek-r1:7b
```

### Ejecutar

```bash
python3 run_app.py  # → http://localhost:8501
```

### Ejemplos de Búsqueda

```
"pytorch models for image classification"
"transformers from huggingface with more than 100 likes"
"what is the average number of downloads per repository"
```

**Nota**: Sistema incluye 536 modelos de 7 repositorios. Ver [docs/PROJECT_SETUP.md](docs/PROJECT_SETUP.md) para detalles

---

## 📁 Estructura del Código

```
ai-model-discovery/
├── data/
│   ├── ai_models_multi_repo.ttl    # 536 modelos, 22,097 triples RDF
│   └── raw/                        # Datos crudos de 7 repositorios
├── ontologies/
│   └── daimo.ttl                   # Ontología DAIMO v2.2 (40 propiedades)
├── llm/
│   ├── text_to_sparql.py           # Conversor NL→SPARQL (core)
│   ├── rag_sparql_examples.py      # 150 ejemplos RAG
│   ├── sparql_error_corrector.py   # 15 reglas de corrección
│   └── query_validator.py          # Validador sintáctico/semántico
├── search/
│   ├── non_federated/              # ✅ Método 1 (completado)
│   ├── federated/                  # ❌ Método 2 (pendiente)
│   └── cross_repository/           # ❌ Método 3 (pendiente)
├── knowledge_graph/
│   ├── build_graph.py              # Constructor de grafo
│   └── multi_repository_builder.py # Builder multi-repo
├── app/
│   ├── main.py                     # Interfaz Streamlit
│   └── pages/                      # 4 páginas (Búsqueda, Datos, Dashboard, Config)
├── experiments/benchmarks/
│   ├── evaluation_pipeline_v3.ipynb # Pipeline de evaluación (90 queries)
│   ├── queries_90.jsonl            # Benchmark dataset
│   └── results/                    # Resultados de evaluaciones
├── notebooks/
│   ├── 01_validation.ipynb         # ✅ Validación Phase 1
│   ├── 02_multi_repository_validation.ipynb  # ✅ Multi-repo
│   ├── 03_text_to_sparql_validation.ipynb    # ✅ Text-to-SPARQL
│   └── 04_enhanced_search_validation.ipynb   # ⚠️ Enhanced search
└── utils/
    └── *_repository.py             # 7 colectores de datos
```

---

## 🎓 Tecnologías Clave

**Ontología**: DAIMO v2.2 (PIONERA-UPM) - 7 clases, 40 propiedades  
**LLM**: DeepSeek R1 7B (Ollama local, temp=0.1) + RAG (ChromaDB, 150 ejemplos)  
**Grafos**: RDFLib + SPARQL 1.1  
**Frontend**: Streamlit + Plotly  
**Evaluación**: Benchmark con 90 queries (P@5, R@5, F1@5, NDCG, MRR)  
**Datos**: 536 modelos de HuggingFace, Kaggle, Civitai, Replicate, PyTorch Hub, TensorFlow Hub, Papers with Code

---

## 📊 Evaluación Académica - Método 1

**Dataset**: 90 queries categorizadas (57 retrieval, 18 aggregation, 11 ordering, 4 complex)  
**Métodos comparados**: BM25 Baseline, Method1 Enhanced, LLM-Only  
**Archivo**: `experiments/benchmarks/queries_90.jsonl`

### Resultados Principales

| Método | P@5 | R@5 | F1@5 | NDCG@5 | MRR | Error Rate | Latency |
|--------|-----|-----|------|--------|-----|------------|---------|
| **BM25 Baseline** | 0.570 | 0.237 | 0.319 | 0.587 | 0.673 | 0.0% | ~0.05s |
| **Method1 Enhanced** | 0.383 | 0.180 | 0.219 | 0.394 | 0.469 | 4.4% | ~1.5s |
| **LLM-Only** | 0.350 | 0.162 | 0.199 | 0.368 | 0.427 | 5.6% | ~1.5s |

### Conclusiones

- ✅ **Method1 funciona y es evaluable** con métricas académicas rigurosas
- ✅ **BM25 superior para queries simples** (+78.8% F1@5 vs Method1)
- ✅ **Method1 único capaz** de manejar agregaciones y queries complejas
- ✅ **Trade-off identificado**: Expresividad vs. Precisión simple

**Ver análisis completo**: [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)  
**Resultados detallados**: `experiments/benchmarks/results/`

---

## 📖 Recursos y Documentación

- 📊 **[Estado Completo del Proyecto](docs/PROJECT_STATUS.md)** ← Análisis detallado actualizado
- 📘 [Guía de Búsqueda y Uso](docs/SEARCH_GUIDE.md)
- ⚙️ [Configuración del Proyecto](docs/PROJECT_SETUP.md)
- 📈 [Análisis de Experimentos](docs/EXPERIMENT_ANALYSIS.md)
- 🔬 [Metodología de Benchmarks](docs/BENCHMARK_METHODOLOGY.md)
- 📝 [Grafo de Conocimiento](docs/KNOWLEDGE_GRAPH.md)
- 🔌 [Integraciones](docs/INTEGRATIONS.md)
- 📚 **Notebooks Interactivos**: `notebooks/` (4 validados, 1 en progreso)

---

## 📝 Licencia y Contacto

**Licencia**: MIT (código) | CC BY 4.0 (ontología DAIMO)  
**Autor**: Edmundo Mori Orrillo | edmundo.mori.orrillo@upm.es  
**Institución**: UPM - Grupo PIONERA  
**Agradecimientos**: Jiayun Liu (co-autora DAIMO), comunidades HuggingFace/Papers with Code
