# Nuevos Ejemplos RAG: PyTorch + NLP

## 📋 Resumen

Se agregaron **3 nuevos ejemplos** a la base de conocimiento RAG para mejorar la generación de queries SPARQL relacionados con "PyTorch models for NLP".

**Fecha**: 2024
**Archivo modificado**: `llm/rag_sparql_examples.py`
**Total de ejemplos**: 27 (antes: 24)

---

## 🎯 Objetivo

Mejorar la capacidad del sistema RAG para generar queries SPARQL correctos cuando el usuario pregunta por:
- Modelos PyTorch para NLP
- Modelos de procesamiento de lenguaje natural
- Modelos con transformers o BERT

### Problema Original
Queries anteriores retornaban 0 resultados debido a:
1. **Sintaxis incorrecta**: `;` seguido de `.`
2. **Lógica errónea**: FILTER sobre campos OPTIONAL sin `!BOUND()`

---

## 📊 Ejemplos Agregados

### 1. `intermediate_004` - PyTorch + Task opcional con !BOUND

**Natural Query**: `pytorch models for nlp`

**Características**:
- ✅ Usa `OPTIONAL` para campos que pueden ser NULL
- ✅ Usa `!BOUND(?task)` para manejar valores NULL de forma segura
- ✅ Búsqueda flexible: incluye modelos SIN task definido
- ✅ Detecta múltiples variantes: "nlp", "natural language", "text"

**SPARQL**:
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(
    CONTAINS(LCASE(?library), "pytorch") &&
    (!BOUND(?task) || 
     CONTAINS(LCASE(?task), "nlp") || 
     CONTAINS(LCASE(?task), "natural language") ||
     CONTAINS(LCASE(?task), "text"))
  )
}
LIMIT 15
```

**Resultados**: 11 modelos

**Keywords**: `["pytorch", "nlp", "natural language", "text", "optional", "bound"]`

---

### 2. `intermediate_005` - PyTorch + NLP en título

**Natural Query**: `pytorch models with nlp in title`

**Características**:
- ✅ Búsqueda semántica en el título del modelo
- ✅ Detecta múltiples keywords: "nlp", "language", "text", "sentiment", "translation"
- ✅ No depende del campo `task` (más robusto)
- ✅ Ideal para modelos sin metadata completa

**SPARQL**:
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(
    CONTAINS(LCASE(?library), "pytorch") &&
    (CONTAINS(LCASE(?title), "nlp") || 
     CONTAINS(LCASE(?title), "language") ||
     CONTAINS(LCASE(?title), "text") ||
     CONTAINS(LCASE(?title), "sentiment") ||
     CONTAINS(LCASE(?title), "translation"))
  )
}
LIMIT 15
```

**Resultados**: 11 modelos

**Keywords**: `["pytorch", "nlp", "language", "text", "title", "sentiment", "translation"]`

---

### 3. `intermediate_006` - Transformers (alternativa)

**Natural Query**: `transformer models for natural language`

**Características**:
- ✅ Busca modelos con biblioteca `transformers` (HuggingFace)
- ✅ Incluye modelos PyTorch + BERT (común para NLP)
- ✅ Alternativa cuando el usuario no especifica PyTorch
- ✅ Cobertura más amplia de modelos NLP

**SPARQL**:
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(
    CONTAINS(LCASE(?library), "transformers") ||
    (CONTAINS(LCASE(?library), "pytorch") && CONTAINS(LCASE(?title), "bert"))
  )
}
LIMIT 15
```

**Resultados**: 15 modelos

**Keywords**: `["transformers", "huggingface", "bert", "natural language", "nlp"]`

---

## ✅ Validación

### Prueba contra `ai_models_multi_repo.ttl`

```bash
📊 Cargando grafo ai_models_multi_repo.ttl...
✅ Grafo cargado: 12477 triples

🧪 GENERANDO Y VALIDANDO QUERIES SPARQL
======================================================================

🔍 Opción 1 - Biblioteca + Task opcional con !BOUND
✅ Query válida: 11 resultados
📋 Primeros 3 resultados:
   1. Kaggle NLP Model 1 (lib: PyTorch)
   2. Kaggle NLP Model 11 (lib: PyTorch)
   3. Kaggle NLP Model 16 (lib: PyTorch)

🔍 Opción 2 - Solo biblioteca Pytorch (más inclusivo)
✅ Query válida: 15 resultados

🔍 Opción 3 - Título contiene NLP/language/text + Pytorch
✅ Query válida: 11 resultados

🔍 Opción 4 - Biblioteca Pytorch + Tags opcionales
✅ Query válida: 15 resultados

🔍 Opción 5 - Biblioteca transformers (alternativa)
✅ Query válida: 15 resultados

📊 RESUMEN DE VALIDACIÓN
======================================================================
✅ Queries con resultados: 5/5
🎉 ¡Tenemos 5 queries válidas para agregar al RAG!
```

### Prueba de Retrieval RAG

```bash
🔍 Query de prueba: 'Pytorch models for NLP'
======================================================================

📋 Top 5 ejemplos recuperados por RAG:

1. intermediate_004 - 'pytorch models for nlp'
   Similarity: 0.7557
   Category: library_task_filter
   🆕 NUEVO EJEMPLO!

2. intermediate_001 - 'PyTorch models for NLP'
   Similarity: 0.6952
   Category: multi_filter

3. intermediate_005 - 'pytorch models with nlp in title'
   Similarity: 0.6073
   Category: title_based_filter
   🆕 NUEVO EJEMPLO!

4. intermediate_006 - 'transformer models for natural language'
   Similarity: 0.1878
   Category: library_alternative
   🆕 NUEVO EJEMPLO!

✅ RAG recupera 3/3 nuevos ejemplos en top 5!
```

---

## 🎯 Impacto

### Antes
- ❌ Query "Pytorch models for NLP" retornaba 0 resultados
- ❌ Sintaxis incorrecta: `daimo:library ?library; .`
- ❌ Lógica errónea: FILTER sin `!BOUND()` sobre OPTIONAL

### Después
- ✅ 3 nuevos ejemplos en RAG para este patrón
- ✅ Similarity score alto (0.75) para el ejemplo más relevante
- ✅ Cobertura de múltiples estrategias (task, título, biblioteca alternativa)
- ✅ Queries validados con resultados reales (11-15 modelos cada uno)

---

## 📂 Archivos Modificados

```
llm/rag_sparql_examples.py
├── Total ejemplos: 27 (antes: 24)
├── Nuevos IDs: intermediate_004, intermediate_005, intermediate_006
└── Categories: library_task_filter, title_based_filter, library_alternative
```

---

## 🔄 Reinicialización de ChromaDB

Para que los nuevos ejemplos sean indexados:

```bash
# Eliminar cache persistente
rm -rf ~/.cache/ai_model_discovery/chroma
rm -rf llm/chroma_db

# Reinicializar al ejecutar la aplicación
# ChromaDB detectará 27 ejemplos automáticamente
```

**Salida esperada**:
```
🔧 Inicializando RAG con ChromaDB...
   ✓ 27 ejemplos indexados en ChromaDB
   ✓ LangChain chain configurado
```

---

## 🧠 Patrones Aprendidos

### 1. Uso de `!BOUND()` con OPTIONAL
```sparql
OPTIONAL { ?model daimo:task ?task }
FILTER(!BOUND(?task) || CONTAINS(LCASE(?task), "nlp"))
```
✅ Permite que modelos SIN task definido también sean incluidos

### 2. Búsqueda semántica en títulos
```sparql
FILTER(CONTAINS(LCASE(?title), "nlp") || 
       CONTAINS(LCASE(?title), "language"))
```
✅ Más robusto que depender solo de metadata estructurada

### 3. Bibliotecas alternativas
```sparql
FILTER(CONTAINS(LCASE(?library), "transformers") ||
       (CONTAINS(LCASE(?library), "pytorch") && CONTAINS(LCASE(?title), "bert")))
```
✅ Amplía cobertura incluyendo bibliotecas comunes para el dominio

---

## 📈 Estadísticas

| Métrica | Antes | Después |
|---------|-------|---------|
| Total ejemplos RAG | 24 | **27** |
| Ejemplos intermedios | 3 | **6** |
| Ejemplos PyTorch+NLP | 1 | **4** |
| Top-1 similarity | 0.6952 | **0.7557** (+8.7%) |

---

## ✅ Checklist de Validación

- [x] Queries generados sintácticamente válidos
- [x] Queries retornan resultados (11-15 modelos)
- [x] Ejemplos agregados a `rag_sparql_examples.py`
- [x] ChromaDB reinicializado con 27 ejemplos
- [x] RAG recupera nuevos ejemplos en top-5
- [x] Documentación creada
- [x] Similarity score mejorado

---

## 🔗 Contexto

Este trabajo complementa las **16 correcciones de post-procesamiento** implementadas previamente:
- **Correcciones 0a-0d**: Errores sintácticos (texto después de query, llaves desbalanceadas, etc.)
- **Correcciones 1-12**: Errores semánticos y de formato

Documentos relacionados:
- `docs/NUEVAS_CORRECCIONES_SINTACTICAS.md` - 4 correcciones sintácticas
- `llm/test_post_processing.py` - Tests de las correcciones
- `llm/text_to_sparql.py` - Sistema de post-procesamiento

---

## 🚀 Próximos Pasos

1. **Monitorear producción**: Verificar que queries "Pytorch models for NLP" ahora retornen resultados
2. **Agregar más ejemplos**: Considerar otros patrones comunes (TensorFlow+CV, etc.)
3. **Mejorar embeddings**: Evaluar modelos de embedding más especializados
4. **A/B Testing**: Comparar performance con/sin nuevos ejemplos
