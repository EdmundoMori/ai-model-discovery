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
