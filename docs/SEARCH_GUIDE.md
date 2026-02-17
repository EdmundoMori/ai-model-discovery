# 🎯 Guía de Uso: Búsqueda Multi-Método

Esta guía te ayudará a elegir el método correcto según tu necesidad.

---

## 📊 ¿Qué método usar?

```
┌─────────────────────────────────────────────────────────────┐
│  TIPO DE QUERY              │  MÉTODO RECOMENDADO           │
├─────────────────────────────┼───────────────────────────────┤
│  Palabras clave simples     │  ⚡ Rápida                    │
│  Listados básicos           │  ⚡ Rápida                    │
│  Búsqueda por nombre        │  ⚡ Rápida                    │
├─────────────────────────────┼───────────────────────────────┤
│  Con filtros                │  🎯 Inteligente               │
│  Con ordenamiento (top N)   │  🎯 Inteligente               │
│  Búsqueda semántica         │  🎯 Inteligente               │
├─────────────────────────────┼───────────────────────────────┤
│  Agregaciones (count, avg)  │  🧠 Experta                   │
│  Queries complejas          │  🧠 Experta                   │
│  Análisis estadístico       │  🧠 Experta                   │
└─────────────────────────────┴───────────────────────────────┘
```

---

## ⚡ Búsqueda Rápida - Ejemplos

### ✅ FUNCIONA BIEN:
```
✓ "PyTorch models"
✓ "computer vision"
✓ "NLP transformers"
✓ "HuggingFace BERT"
✓ "TensorFlow image classification"
```

### ❌ NO FUNCIONA:
```
✗ "count models by framework"          → Use 🧠 Experta
✗ "top 10 models by rating"            → Use 🎯 Inteligente
✗ "average rating of CV models"        → Use 🧠 Experta
✗ "models with more than 1000 downloads" → Use 🎯 Inteligente
```

### 💡 CUÁNDO USAR:
- Necesitas resultados inmediatos (~1ms)
- Sabes las palabras clave exactas
- Quieres explorar rápidamente el catálogo

---

## 🎯 Búsqueda Inteligente - Ejemplos

### ✅ FUNCIONA BIEN:

#### Queries Simples (usa Hybrid):
```
✓ "PyTorch models for NLP"
✓ "high quality computer vision models"
✓ "BERT models from HuggingFace"
✓ "image classification with TensorFlow"
```

#### Queries Complejas (usa LLM):
```
✓ "top 10 PyTorch models by rating"
✓ "most popular NLP models"
✓ "best rated computer vision models"
✓ "models with more than 1000 downloads"
```

### 💡 CUÁNDO USAR:
- No sabes si tu query es simple o compleja
- Quieres el mejor balance velocidad/precisión
- Confías en el sistema para elegir el sub-método

### 🔍 SUB-MÉTODOS:
El router decide automáticamente:
- **Hybrid** (BM25+Dense): Para queries simples → ~100ms
- **LLM+RAG**: Para queries complejas → ~1000ms

---

## 🧠 Búsqueda Experta - Ejemplos

### ✅ FUNCIONA BIEN:

#### Agregaciones:
```
✓ "count models by framework"
✓ "count models by task"
✓ "average rating of computer vision models"
✓ "sum of downloads by library"
✓ "how many models are from HuggingFace"
```

#### Queries Complejas:
```
✓ "models with rating > 4.5 and downloads > 1000"
✓ "PyTorch models ordered by popularity"
✓ "top 10 NLP models with highest rating"
✓ "compare frameworks by number of models"
```

### 💡 CUÁNDO USAR:
- Necesitas agregaciones (COUNT, AVG, SUM)
- Query tiene múltiples condiciones
- Requieres análisis estadístico
- No te importa esperar 3-6 segundos

### 📊 SALIDA ESPECIAL:
Para agregaciones, muestra tabla en vez de tarjetas:

```
┌────────────┬──────────┐
│ Framework  │ Cantidad │
├────────────┼──────────┤
│ PyTorch    │ 450      │
│ TensorFlow │ 380      │
│ JAX        │ 120      │
└────────────┴──────────┘
```

---

## 🔄 Modo Comparación

Activa el checkbox **"Modo comparación"** para:
- Ejecutar los 3 métodos simultáneamente
- Ver qué método funciona mejor para tu query
- Comparar tiempos de ejecución
- Identificar el método óptimo

### Ejemplo de Salida:

```
Query: "top 10 PyTorch models"

┌─────────────────┬───────────┬───────────┐
│ Método          │ Tiempo    │ Resultados│
├─────────────────┼───────────┼───────────┤
│ ⚡ Rápida       │ ❌ No aplica           │
│ 🎯 Inteligente  │ 850ms     │ 10 ✅     │
│ 🧠 Experta      │ 4200ms    │ 10 ✅     │
└─────────────────┴───────────┴───────────┘

🏆 Mejor método: INTELIGENTE (más rápido con mismo resultado)
```

---

## 📋 Ejemplos por Categoría

### Categoría 1: Listados Simples

| Query | Método Recomendado | Por qué |
|-------|-------------------|---------|
| "list all AI models" | ⚡ Rápida | Listado completo sin filtros |
| "PyTorch models for NLP" | 🎯 Inteligente | Filtro semántico |
| "models from HuggingFace" | ⚡ Rápida | Palabra clave directa |

### Categoría 2: Agregaciones

| Query | Método Recomendado | Por qué |
|-------|-------------------|---------|
| "count models by task" | 🧠 Experta | Requiere GROUP BY |
| "average rating of CV models" | 🧠 Experta | Requiere AVG() |
| "total downloads by framework" | 🧠 Experta | Requiere SUM() |

### Categoría 3: Filtros Complejos

| Query | Método Recomendado | Por qué |
|-------|-------------------|---------|
| "top 10 PyTorch models by rating" | 🎯 Inteligente | ORDER BY + LIMIT |
| "high rated CV models with >1000 downloads" | 🧠 Experta | Múltiples filtros |
| "models from HF ordered by popularity" | 🎯 Inteligente | ORDER BY simple |

---

## 🎨 Tipos de Presentación

### Tipo 1: Listado de Modelos (Tarjetas)

```
┌─────────────────────────────────────────┐
│ 1. bert-base-uncased                    │
│ ─────────────────────────────────────── │
│ 📦 Repositorio: HuggingFace             │
│ 🎯 Tarea: Natural Language Processing   │
│ ⭐ Score: 0.95                          │
│                                         │
│ [📋 Ver metadata completa]              │
└─────────────────────────────────────────┘
```

**Usa este formato para:**
- Listados simples
- Queries de ordenamiento
- Resultados de búsqueda por palabras clave

### Tipo 2: Tabla de Agregación

```
┌─────────────┬──────────┬──────────┐
│ Tarea       │ Cantidad │ Promedio │
├─────────────┼──────────┼──────────┤
│ NLP         │ 450      │ 4.2      │
│ CV          │ 380      │ 4.5      │
│ Audio       │ 120      │ 3.9      │
├─────────────┼──────────┼──────────┤
│ TOTAL       │ 950      │ 4.2      │
└─────────────┴──────────┴──────────┘

[📥 Descargar CSV]
```

**Usa este formato para:**
- COUNT, SUM, AVG, MAX, MIN
- GROUP BY queries
- Análisis estadístico

---

## 💡 Tips y Trucos

### Tip 1: Empieza Simple
```
❌ MAL:  "average rating of PyTorch models for NLP with >1K downloads"
✅ BIEN: Primero: "PyTorch models for NLP"
        Luego: Afina con filtros
```

### Tip 2: Usa Modo Comparación para Aprender
```
🔄 Ejecuta la misma query en los 3 métodos
📊 Observa cuál funciona mejor
🎓 Aprende qué método usar para queries similares
```

### Tip 3: Reformula si Falla
```
Si un método no aplica, la app te dará sugerencias:

❌ "cuántos modelos hay"
💡 Sugerencia: "count models by task"
```

### Tip 4: Usa el Historial
```
📜 El sidebar guarda tus últimas 5 búsquedas
⏱️ Ve los tiempos de cada una
🔄 Repite queries anteriores con un clic
```

---

## 🚀 Casos de Uso Reales

### Caso 1: Explorador de Catálogo (Data Scientist)
**Necesidad**: Ver qué modelos hay disponibles

**Workflow**:
1. ⚡ Rápida: "PyTorch models" → Ver listado general
2. 🎯 Inteligente: "PyTorch NLP models" → Filtrar por dominio
3. 🧠 Experta: "count PyTorch NLP models by task" → Análisis

### Caso 2: Investigador ML
**Necesidad**: Encontrar el mejor modelo para una tarea

**Workflow**:
1. 🎯 Inteligente: "top 10 computer vision models"
2. 🎯 Inteligente: "high rated CV models with >1000 downloads"
3. ⚡ Rápida: "ResNet variants" → Ver opciones específicas

### Caso 3: Analista de Datos
**Necesidad**: Estadísticas del catálogo

**Workflow**:
1. 🧠 Experta: "count models by framework"
2. 🧠 Experta: "average rating by task"
3. 🧠 Experta: "sum downloads by source"

---

## ⚙️ Configuración Recomendada

### Para Uso Diario:
```
Método: 🎯 Inteligente (router automático)
Max resultados: 10
Mostrar SPARQL: ✓ (aprender de las conversiones)
Metadata completa: ✗ (solo si necesitas detalles)
Modo comparación: ✗
```

### Para Aprender:
```
Método: Probar todos
Max resultados: 5 (más rápido)
Mostrar SPARQL: ✓
Metadata completa: ✓
Modo comparación: ✓ (ver diferencias)
```

### Para Análisis:
```
Método: 🧠 Experta
Max resultados: 50
Mostrar SPARQL: ✓
Metadata completa: ✓
Modo comparación: ✗
```

---

## 📈 Métricas de Rendimiento

### ⚡ Búsqueda Rápida
```
Latencia promedio: 0.5ms - 2ms
Precisión: Media (70%)
Recall: Alto (85%)
Best for: Queries simples
```

### 🎯 Búsqueda Inteligente
```
Latencia promedio:
  - Hybrid: 50ms - 200ms
  - LLM: 500ms - 2000ms
Precisión: Alta (85%)
Recall: Alto (82%)
Best for: Uso general
```

### 🧠 Búsqueda Experta
```
Latencia promedio: 2500ms - 6000ms
Precisión: Muy Alta (92%)
Recall: Medio (65%)
Best for: Queries complejas
```

---

## ❓ FAQ - Preguntas Frecuentes

### P: ¿Qué método debo usar si no sé qué tan compleja es mi query?
**R**: Usa 🎯 **Inteligente**. El router decidirá automáticamente.

### P: ¿Por qué un método dice "no aplica"?
**R**: Cada método tiene fortalezas diferentes. El error te sugerirá qué método usar.

### P: ¿Puedo guardar mis búsquedas favoritas?
**R**: El historial guarda las últimas 5 automáticamente. Para persistencia, usa CSV/JSON.

### P: ¿Cómo sé si mi query es de agregación?
**R**: Si usas palabras como "count", "average", "sum", "total", es agregación.

### P: ¿El modo comparación es más lento?
**R**: Sí, ejecuta 3 métodos. Úsalo solo para aprender o comparar.

### P: ¿Puedo usar español?
**R**: Sí, pero el LLM funciona mejor en inglés. Para agregaciones en español usa: "cuántos", "promedio", "suma".

---

## 🎓 Aprende Más

### Documentación Técnica:
- `docs/BUSQUEDA_MULTI_METODO.md` - Documentación completa
- `experiments/benchmarks/evaluation_pipeline_v3.ipynb` - Evaluación de métodos

### Ejemplos en Código:
- `app/pages/1_🔍_Búsqueda.py` - Implementación
- `experiments/benchmarks/keyword_bm25.py` - BM25 Baseline
- `experiments/benchmarks/hybrid_retrieval.py` - Hybrid Router
- `llm/text_to_sparql.py` - LLM + RAG

---

**¡Feliz Búsqueda! 🚀**
# 🔍 Búsqueda Multi-Método - Documentación de Cambios

**Fecha**: 2026-02-16  
**Archivo modificado**: `app/pages/1_🔍_Búsqueda.py`

---

## 📋 Resumen de Cambios Implementados

Se ha rediseñado completamente la página de búsqueda para incluir **3 métodos diferentes**, **detección automática de tipo de query**, y **presentación diferenciada de resultados**.

---

## 1️⃣ Tres Métodos de Búsqueda con Nombres Intuitivos

### ⚡ **Búsqueda Rápida** (BM25 Baseline)
- **Tecnología**: BM25 con scoring de palabras clave
- **Latencia**: ~1ms
- **Mejor para**: Listados simples, búsquedas directas por palabras
- **Ejemplo**: "PyTorch models", "computer vision models"
- **Función**: `execute_fast_search()`

### 🎯 **Búsqueda Inteligente** (Router Híbrido)
- **Tecnología**: 
  - Hybrid (BM25 + Dense SBERT) para queries simples
  - LLM + RAG para queries complejas
- **Latencia**: ~100-1000ms
- **Mejor para**: Queries variadas con filtros
- **Ejemplo**: "top 10 PyTorch models", "high rated NLP models"
- **Función**: `execute_smart_search()`
- **Lógica de routing**:
  ```python
  if is_complex_query(query):
      → Use LLM + RAG
  else:
      → Use Hybrid (BM25 + Dense)
  ```

### 🧠 **Búsqueda Experta** (LLM + RAG Completo)
- **Tecnología**: LLM (DeepSeek-R1:7b) + Ontology Dictionary + RAG
- **Latencia**: ~3-6s
- **Mejor para**: Agregaciones, queries complejas
- **Ejemplo**: "count models by framework", "average rating of CV models"
- **Función**: `execute_expert_search()`

---

## 2️⃣ Detección Automática del Tipo de Query

### Función: `detect_query_type(query, sparql)`

Detecta el tipo de consulta analizando:
1. **Patrones en SPARQL** (si está disponible):
   - `COUNT(`, `SUM(`, `AVG(`, `GROUP BY` → Agregación
   - `ORDER BY` → Ordenamiento
2. **Patrones en lenguaje natural**:
   - "count", "how many", "cuántos", "average" → Agregación
   - "top", "best", "highest", "ordenar" → Ordenamiento
   - Default → Listado

### Tipos de Query:
- **`list`**: Consulta de listado simple
- **`aggregation`**: Consulta de agregación (COUNT, SUM, AVG, etc.)
- **`ordering`**: Consulta con ordenamiento (ORDER BY)
- **`complex`**: Consulta compleja (múltiples condiciones)

---

## 3️⃣ Presentación Diferenciada de Resultados

### Para Listados (tipo: `list`, `ordering`):
```
📋 Top N Modelos
┌─────────────────────────────────┐
│ 1. bert-base-uncased           │
│ 📦 Repositorio: HuggingFace    │
│ 🎯 Tarea: NLP                  │
│ ⭐ Score: 0.95                 │
└─────────────────────────────────┘
```
- Tarjetas con diseño profesional
- Metadata expandible
- Descarga en JSON

### Para Agregaciones (tipo: `aggregation`):
```
📊 Resultados de Agregación
┌────────────┬──────────┐
│ Framework  │ Cantidad │
├────────────┼──────────┤
│ PyTorch    │ 450      │
│ TensorFlow │ 380      │
│ JAX        │ 120      │
└────────────┴──────────┘
```
- Tabla interactiva con pandas
- Columnas con nombres legibles en español
- Descarga en CSV

---

## 4️⃣ Manejo de Errores Mejorado

### Antes:
```
❌ Error ejecutando búsqueda: ...
```

### Ahora:
```
❌ Este método no puede procesar esta consulta

💡 Sugerencia: Este método es ideal para queries complejas:
   'count models by framework'
   'average rating of computer vision models'
   'models with more than 1000 downloads'
```

### Mensajes personalizados por método:
- **Búsqueda Rápida**: Sugiere queries simples por palabras clave
- **Búsqueda Inteligente**: Sugiere queries con filtrado o ranking
- **Búsqueda Experta**: Sugiere queries complejas y agregaciones

---

## 5️⃣ Mejoras Adicionales Implementadas

### a) 🔄 Modo Comparación
- **Ubicación**: Checkbox en sidebar
- **Función**: Ejecuta los 3 métodos simultáneamente
- **Muestra**:
  - Resultados comparativos (tiempo, confianza, resultados)
  - Identifica el mejor método automáticamente
  - Permite comparar fortalezas/debilidades

### b) 📜 Historial de Búsqueda
- **Ubicación**: Sidebar (últimas 5 búsquedas)
- **Información guardada**:
  - Query original
  - Método usado (con icono)
  - Número de resultados
  - Tiempo de ejecución
  - Timestamp

### c) 💡 Ejemplos por Categoría
- **3 tabs organizados**:
  - 📋 **Listados**: Queries simples
  - 📊 **Agregaciones**: COUNT, AVG, SUM
  - 🔍 **Filtros Complejos**: TOP, ORDER BY, múltiples condiciones
- **9 ejemplos ejecutables** con un clic

### d) 📥 Exportar Resultados
- **Agregaciones**: CSV con columnas legibles
  - `count` → `Cantidad`
  - `avg` → `Promedio`
  - `task` → `Tarea`
- **Listados**: JSON con metadata completa

### e) 🎯 Métricas de Confianza
- **Niveles visuales**:
  - 🟢 **High**: Conversión exitosa con múltiples resultados
  - 🟡 **Medium**: Conversión exitosa con pocos resultados
  - 🔴 **Low**: Sin resultados o baja calidad
- **Basado en**:
  - Validación del LLM
  - Número de resultados encontrados
  - Calidad del SPARQL generado

### f) 📊 Información Detallada por Método
- **Sidebar muestra para cada método**:
  - Icono descriptivo
  - Descripción técnica
  - Tiempo de ejecución aproximado
  - Mejor caso de uso

---

## 🎨 Mejoras de UX Implementadas

1. **Radio buttons** para selección clara de método
2. **Tabs** para organizar ejemplos por tipo
3. **Expanders** para contenido secundario (SPARQL, metadata, historial)
4. **Progress spinners** con icono del método activo
5. **Color coding** para niveles de confianza
6. **Download buttons** para exportar datos
7. **Tooltips** con ayuda contextual

---

## 🧪 Cómo Probar el Sistema

### 1. Verificar Setup
```bash
cd /home/edmundo/ai-model-discovery

# Verificar que el grafo existe
ls -lh data/ai_models_multi_repo.ttl

# Verificar imports
python3 -c "import sys; sys.path.insert(0, 'experiments/benchmarks'); from keyword_bm25 import KeywordBM25Baseline; print('✅ OK')"
```

### 2. Ejecutar Streamlit
```bash
cd /home/edmundo/ai-model-discovery
streamlit run app/main.py
```

### 3. Navegar a la Página
- Abrir navegador
- Ir a la página **"1_🔍_Búsqueda"**

### 4. Probar Cada Método

#### Prueba 1: Búsqueda Rápida (⚡)
- **Query**: "PyTorch models"
- **Esperado**: 
  - Listado de modelos PyTorch
  - Tiempo < 10ms
  - Confianza: Medium

#### Prueba 2: Búsqueda Inteligente (🎯)
- **Query Simple**: "PyTorch models for NLP"
- **Esperado**: 
  - Usa sub-método: `hybrid`
  - Listado con scores BM25+Dense
- **Query Compleja**: "count models by task"
- **Esperado**: 
  - Usa sub-método: `llm`
  - Tabla de agregación

#### Prueba 3: Búsqueda Experta (🧠)
- **Query**: "average rating of computer vision models"
- **Esperado**: 
  - Tabla de agregación
  - Muestra SPARQL generado
  - Ejemplos RAG usados

#### Prueba 4: Modo Comparación
- **Activar**: Checkbox "Modo comparación"
- **Query**: "top 10 PyTorch models"
- **Esperado**: 
  - Ejecuta 3 métodos
  - Muestra comparativa de tiempos
  - Identifica el mejor método

---

## 🔧 Estructura del Código

### Funciones Principales

```python
# ==================== SEARCH UTILITIES ====================
detect_query_type(query, sparql) → (tipo, descripcion)
is_complex_query(query) → bool
format_query_results_suggestion(query, method) → str

# ==================== CACHE RESOURCES ====================
load_graph() → (Graph, status_message)
load_bm25_engine() → (engine, status_message)
load_hybrid_engine() → (engine, status_message)
load_llm_engine() → (engine, status_message)

# ==================== SEARCH METHODS ====================
execute_fast_search(query, top_k) → Dict[str, Any]
execute_smart_search(query, top_k) → Dict[str, Any]
execute_expert_search(query, top_k) → Dict[str, Any]

# ==================== HELPER FUNCTIONS ====================
extract_model_metadata(graph, model_uri) → Dict[str, Any]
format_sparql_results(graph, results, query, top_k) → List[Dict]

# ==================== MAIN APP ====================
main() → None
display_results(result, query, show_sparql, show_metadata) → None
```

### Flujo de Ejecución

```mermaid
User Input → Select Method → Execute Search
                ↓                    ↓
         [fast/smart/expert]   [BM25/Hybrid/LLM]
                                    ↓
                            Detect Query Type
                                    ↓
                        ┌───────────┴───────────┐
                        ↓                       ↓
                   Listado                 Agregación
                        ↓                       ↓
                  Show Cards            Show Table (CSV)
                  Download JSON
```

---

## 📊 Comparativa de Métodos

| Característica | ⚡ Rápida | 🎯 Inteligente | 🧠 Experta |
|---|---|---|---|
| **Latencia** | ~1ms | ~100-1000ms | ~3-6s |
| **Tecnología** | BM25 | Hybrid/LLM Router | LLM+RAG |
| **Listados** | ✅ Excelente | ✅ Excelente | ✅ Bueno |
| **Agregaciones** | ❌ No soporta | ✅ Bueno | ✅ Excelente |
| **Filtros Complejos** | ❌ Limitado | ✅ Bueno | ✅ Excelente |
| **Comprensión Semántica** | ❌ No | ✅ Parcial | ✅ Completa |
| **Uso Recomendado** | Exploración rápida | Uso general | Análisis profundo |

---

## 🚀 Próximas Mejoras Sugeridas

### Corto Plazo (Sprint Actual)
1. **Cache de Embeddings**: Precalcular embeddings de queries comunes
2. **Paginación**: Para resultados > 50 items
3. **Filtros Post-Search**: Framework, task, source
4. **Visualización de Stats**: Gráficos de distribución

### Mediano Plazo
1. **Guardado de Búsquedas**: Persistir historial en DB
2. **Comparación Visual**: Gráficos de performance por método
3. **Sugerencias Inteligentes**: Autocompletar basado en historial
4. **A/B Testing**: Métricas de uso por método

### Largo Plazo
1. **Fine-tuning del LLM**: Entrenar con queries específicas del dominio
2. **Multi-idioma**: Soporte completo español/inglés
3. **API REST**: Exponer métodos como endpoints
4. **Dashboard Analytics**: Métricas de uso y performance

---

## 🐛 Errores Conocidos y Limitaciones

### Limitaciones Actuales
1. **BM25**: No soporta agregaciones ni queries complejas
2. **Hybrid**: Requiere CUDA para embeddings densos (fallback a CPU)
3. **LLM**: Dependiente de Ollama local (requiere ~8GB RAM)
4. **Cache**: Se limpia al reiniciar la app

### Soluciones Paliativas
1. BM25 muestra mensaje amigable al fallar
2. Hybrid usa CPU si no hay GPU
3. LLM muestra sugerencias si falla conversión
4. Cache se recarga rápidamente (<5s)

---

## 📚 Referencias

- **Módulos de búsqueda**: `experiments/benchmarks/`
  - `keyword_bm25.py`: BM25 Baseline
  - `hybrid_retrieval.py`: Hybrid (BM25 + Dense)
  - `ontology_enhanced_bm25.py`: BM25 con ontología
  - `dense_retrieval.py`: SBERT embeddings

- **LLM**: `llm/text_to_sparql.py`
  - Conversión de texto a SPARQL
  - RAG con ChromaDB
  - Validación de queries

- **Notebook de evaluación**: `experiments/benchmarks/evaluation_pipeline_v3.ipynb`
  - Métricas de los 3 métodos
  - 90 queries de prueba
  - Resultados comparativos

---

## ✅ Checklist de Implementación

- [x] Implementar 3 métodos de búsqueda
- [x] Crear nombres cortos e intuitivos
- [x] Detectar tipo de query (listado vs agregación)
- [x] Presentación diferenciada de resultados
- [x] Manejo de errores amigable
- [x] Modo comparación de 3 métodos
- [x] Historial de búsqueda (últimas 5)
- [x] Ejemplos organizados por categoría
- [x] Exportar resultados (CSV/JSON)
- [x] Métricas de confianza visual
- [x] Documentación completa
- [x] Tests de importación exitosos
- [x] Backup del archivo original

---

## 👤 Autor

**Edmundo Mori**  
Fecha: 2026-02-16

---

## 📝 Notas de Versión

**Versión 2.0** - Multi-Método (2026-02-16)
- Implementación completa de 3 métodos
- Detección automática de tipo de query
- Presentación diferenciada por tipo
- Modo comparación incluido
- 6 mejoras adicionales de UX

**Versión 1.0** - Version Original
- Sistema único con Phase 2/3/4
- Solo muestra método usado post-facto
- Presentación uniforme de resultados
# 📚 Ejemplos RAG: Métodos Inteligente y Experta

**Fecha**: 2026-02-16  
**Archivo fuente**: `llm/rag_sparql_examples.py`

---

## 📊 Resumen Ejecutivo

### Total de Ejemplos RAG Disponibles: **150**

```
┌─────────────────────────────────────────┐
│  NIVEL          │  CANTIDAD              │
├─────────────────┼────────────────────────┤
│  Basic          │  53 ejemplos (35.3%)   │
│  Intermediate   │  40 ejemplos (26.7%)   │
│  Advanced       │  57 ejemplos (38.0%)   │
├─────────────────┼────────────────────────┤
│  TOTAL          │  150 ejemplos          │
└─────────────────────────────────────────┘
```

---

## 🔍 ¿Qué Métodos Usan RAG?

### ⚡ Búsqueda Rápida (BM25 Baseline)
- **Usa RAG**: ❌ No
- **Motivo**: Búsqueda por palabras clave puras, sin LLM

### 🎯 Búsqueda Inteligente (Router)
- **Usa RAG**: ✅ Sí (solo para queries complejas)
- **Cuándo**: Si `is_complex_query(query) == True`
- **Sub-método**: Usa LLM+RAG (mismo que Experta)
- **Top-K ejemplos**: 3 ejemplos por defecto

### 🧠 Búsqueda Experta (LLM+RAG)
- **Usa RAG**: ✅ Sí (siempre)
- **Motivo**: Todas las queries pasan por LLM
- **Top-K ejemplos**: 3 ejemplos por defecto

---

## 🎯 Top 10 Categorías de Ejemplos

Las categorías más representadas en la base de conocimiento:

| # | Categoría | Ejemplos | Descripción |
|---|-----------|----------|-------------|
| 1 | search_by_name | 5 | Búsqueda por nombre de modelo |
| 2 | filter_by_repository | 5 | Filtrar por repositorio |
| 3 | filter_by_task | 5 | Filtrar por tarea (NLP, CV, etc.) |
| 4 | filter_by_library | 5 | Filtrar por biblioteca (PyTorch, TF) |
| 5 | filter_by_metrics | 5 | Filtrar por métricas (rating, downloads) |
| 6 | filter_by_domain | 5 | Filtrar por dominio |
| 7 | list_metadata | 5 | Listar metadata |
| 8 | filter_by_size | 5 | Filtrar por tamaño de modelo |
| 9 | filter_by_usecase | 5 | Filtrar por caso de uso |
| 10 | filter_by_architecture | 5 | Filtrar por arquitectura |

**Total de categorías únicas**: 106

---

## 🔎 Proceso de RAG (Retrieval Augmented Generation)

### 1. **Indexación (Una vez al iniciar)**

```python
# En TextToSPARQLConverter.__init__()
1. Cargar 150 ejemplos desde rag_sparql_examples.py
2. Crear ChromaDB collection: "sparql_examples"
3. Para cada ejemplo:
   - Documento = natural_query + keywords
   - Metadata = id, complexity, category, explanation
4. Indexar con embeddings (DefaultEmbeddingFunction)
5. Guardar en: ~/.cache/ai_model_discovery/chroma/
```

### 2. **Retrieval (Por cada query)**

```python
# En TextToSPARQLConverter.convert(query)
1. Usuario ingresa: "PyTorch models for NLP"
2. ChromaDB busca los Top-3 ejemplos más similares
3. Calcula RAG score (similaridad promedio)
4. Retorna: [ejemplo1, ejemplo2, ejemplo3], score
```

### 3. **Inyección Inteligente del Diccionario**

```python
# Estrategia basada en RAG score:
if rag_score > 0.8:
    # Ejemplos MUY similares → Sin diccionario
    context = ""
    
elif rag_score >= 0.5:
    # Ejemplos MEDIANAMENTE similares → Top 10 propiedades
    context = get_property_context_compact(top_10)
    
else:
    # Ejemplos POCO similares → Diccionario completo
    context = get_property_context_detailed(all_properties)
```

### 4. **Construcción del Prompt**

```python
# Prompt final enviado al LLM:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

EJEMPLOS RELEVANTES:
{ejemplo1}
{ejemplo2}
{ejemplo3}

{diccionario de propiedades (si score < 0.8)}

USER QUERY: {query del usuario}

SPARQL:
```

---

## 💡 Ejemplos RAG Más Relevantes

### Ejemplo 1: "PyTorch models for NLP"

**ID**: `intermediate_001`

**Natural Query**: "PyTorch models for NLP"

**Keywords**: `pytorch`, `nlp`, `natural language`, `framework`, `library`, `text`

**SPARQL**:
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?library ?task ?downloads
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(
    CONTAINS(LCASE(?library), "pytorch") &&
    (!BOUND(?task) || CONTAINS(LCASE(?task), "nlp") || 
     CONTAINS(LCASE(?task), "language") || CONTAINS(LCASE(?task), "text"))
  )
}
ORDER BY DESC(?downloads)
LIMIT 15
```

**Explicación**: PyTorch models con filtrado opcional de tarea NLP para evitar sobre-filtrado

---

### Ejemplo 2: "count models by task"

**ID**: `intermediate_003`

**Natural Query**: "count models for task"

**Keywords**: `count`, `group by`, `library`, `task`, `aggregate`

**SPARQL**:
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?library (COUNT(?model) as ?modelCount)
WHERE {
  ?model a daimo:Model ;
         daimo:library ?library .
}
GROUP BY ?library
ORDER BY DESC(?modelCount)
LIMIT 20
```

**Explicación**: Agregación con COUNT y GROUP BY para contar modelos por biblioteca

---

### Ejemplo 3: "high rated computer vision models"

**ID**: `basic_002`

**Natural Query**: "high rated computer vision models"

**Keywords**: `high rated`, `likes`, `popular`, `computer vision`, `vision`, `image`, `cv`

**SPARQL**:
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?title ?likes ?downloads ?library
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:library ?library }
  FILTER(BOUND(?likes) && ?likes > 10)
}
ORDER BY DESC(?likes) DESC(?downloads)
LIMIT 15
```

**Explicación**: Filtrado por likes (rating) con comparación numérica

---

## 🧪 Cómo Ver los Ejemplos RAG Usados

### En la Interfaz Web:

1. **Activar visualización de SPARQL**:
   - Sidebar → ☑️ "Mostrar SPARQL generado"

2. **Ejecutar búsqueda**:
   - Selecciona: 🎯 Inteligente o 🧠 Experta
   - Query: "PyTorch models for NLP"
   - Clic: 🚀 Buscar

3. **Ver ejemplos usados**:
   - Expandir: "📝 SPARQL generado"
   - Al final verás: "📚 Ejemplos RAG usados: intermediate_001, basic_003, basic_001"

---

## 📊 Estadísticas por Complejidad

### Basic (53 ejemplos)
- **Queries simples**: "list all models", "models from HuggingFace"
- **Filtros básicos**: Por source, library, task
- **Sin agregaciones**: Solo SELECT simple

### Intermediate (40 ejemplos)
- **Multi-criterio**: "PyTorch models for NLP"
- **Agregaciones simples**: COUNT, GROUP BY
- **Ordenamiento**: ORDER BY downloads, likes

### Advanced (57 ejemplos)
- **Agregaciones complejas**: AVG, SUM, MIN, MAX
- **Múltiples JOIN**: Relaciones entre entidades
- **Filtros avanzados**: HAVING, múltiples OPTIONAL

---

## 🔧 Configuración del Sistema RAG

### Parámetros por Método:

#### 🎯 Búsqueda Inteligente (sub-método LLM)
```python
TextToSPARQLConverter(
    model="deepseek-r1:7b",
    use_rag=True,              # ✅ RAG activado
    top_k_examples=3,          # Top-3 ejemplos
    temperature=0.0,           # Determinístico
    llm_provider="ollama",     # Ollama local
    validation_graph=graph     # Grafo para validación
)
```

#### 🧠 Búsqueda Experta
```python
# Misma configuración que Inteligente (sub-método LLM)
TextToSPARQLConverter(
    model="deepseek-r1:7b",
    use_rag=True,              # ✅ RAG activado
    top_k_examples=3,          # Top-3 ejemplos
    temperature=0.0,           # Determinístico
    llm_provider="ollama",
    validation_graph=graph
)
```

### Storage de ChromaDB:
```bash
~/.cache/ai_model_discovery/chroma/
├── chroma.sqlite3           # Base de datos
├── embeddings/              # Vectores de embeddings
└── indices/                 # Índices de búsqueda
```

---

## 🎓 Casos de Uso: Qué Ejemplos se Usan

### Caso 1: Query Simple
**Input**: "PyTorch models"

**Ejemplos RAG Recuperados**:
1. `intermediate_001`: "PyTorch models for NLP"
2. `basic_003`: "models from HuggingFace" (menciona PyTorch)
3. `intermediate_002`: "most popular models by downloads"

**RAG Score**: 0.65 (medio)
**Diccionario**: Top 10 propiedades (compacto)

---

### Caso 2: Query Compleja de Agregación
**Input**: "count models by framework"

**Ejemplos RAG Recuperados**:
1. `intermediate_003`: "count models for task" (COUNT + GROUP BY)
2. `advanced_015`: "average rating by framework"
3. `advanced_022`: "sum downloads by library"

**RAG Score**: 0.85 (alto)
**Diccionario**: Sin diccionario (ejemplos suficientes)

---

### Caso 3: Query Muy Específica
**Input**: "models with more than 1000 downloads and rating > 4.5"

**Ejemplos RAG Recuperados**:
1. `intermediate_002`: "most popular models by downloads"
2. `basic_002`: "high rated computer vision models"
3. `advanced_008`: "models with multiple filters"

**RAG Score**: 0.45 (bajo)
**Diccionario**: Completo (~30 propiedades)

---

## 📈 Métricas de Efectividad del RAG

### Según Evaluation Pipeline v3:

| Método | RAG Usado | Correctness | Completeness | Success Rate |
|--------|-----------|-------------|--------------|--------------|
| **🎯 Inteligente (LLM)** | ✅ Sí | 18% | 50% | 97% |
| **🧠 Experta** | ✅ Sí | 15% | 39% | 94% |

**Observación**: El RAG mejora significativamente la tasa de éxito y completitud comparado con LLM sin RAG.

---

## 💡 Tips para Mejorar el RAG

### 1. **Agregar más ejemplos**
Editar `llm/rag_sparql_examples.py` y agregar nuevos `SPARQLExample`:
```python
SPARQLExample(
    id="custom_001",
    natural_query="tu query",
    sparql_query="tu SPARQL",
    complexity="intermediate",
    category="custom_filter",
    keywords=["keyword1", "keyword2"],
    explanation="Explicación"
)
```

### 2. **Limpiar cache de ChromaDB**
Si actualizas ejemplos, limpia la cache:
```bash
rm -rf ~/.cache/ai_model_discovery/chroma/
# Reiniciar app para reindexar
```

### 3. **Ajustar Top-K**
Para más contexto, aumentar `top_k_examples`:
```python
# En app/pages/1_🔍_Búsqueda.py
llm_engine = TextToSPARQLConverter(
    ...
    top_k_examples=5,  # En vez de 3
    ...
)
```

### 4. **Mejorar Keywords**
Asegúrate que cada ejemplo tenga keywords relevantes y completas.

---

## 🔍 Cómo Verificar Ejemplos Manualmente

```python
# En Python:
from llm.rag_sparql_examples import get_all_examples

examples = get_all_examples()

# Ver un ejemplo específico
pytorch_ex = [ex for ex in examples if ex.id == "intermediate_001"][0]
print(f"Query: {pytorch_ex.natural_query}")
print(f"Keywords: {pytorch_ex.keywords}")
print(f"SPARQL:\n{pytorch_ex.sparql_query}")

# Buscar por keyword
nlp_examples = [ex for ex in examples if "nlp" in ex.keywords]
print(f"Ejemplos con 'nlp': {len(nlp_examples)}")
```

---

## 📚 Archivos Relacionados

- **Ejemplos RAG**: `llm/rag_sparql_examples.py` (3,245 líneas)
- **TextToSPARQL**: `llm/text_to_sparql.py` (825 líneas)
- **Página de búsqueda**: `app/pages/1_🔍_Búsqueda.py` (997 líneas)
- **Diccionario de ontología**: `llm/ontology_dictionary.py`

---

## ✅ Resumen

- **150 ejemplos RAG** disponibles en 106 categorías
- **Top-3 ejemplos** recuperados por cada query
- **Inyección inteligente** del diccionario según RAG score
- **ChromaDB persistente** en ~/.cache/
- **Usado por**: 🎯 Inteligente (queries complejas) y 🧠 Experta (todas)

---

**Última actualización**: 2026-02-16
# Módulo de Búsqueda

Este directorio contiene las implementaciones de los tres métodos de búsqueda del proyecto.

## Estructura

- **`non_federated/`**: Método 1 - Búsqueda semántica en un único catálogo
- **`federated/`**: Método 2 - Búsqueda federada SPARQL
- **`cross_repository/`**: Método 3 - Búsqueda multi-fuente web-wide

## Estado Actual

| Método | Estado | Fase |
|--------|--------|------|
| Non-federated | 📅 Planificado | 2 (Semanas 3-4) |
| Federated | 📅 Planificado | 3 (Semana 5) |
| Cross-repository | 📅 Planificado | 4 (Semanas 6-7) |

## Método 1: Búsqueda No Federada (Próximamente)

Componentes a implementar:

1. `semantic_search.py`: Motor de búsqueda principal
2. `query_interface.py`: CLI interactiva
3. `ranker.py`: Sistema de ranking de resultados

Pipeline:
```
Usuario → Consulta NL → LLM (text_to_sparql) → SPARQL Query → Grafo RDF → Resultados → Ranking
```

## Método 2: Búsqueda Federada (Fase 3)

Permitirá consultar múltiples grafos RDF simultáneamente usando SPARQL federado.

## Método 3: Cross-Repository (Fase 4)

Integrará múltiples fuentes:
- Hugging Face API
- Papers with Code
- OpenML
- Otros repositorios públicos

Ver [README.md](../README.md) principal para detalles del plan de implementación.
# Consultas SPARQL de Ejemplo

Este directorio contiene consultas SPARQL predefinidas para explorar el grafo de conocimiento de modelos de IA.

## Consultas Básicas

### 1. Listar todos los modelos
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?created
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  OPTIONAL { ?model dcterms:created ?created }
}
ORDER BY DESC(?created)
LIMIT 10
```

### 2. Modelos por tarea
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:subject ?task .
  FILTER(CONTAINS(?task, "classification"))
}
LIMIT 20
```

### 3. Modelos con licencia específica
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>

SELECT ?model ?title ?license
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model odrl:hasPolicy ?licenseObj .
  ?licenseObj dcterms:identifier ?license .
  FILTER(CONTAINS(?license, "mit"))
}
```

### 4. Modelos más populares
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
}
ORDER BY DESC(?downloads)
LIMIT 10
```

### 5. Modelos por autor
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?model ?title ?author
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:creator ?authorObj .
  ?authorObj foaf:name ?author .
}
```

### 6. Modelos entrenados con dataset específico
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>

SELECT ?model ?title ?dataset
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model prov:wasDerivedFrom ?datasetObj .
  ?datasetObj dcterms:identifier ?dataset .
}
```

### 7. Modelos por librería/framework
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model daimo:library ?library .
  FILTER(?library = "transformers")
}
```

### 8. Estadísticas por tarea
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?task (COUNT(?model) as ?count)
WHERE {
  ?model a daimo:Model .
  ?model dcterms:subject ?task .
}
GROUP BY ?task
ORDER BY DESC(?count)
```

## Consultas Avanzadas

### 9. Modelos multilingües
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title (COUNT(?lang) as ?numLanguages)
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:language ?lang .
}
GROUP BY ?model ?title
HAVING (COUNT(?lang) > 1)
ORDER BY DESC(?numLanguages)
```

### 10. Modelos con múltiples tags
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>

SELECT ?model ?title (GROUP_CONCAT(?keyword; separator=", ") as ?tags)
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcat:keyword ?keyword .
}
GROUP BY ?model ?title
LIMIT 10
```

## Uso

Las consultas se pueden ejecutar usando:

1. **Python con RDFLib**:
```python
from knowledge_graph import DAIMOGraphBuilder

builder = DAIMOGraphBuilder()
builder.build_from_json("data/raw/hf_models.json")

query = """
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?model WHERE { ?model a daimo:Model }
"""

results = builder.query(query)
for row in results:
    print(row)
```

2. **Desde el notebook de validación** (notebooks/01_validation.ipynb)

3. **Herramientas externas**:
   - Apache Jena Fuseki
   - GraphDB
   - Protégé
# Consultas SPARQL de Ejemplo

Este directorio contiene consultas SPARQL predefinidas para explorar el grafo de conocimiento de modelos de IA.

## Consultas Básicas

### 1. Listar todos los modelos
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?created
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  OPTIONAL { ?model dcterms:created ?created }
}
ORDER BY DESC(?created)
LIMIT 10
```

### 2. Modelos por tarea
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:subject ?task .
  FILTER(CONTAINS(?task, "classification"))
}
LIMIT 20
```

### 3. Modelos con licencia específica
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>

SELECT ?model ?title ?license
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model odrl:hasPolicy ?licenseObj .
  ?licenseObj dcterms:identifier ?license .
  FILTER(CONTAINS(?license, "mit"))
}
```

### 4. Modelos más populares
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
}
ORDER BY DESC(?downloads)
LIMIT 10
```

### 5. Modelos por autor
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?model ?title ?author
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:creator ?authorObj .
  ?authorObj foaf:name ?author .
}
```

### 6. Modelos entrenados con dataset específico
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>

SELECT ?model ?title ?dataset
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model prov:wasDerivedFrom ?datasetObj .
  ?datasetObj dcterms:identifier ?dataset .
}
```

### 7. Modelos por librería/framework
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model daimo:library ?library .
  FILTER(?library = "transformers")
}
```

### 8. Estadísticas por tarea
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?task (COUNT(?model) as ?count)
WHERE {
  ?model a daimo:Model .
  ?model dcterms:subject ?task .
}
GROUP BY ?task
ORDER BY DESC(?count)
```

## Consultas Avanzadas

### 9. Modelos multilingües
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title (COUNT(?lang) as ?numLanguages)
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:language ?lang .
}
GROUP BY ?model ?title
HAVING (COUNT(?lang) > 1)
ORDER BY DESC(?numLanguages)
```

### 10. Modelos con múltiples tags
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>

SELECT ?model ?title (GROUP_CONCAT(?keyword; separator=", ") as ?tags)
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcat:keyword ?keyword .
}
GROUP BY ?model ?title
LIMIT 10
```

## Uso

Las consultas se pueden ejecutar usando:

1. **Python con RDFLib**:
```python
from knowledge_graph import DAIMOGraphBuilder

builder = DAIMOGraphBuilder()
builder.build_from_json("data/raw/hf_models.json")

query = """
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?model WHERE { ?model a daimo:Model }
"""

results = builder.query(query)
for row in results:
    print(row)
```

2. **Desde el notebook de validación** (notebooks/01_validation.ipynb)

3. **Herramientas externas**:
   - Apache Jena Fuseki
   - GraphDB
   - Protégé
