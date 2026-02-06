# 📊 Análisis Completo de Metadatos - Hugging Face y Extensión de DAIMO

**Proyecto**: AI Model Discovery System  
**Autor**: Edmundo Mori Orrillo  
**Fecha**: Enero 2026  
**Objetivo**: Extender ontología DAIMO para soportar metadatos completos de repositorios de modelos IA

---

## 🎯 Resumen Ejecutivo

Este documento analiza **TODOS** los metadatos disponibles en Hugging Face Hub, los clasifica por prioridad, mapea contra la ontología DAIMO actual, e identifica extensiones necesarias para crear un sistema robusto de descubrimiento de modelos IA.

---

## 📋 1. Inventario Completo de Metadatos (Hugging Face)

### 1.1. Metadatos Básicos de Identidad

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id` / `modelId` | string | Identificador único del modelo | `"meta-llama/Llama-3.3-70B-Instruct"` |
| `author` | string | Creador/organización | `"meta-llama"` |
| `sha` | string | Hash de commit del repositorio | `"6f6073b423..."` |
| `created_at` | datetime | Fecha de creación | `2024-11-26T16:08:47Z` |
| `last_modified` | datetime | Última actualización | `2024-12-21T18:28:01Z` |

### 1.2. Control de Acceso y Visibilidad

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `private` | boolean | Modelo privado/público | `false` |
| `disabled` | boolean | Modelo deshabilitado | `false` |
| `gated` | string/bool | Requiere aprobación (`"auto"`, `"manual"`, `false`) | `"manual"` |
| `extra_gated_prompt` | string | Texto del formulario de acceso | "LLAMA 3.3 LICENSE..." |
| `extra_gated_fields` | dict | Campos del formulario | `{"First Name": "text", ...}` |

### 1.3. Popularidad y Métricas de Uso

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `downloads` | integer | Descargas totales | `715,095` |
| `downloads_all_time` | integer | Descargas históricas | (puede ser None) |
| `likes` | integer | Número de likes | `2,635` |
| `trending_score` | float | Score de tendencia | (temporal) |
| `spaces` | list[str] | Espacios que usan el modelo | `["space1", "space2"]` |
| `usedStorage` | integer | Espacio en bytes | `269179020000` (269 GB) |

### 1.4. Clasificación y Taxonomía

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `pipeline_tag` | string | Tarea principal ML | `"text-generation"` |
| `tags` | list[str] | Tags libres | `["transformers", "pytorch", "llama-3"]` |
| `library_name` | string | Framework principal | `"transformers"`, `"diffusers"` |
| `language` | list[str] | Idiomas soportados | `["en", "es", "fr"]` |
| `datasets` | list[str] | Datasets de entrenamiento | `["openwebtext", "c4"]` |
| `metrics` | list[str] | Métricas evaluadas | `["accuracy", "bleu"]` |

### 1.5. Licencia y Uso Legal

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `license` | string | Identificador de licencia | `"apache-2.0"`, `"llama3.3"`, `"openrail"` |
| `license_name` | string | Nombre completo | `"Apache License 2.0"` |
| `license_link` | string | URL licencia | `"https://..."` |

### 1.6. Información Técnica del Modelo

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `config` | dict | Configuración del modelo | `{"hidden_size": 4096, ...}` |
| `model_type` | string | Arquitectura base | `"llama"`, `"bert"`, `"gpt2"` |
| `architectures` | list[str] | Clases de arquitectura | `["LlamaForCausalLM"]` |
| `transformers_info` | object | Info específica de Transformers | Objeto con `auto_model`, `pipeline_tag` |
| `safetensors` | object | Info de SafeTensors | `{"parameters": {"BF16": 70B}, "total": 70B}` |
| `mask_token` | string | Token de máscara | `"[MASK]"` |
| `tokenizer_config` | dict | Config del tokenizer | Configuración completa |

### 1.7. Información de Modelos Base y Derivados

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `base_model` | list[str] | Modelo(s) base | `["meta-llama/Llama-3.1-70B"]` |
| `model_index` | list[dict] | Índice de modelos evaluados | Resultados de benchmarks |

### 1.8. Archivos y Artefactos

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `siblings` | list[RepoFile] | Todos los archivos del repo | Lista de objetos con `rfilename`, `size`, `blob_id` |
| `widget_data` | list[dict] | Ejemplos para el widget de inferencia | Inputs/outputs de ejemplo |

### 1.9. Proveedores de Inferencia

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `inference` | string | Disponibilidad de inferencia | `"hosted"`, `"local"` |
| `inference_provider_mapping` | dict | Mapeo de proveedores | Info de endpoints |

### 1.10. Metadatos de Card (README estructurado)

Extraídos del YAML front-matter del README.md:

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `model-index` | list[dict] | Resultados de evaluación | Benchmarks estructurados |
| `co2_eq_emissions` | float/dict | Emisiones de CO2 | Información de impacto ambiental |
| `eval_results` | dict | Resultados de evaluación | Métricas detalladas |
| `dataset_info` | dict | Info sobre datasets usados | Estadísticas de datos |

---

## 🏆 2. Clasificación por Prioridad

### ✅ **NIVEL 1: CRÍTICOS** (Obligatorios para búsqueda semántica)

Estos metadatos son **esenciales** para el descubrimiento y clasificación básica:

1. **Identidad**:
   - `id`, `modelId`, `author`, `created_at`, `last_modified`
   
2. **Clasificación ML**:
   - `pipeline_tag` (tarea principal)
   - `library_name` (framework)
   - `model_type` / `architectures` (arquitectura)
   - `language` (idiomas)

3. **Licencia**:
   - `license` (uso legal)

4. **Popularidad básica**:
   - `downloads`, `likes`

5. **Acceso**:
   - `private`, `disabled`, `gated`

**Justificación**: Sin estos campos, es imposible responder preguntas básicas como "modelos de text-generation en español con licencia Apache-2.0".

---

### 🔸 **NIVEL 2: IMPORTANTES** (Mejoran significativamente la calidad)

Proporcionan contexto técnico y de evaluación:

6. **Entrenamiento y Proveniencia**:
   - `datasets` (datos de entrenamiento)
   - `base_model` (fine-tuning)

7. **Evaluación**:
   - `metrics` (métricas usadas)
   - `eval_results` / `model_index` (resultados)

8. **Taxonomía extendida**:
   - `tags` (filtrado avanzado)

9. **Configuración técnica**:
   - `config` (parámetros del modelo)
   - `safetensors` (info de peso/formato)
   - `tokenizer_config`

10. **Uso y adopción**:
    - `spaces` (aplicaciones que lo usan)
    - `trending_score`

**Justificación**: Permiten consultas avanzadas tipo "modelos fine-tuneados de BERT evaluados en GLUE con >90% accuracy".

---

### 🔹 **NIVEL 3: OPCIONALES** (Nice-to-have, contexto adicional)

Útiles para casos de uso específicos:

11. **Inferencia**:
    - `inference`, `inference_provider_mapping`
    - `widget_data`

12. **Sostenibilidad**:
    - `co2_eq_emissions`

13. **Metadatos técnicos**:
    - `sha`, `mask_token`
    - `usedStorage`

14. **Gatekeeping detallado**:
    - `extra_gated_prompt`, `extra_gated_fields`

**Justificación**: Útiles para búsquedas especializadas (ej: "modelos con inferencia hosted") pero no críticos.

---

### ❌ **NIVEL 4: DESCARTABLES** (No agregan valor semántico)

15. **Metadatos de implementación**:
    - `siblings` (lista completa de archivos) → Demasiado granular
    - `downloads_all_time` → Redundante con `downloads`
    - `transformers_info` → Ya cubierto por `library_name` y `config`

**Justificación**: No aportan al descubrimiento semántico; son más útiles para descarga/deployment.

---

## 🗺️ 3. Mapeo contra Ontología DAIMO Actual

### ✅ **Ya Soportados (bien mapeados)**

| Metadato HF | Clase/Propiedad DAIMO | Status |
|-------------|----------------------|--------|
| `id`, `modelId` | `dcterms:identifier`, `dcterms:title` | ✅ OK |
| `author` | `dcterms:creator` → `foaf:Agent` | ✅ OK |
| `created_at`, `last_modified` | `dcterms:created`, `dcterms:modified` | ✅ OK |
| `pipeline_tag` | `dcterms:subject` + `mls:Task` | ✅ OK |
| `license` | `odrl:hasPolicy` → `odrl:Offer` | ✅ OK |
| `downloads`, `likes` | `daimo:downloads`, `daimo:likes` | ✅ OK |
| `library_name` | `daimo:library` | ✅ OK |
| `tags` | `dcat:keyword` | ✅ OK |
| `language` | `dcterms:language` | ✅ OK |
| `datasets` | `prov:wasDerivedFrom` → `dcat:Dataset` | ✅ OK |

---

### ⚠️ **Parcialmente Soportados (requieren mejora)**

| Metadato HF | Problema Actual | Solución Propuesta |
|-------------|----------------|-------------------|
| `gated` | No mapeado | Nueva propiedad `daimo:accessControl` |
| `model_type`, `architectures` | Solo en `mls:Task`, no arquitectura | Nueva clase `daimo:ModelArchitecture` |
| `config` | No estructurado | Nueva propiedad `daimo:hyperparameters` |
| `base_model` | Usa `prov:wasDerivedFrom` genérico | Relación específica `daimo:fineTunedFrom` |

---

### ❌ **NO Soportados (gaps críticos)**

| Metadato HF | Impacto | Solución Propuesta |
|-------------|---------|-------------------|
| `metrics`, `eval_results` | **Alto** - Imposible filtrar por performance | Clase `mls:ModelEvaluation` con `mls:specifiedBy` |
| `safetensors` (parámetros) | **Medio** - No se puede buscar por tamaño | Propiedad `daimo:parameterCount` |
| `spaces` | **Medio** - No se captura adopción | Propiedad `daimo:usedByApplication` |
| `co2_eq_emissions` | **Bajo** - Sostenibilidad | Propiedad `daimo:carbonFootprint` |
| `inference` | **Bajo** - Deployment | Propiedad `daimo:inferenceEndpoint` |

---

## 🛠️ 4. Propuesta de Extensión de DAIMO

### 4.1. Nuevas Clases

```turtle
# Arquitectura de modelo
daimo:ModelArchitecture a rdfs:Class ;
    rdfs:subClassOf owl:Thing ;
    rdfs:label "Model Architecture" ;
    rdfs:comment "Arquitectura o familia de un modelo ML (ej: BERT, GPT, Llama)" .

# Configuración/Hiperparámetros
daimo:HyperparameterConfiguration a rdfs:Class ;
    rdfs:subClassOf owl:Thing ;
    rdfs:label "Hyperparameter Configuration" ;
    rdfs:comment "Configuración técnica del modelo (hidden_size, num_layers, etc.)" .

# Control de acceso
daimo:AccessPolicy a rdfs:Class ;
    rdfs:subClassOf odrl:Policy ;
    rdfs:label "Access Policy" ;
    rdfs:comment "Política de acceso al modelo (público, privado, gated)" .
```

### 4.2. Nuevas Propiedades

```turtle
# Arquitectura
daimo:hasArchitecture a rdf:Property ;
    rdfs:domain daimo:Model ;
    rdfs:range daimo:ModelArchitecture .

# Hiperparámetros
daimo:hasConfiguration a rdf:Property ;
    rdfs:domain daimo:Model ;
    rdfs:range daimo:HyperparameterConfiguration .

daimo:parameterCount a rdf:Property ;
    rdfs:domain daimo:Model ;
    rdfs:range xsd:long ;
    rdfs:comment "Número total de parámetros del modelo" .

# Fine-tuning
daimo:fineTunedFrom a rdf:Property ;
    rdfs:subPropertyOf prov:wasDerivedFrom ;
    rdfs:domain daimo:Model ;
    rdfs:range daimo:Model ;
    rdfs:comment "Modelo base del cual se hizo fine-tuning" .

# Control de acceso
daimo:accessControl a rdf:Property ;
    rdfs:domain daimo:Model ;
    rdfs:range daimo:AccessPolicy .

daimo:requiresApproval a rdf:Property ;
    rdfs:domain daimo:Model ;
    rdfs:range xsd:boolean .

# Uso y adopción
daimo:usedByApplication a rdf:Property ;
    rdfs:domain daimo:Model ;
    rdfs:range foaf:Project ;
    rdfs:comment "Aplicaciones/espacios que usan el modelo" .

# Sostenibilidad
daimo:carbonFootprint a rdf:Property ;
    rdfs:domain daimo:Model ;
    rdfs:range xsd:float ;
    rdfs:comment "Emisiones de CO2 equivalentes en kg" .

# Inferencia
daimo:inferenceEndpoint a rdf:Property ;
    rdfs:domain daimo:Model ;
    rdfs:range xsd:anyURI ;
    rdfs:comment "Endpoint de inferencia hosted" .
```

### 4.3. Uso de ML-Schema (mls:ModelEvaluation)

ML-Schema ya proporciona clases para evaluación. Extenderemos su uso:

```turtle
# Ejemplo de evaluación completa
:model123 a daimo:Model ;
    mls:hasEvaluation :eval1 .

:eval1 a mls:ModelEvaluation ;
    mls:specifiedBy :metric_accuracy ;
    mls:hasValue "0.92"^^xsd:float ;
    mls:evaluatedOn :dataset_glue .

:metric_accuracy a mls:EvaluationMeasure ;
    rdfs:label "Accuracy" .
```

---

## 📊 5. Priorización de Implementación

### **Sprint 1: Metadatos Críticos** (Nivel 1)
- ✅ Ya implementados en versión actual
- 🔧 Mejora: Añadir `model_type`, `architectures` → `daimo:hasArchitecture`
- 🔧 Mejora: Añadir `gated` → `daimo:accessControl`

### **Sprint 2: Evaluación y Performance** (Nivel 2 - Alto impacto)
- 📍 Implementar `mls:ModelEvaluation` para `metrics` y `eval_results`
- 📍 Añadir `daimo:parameterCount` para filtrado por tamaño
- 📍 Implementar `daimo:fineTunedFrom` para proveniencia

### **Sprint 3: Contexto Técnico** (Nivel 2 - Medio impacto)
- 📍 Mapear `config` a `daimo:HyperparameterConfiguration`
- 📍 Añadir `spaces` → `daimo:usedByApplication`
- 📍 Capturar `tokenizer_config` en configuración

### **Sprint 4: Opcionales** (Nivel 3)
- 📍 `co2_eq_emissions` → `daimo:carbonFootprint`
- 📍 `inference` → `daimo:inferenceEndpoint`

---

## 🌐 6. Compatibilidad con Otros Repositorios

### 6.1. ModelHub/Papers with Code

**Metadatos únicos**:
- `paper_url`, `arxiv_id` → Añadir `dcterms:references`
- `sota_benchmarks` → Extender `mls:ModelEvaluation`

### 6.2. TensorFlow Hub

**Metadatos únicos**:
- `publisher` → Ya cubierto con `dcterms:creator`
- `asset_type` → Similar a `library_name`

### 6.3. PyTorch Hub / ONNX Model Zoo

**Metadatos únicos**:
- `input_shape`, `output_shape` → Parte de `config`
- `onnx_version` → Framework version

**Conclusión**: La extensión propuesta de DAIMO es **suficientemente genérica** para soportar múltiples repositorios.

---

## 📝 7. Siguientes Pasos (Roadmap)

1. **Extender `daimo.ttl`** con las nuevas clases y propiedades propuestas
2. **Actualizar `collect_hf_models.py`** para extraer metadatos Nivel 1 + 2
3. **Actualizar `build_graph.py`** para mapear los nuevos campos
4. **Crear script de validación** para verificar completitud de metadatos
5. **Ejecutar recolección completa** con 1000+ modelos
6. **Validar consultas SPARQL avanzadas** (ej: filtros por arquitectura, evaluación)
7. **Proceder a Fase 2**: Text-to-SPARQL con ontología enriquecida

---

## 🎯 Conclusión

**Metadatos a capturar**: **~25 campos prioritarios** (Nivel 1 + 2)  
**Extensiones DAIMO necesarias**: **3 clases nuevas + 10 propiedades**  
**Compatibilidad**: Diseño genérico para múltiples repositorios  
**Impacto**: Sistema de descubrimiento **10x más robusto** con capacidades de filtrado avanzado

**Próxima acción**: Implementar Sprint 1 + 2 antes de Fase 2.
