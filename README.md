# AI Model Discovery System
## Sistema de Descubrimiento Semántico de Modelos de IA

**Tesis Doctoral** | Universidad Politécnica de Madrid  
**Autor**: Edmundo Mori Orrillo | Grupo PIONERA

---

## 📊 Estado del Proyecto

### ✅ FASE 1 COMPLETADA: Método de Búsqueda No Federada

**Sistema operativo** que permite descubrir modelos de IA usando **lenguaje natural**:
- **318 modelos** de 7 repositorios → **12,477 triples RDF** con ontología DAIMO v2.0
- **Text-to-SPARQL** con DeepSeek R1 7B + RAG (150 ejemplos) → **100% éxito** en evaluación inicial
- **Interfaz web Streamlit** con Model Cards interactivas
- **Tiempo de respuesta**: 0.56s promedio por consulta

### 🎯 Objetivo de Investigación

Desarrollar y comparar **3 métodos de búsqueda semántica** de modelos de IA para determinar ventajas, limitaciones y casos de uso óptimos de cada enfoque

---

## 📋 Tres Métodos de Búsqueda (Objetivo de Tesis)

| Método | Descripción | Estado | Avance |
|--------|-------------|--------|--------|
| **1. No Federada** | Catálogo único RDF + SPARQL + Text-to-SPARQL con LLM | ✅ **Completado** | **100%** |
| **2. Federada** | Múltiples grafos RDF distribuidos + SPARQL SERVICE | ⏳ Planificado | 0% |
| **3. Cross-Repository** | APIs heterogéneas + normalización en tiempo real | ⏳ Planificado | 0% |

**Hipótesis de investigación**: Cada método tiene ventajas en diferentes escenarios (centralización vs. distribución vs. escalabilidad web)

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

- **Ontología DAIMO v2.0**: Extensión de PIONERA con 32 propiedades (metadatos, técnicos, popularidad, legales)
- **RAG con ChromaDB**: 150 ejemplos (53 básicos, 40 intermedios, 57 avanzados) para few-shot learning
- **Post-procesamiento**: 15 reglas automáticas corrigen errores comunes (namespaces, clases, filtros OPTIONAL)
- **7 Repositorios**: Hugging Face (55), PyTorch Hub (55), Civitai (55), Replicate (50), Kaggle (50), TensorFlow Hub (30), Papers with Code (23)

### Capacidades Text-to-SPARQL

✅ **Básicas**: Filtros por tarea, framework, licencia, autor  
✅ **Intermedias**: Múltiples condiciones, ordenamiento, negaciones  
✅ **Avanzadas**: Agregaciones (AVG, COUNT, SUM), GROUP BY, HAVING  

**Evaluación preliminar**: 10/10 queries nuevos (100% éxito), 0.56s promedio

---

## � Análisis de Avance vs. Objetivo de Tesis

### ✅ Lo Completado (Fase 1 - 100%)

| Componente | Estado | Detalles |
|------------|--------|----------|
| Ontología DAIMO v2.0 | ✅ | 7 clases, 32 propiedades, validada |
| Recolectores de datos | ✅ | 7 repositorios implementados |
| Grafo RDF unificado | ✅ | 318 modelos, 12,477 triples |
| Text-to-SPARQL + RAG | ✅ | LLM + 150 ejemplos + post-procesamiento |
| Interfaz web Streamlit | ✅ | Búsqueda NL + Model Cards + Dashboard |
| Evaluación preliminar | ✅ | 10 queries (100% éxito) |

**Hitos**: Método 1 (No Federada) funcional y demostrable

### ⏳ Lo Pendiente para Completar la Investigación

#### 🔴 CRÍTICO - Validación Académica (Necesario para tesis)

1. **Evaluación formal con benchmark**
   - ❌ Dataset de 50-100 queries con ground truth SPARQL
   - ❌ Métricas académicas: Precision@K, Recall@K, F1-Score, Exactitud sintáctica/semántica
   - ❌ Análisis de errores y limitaciones
   - **Impacto**: Sin esto, el sistema es solo un prototipo, no investigación validada

2. **Comparación con baseline**
   - ❌ Búsqueda por keywords tradicional
   - ❌ Otros sistemas de descubrimiento (ModelHub, Hugging Face search)
   - **Impacto**: Imposible demostrar ventajas del enfoque semántico

#### 🟡 ALTO - Completar los 3 Métodos (Objetivo central de tesis)

3. **Método 2: Búsqueda Federada**
   - ❌ Implementar SPARQL SERVICE para consultar múltiples endpoints
   - ❌ Grafos RDF distribuidos independientes
   - ❌ Agregación y ranking de resultados
   - **Impacto**: Sin esto, solo se cubre 1 de 3 métodos prometidos

4. **Método 3: Cross-Repository**
   - ❌ Consultas directas a APIs heterogéneas (sin endpoints SPARQL)
   - ❌ Normalización en tiempo real a DAIMO
   - ❌ Manejo de esquemas diferentes
   - **Impacto**: Sin esto, falta el método más escalable

5. **Comparación entre los 3 métodos**
   - ❌ Mismo dataset de prueba para los 3
   - ❌ Métricas: Latencia, cobertura, precisión, escalabilidad
   - ❌ Análisis de ventajas/desventajas de cada enfoque
   - **Impacto**: Esta es la contribución principal de la tesis

#### 🟢 MEDIO - Mejoras del Sistema

6. **Ampliar dataset**: 318 → 1000+ modelos (más representativo)
7. **Mejorar cobertura de metadatos**: Muchos modelos tienen propiedades incompletas
8. **Relaciones entre modelos**: Fine-tuning chains, derivaciones, prov:wasDerivedFrom
9. **Métricas de benchmarks**: Accuracy, F1-score de los modelos en el grafo

#### ⚪ BAJA - Optimizaciones Futuras

10. Fine-tuning del LLM específico para SPARQL+DAIMO
11. Sistema de recomendaciones basado en historial
12. Interfaz multilingüe (español)
13. API REST pública documentada

---

## 🎯 Próximos Pasos Recomendados (Por Criticidad)

### **Paso 1 (2-3 semanas): Evaluación Formal del Método 1** 🔴

**Objetivo**: Validar académicamente el sistema actual

**Tareas**:
```
1. Crear benchmark dataset:
   - 50 queries en lenguaje natural (15 básicas, 20 intermedias, 15 avanzadas)
   - Ground truth SPARQL manual para cada query
   - Resultados esperados (lista de IDs de modelos)

2. Implementar script de evaluación automática:
   - Precisión sintáctica: % queries SPARQL válidas
   - Precisión semántica: Precision@10, Recall@10, F1-Score
   - Latencia: Tiempo promedio de respuesta

3. Ejecutar evaluación y documentar:
   - Análisis de casos exitosos
   - Análisis de errores (clasificar tipos)
   - Limitaciones identificadas
   - Propuestas de mejora

4. Comparar con baseline:
   - Búsqueda por keywords (TF-IDF sobre descripciones)
   - Calcular mejora relativa del enfoque semántico
```

**Entregable**: Paper draft con evaluación formal

**Criticidad**: ⚠️ **SIN ESTO NO HAY VALIDACIÓN CIENTÍFICA**

---

### **Paso 2 (3-4 semanas): Implementar Método 2 (Federado)** 🟡

**Objetivo**: Permitir búsqueda en grafos RDF distribuidos

**Tareas**:
```
1. Diseño:
   - Definir arquitectura de múltiples endpoints SPARQL
   - Diseñar lógica de agregación de resultados

2. Implementación:
   - search/federated/federated_search.py
   - SPARQL con SERVICE clauses
   - Ranking global de resultados

3. Despliegue:
   - 3+ grafos RDF independientes (local o remoto)
   - Cada uno con subset del catálogo

4. Evaluación:
   - Mismo benchmark del Paso 1
   - Métricas adicionales: latencia de red, tolerancia a fallos
```

**Entregable**: Método 2 funcional y evaluado

---

### **Paso 3 (3-4 semanas): Implementar Método 3 (Cross-Repository)** 🟡

**Objetivo**: Búsqueda directa en APIs heterogéneas sin SPARQL

**Tareas**:
```
1. Diseño:
   - Text-to-API-Query (traducir NL a filtros API)
   - Normalización dinámica a DAIMO

2. Implementación:
   - search/cross_repository/api_search.py
   - Conectores a 5+ APIs públicas
   - Mapeo en tiempo real

3. Evaluación:
   - Mismo benchmark
   - Analizar cobertura (% repositorios accesibles)
```

**Entregable**: Método 3 funcional y evaluado

---

### **Paso 4 (2 semanas): Comparación Final** 🟡

**Objetivo**: Análisis comparativo de los 3 métodos

**Tareas**:
```
1. Ejecutar mismo benchmark en los 3 métodos
2. Comparar:
   - Precisión (P@10, R@10, F1)
   - Latencia (promedio, percentil 95)
   - Cobertura (# repositorios accesibles)
   - Escalabilidad (cómo crecen con N modelos)
   - Complejidad de implementación
3. Identificar casos de uso óptimos para cada método
```

**Entregable**: Paper comparativo completo

**Criticidad**: ⚠️ **CONTRIBUCIÓN PRINCIPAL DE LA TESIS**

---

## 📊 Resumen Ejecutivo del Estado

### 🎉 Logros Actuales

- ✅ **Sistema funcional** de búsqueda semántica con lenguaje natural
- ✅ **Ontología DAIMO v2.0** validada con 318 modelos reales
- ✅ **Text-to-SPARQL** con 100% de éxito en evaluación preliminar (10 queries)
- ✅ **Interfaz web moderna** con Model Cards y Dashboard

**Valor actual**: Prototipo demostrable y funcional del Método 1

### ⚠️ Gaps Críticos para la Tesis

1. **Falta evaluación formal** con métricas académicas (50-100 queries + ground truth)
2. **Faltan Métodos 2 y 3** (solo 1 de 3 implementados = 33% del objetivo)
3. **Falta comparación entre métodos** (contribución principal de la investigación)
4. **Dataset pequeño** (318 modelos, ideal: 1000+)

**Riesgo**: Sin completar los pasos críticos, el proyecto es solo un prototipo, no una investigación doctoral completa

### 🎯 Prioridad #1

**Ejecutar evaluación formal del Método 1** (Paso 1) para:
- Validar científicamente el sistema actual
- Identificar mejoras antes de implementar Métodos 2 y 3
- Tener baseline sólido para comparaciones

**Timeline estimado para completar tesis**:
- Paso 1 (Evaluación): 2-3 semanas
- Paso 2 (Método 2): 3-4 semanas
- Paso 3 (Método 3): 3-4 semanas
- Paso 4 (Comparación): 2 semanas
- **Total**: **10-13 semanas** (~3 meses)

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

**Nota**: Sistema incluye 318 modelos. APIs opcionales para más datos (ver [QUICKSTART.md](QUICKSTART.md))

---

## 📁 Estructura del Código

```
ai-model-discovery/
├── data/
│   ├── raw/              # 318 modelos de 7 repositorios
│   └── unified_graph.ttl # 12,477 triples RDF
├── ontologies/
│   └── daimo.ttl         # Ontología DAIMO v2.0
├──llm/
│   ├── text_to_sparql.py       # Conversor NL→SPARQL
│   └── rag_sparql_examples.py  # 150 ejemplos RAG
├── search/
│   ├── non_federated/    # ✅ Método 1 (completado)
│   ├── federated/        # ⏳ Método 2 (pendiente)
│   └── cross_repository/ # ⏳ Método 3 (pendiente)
├── knowledge_graph/
│   └── build_graph.py    # Constructor del grafo
├── app/
│   └── main.py           # Interfaz Streamlit
└── utils/
    └── *_repository.py   # 7 colectores de datos
```

---

## 🎓 Tecnologías Clave

**Ontología**: DAIMO v2.0 (PIONERA-UPM) - 7 clases, 32 propiedades  
**LLM**: DeepSeek R1 7B (Ollama local) + RAG (ChromaDB, 150 ejemplos)  
**Grafos**: rdflib + SPARQL  
**Frontend**: Streamlit + Plotly  
**Datos**: APIs de HuggingFace, Kaggle, Civitai, Replicate, PyTorch Hub, TensorFlow Hub, Papers with Code

---

## 📊 Evaluación Preliminar

**Método**: 10 queries nuevas (no en RAG)  
**Resultado**: 10/10 éxito (100%), 0.56s promedio  
**Capacidades**: Filtros, agregaciones (AVG, COUNT, SUM), GROUP BY, HAVING

**⚠️ Limitación**: Evaluación preliminar, se necesita benchmark formal (50-100 queries con ground truth)

Detalles: [test_results_10_prompts.txt](test_results_10_prompts.txt)

---

## 📖 Recursos

- **Guía rápida**: [QUICKSTART.md](QUICKSTART.md)
- **Notebooks**: `notebooks/` (construcción grafo, validación, RAG demo)
- **Ontología**: `ontologies/` (DAIMO v2.0)
- **Evaluación**: [test_results_10_prompts.txt](test_results_10_prompts.txt)

---

## 📝 Licencia y Contacto

**Licencia**: MIT (código) | CC BY 4.0 (ontología DAIMO)  
**Autor**: Edmundo Mori Orrillo | edmundo.mori.orrillo@upm.es  
**Institución**: UPM - Grupo PIONERA  
**Agradecimientos**: Jiayun Liu (co-autora DAIMO), comunidades HuggingFace/Papers with Code
