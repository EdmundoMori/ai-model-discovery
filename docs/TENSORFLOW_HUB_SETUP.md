# TensorFlow Hub - Guía de Configuración

## 📋 Información General

**Repositorio**: TensorFlow Hub (https://tfhub.dev)  
**API**: REST API pública  
**Autenticación**: No requerida (API pública)  
**Formato**: JSON  
**Documentación**: https://www.tensorflow.org/hub

## 🔍 Investigación del API

### Endpoints Disponibles

TensorFlow Hub no tiene un API REST oficial documentado, pero expone datos a través de:

1. **tfhub.dev JSON feeds**
   - Lista de modelos: `https://tfhub.dev/s?subtype=module,placeholder`
   - Metadata individual: No hay endpoint directo

2. **tensorflow_hub Python Package**
   - Búsqueda programática de modelos
   - Descarga y uso de modelos
   - Metadata extracción

### Características Únicas

- **Formato TF SavedModel**: Modelos optimizados para TensorFlow
- **Categorías específicas**: Text, Image, Video, Audio
- **Publishers verificados**: Google, DeepMind, etc.
- **Versioning**: Modelos versionados con URLs únicas
- **Colecciones**: Agrupaciones temáticas de modelos

## 🚀 Instalación

### Opción 1: tensorflow-hub Package (Recomendado)

```bash
# Activar entorno virtual
cd /home/edmundo/ai-model-discovery
source .venv/bin/activate

# Instalar tensorflow-hub
pip install tensorflow-hub

# Verificar instalación
python3 -c "import tensorflow_hub as hub; print('✅ TensorFlow Hub instalado')"
```

### Opción 2: Web Scraping (Alternativa)

```bash
# Instalar beautifulsoup4 y requests
pip install beautifulsoup4 requests

# Verificar instalación
python3 -c "from bs4 import BeautifulSoup; import requests; print('✅ Dependencies OK')"
```

## 📊 Método de Recolección

### Estrategia: Web Scraping del Sitio Público

Dado que TensorFlow Hub no tiene un API REST documentado, usaremos scraping del sitio:

```python
import requests
from bs4 import BeautifulSoup
import json

# URL base
BASE_URL = "https://tfhub.dev"

# Obtener listado de modelos
response = requests.get(f"{BASE_URL}/s?subtype=module,placeholder")
soup = BeautifulSoup(response.content, 'html.parser')

# Extraer URLs de modelos
model_links = soup.find_all('a', {'class': 'devsite-result-item-link'})

# Para cada modelo, obtener metadata
for link in model_links:
    model_url = BASE_URL + link['href']
    # Fetch model page and extract metadata
```

### Metadata Disponible

De cada página de modelo se puede extraer:

- **Handle**: URL única del modelo (ej: `tensorflow/efficientnet/b0/feature-vector/1`)
- **Publisher**: Organización/autor (ej: `google`, `tensorflow`)
- **Architecture**: Tipo de modelo (ej: `EfficientNet`, `BERT`)
- **Task/Domain**: Clasificación, detección, embeddings, etc.
- **Framework**: TensorFlow version
- **Dataset**: Dataset de entrenamiento
- **Description**: Descripción textual
- **License**: Tipo de licencia
- **Download Count**: No disponible públicamente
- **Upload Date**: Fecha de publicación

## 🗺️ Mapeo Propuesto

### TensorFlow Hub → StandardizedModel

| Campo TF Hub | StandardizedModel | Notas |
|--------------|-------------------|-------|
| `handle` | `id` | Formato: `publisher/model/version` |
| `handle` | `title` | Nombre legible del handle |
| `publisher` | `author` | Organización/autor |
| `description` | `description` | Descripción del modelo |
| `upload_date` | `created_at` | Fecha de publicación |
| `upload_date` | `last_modified` | Misma fecha (sin updates) |
| N/A | `downloads` | No disponible, usar 0 |
| N/A | `likes` | No disponible, usar 0 |
| `framework` | `library` | Siempre "tensorflow" |
| `architecture` | `architectures` | Lista con arquitectura |
| `task` | `task` | Clasificación, embedding, etc. |
| `license` | `license` | Tipo de licencia |
| `dataset` | N/A | En extra_metadata |
| N/A | `source` | Valor fijo: `"tfhub"` |

### Campos en extra_metadata

| Campo | Descripción |
|-------|-------------|
| `handle` | URL completa del modelo |
| `tfhub_url` | URL web del modelo |
| `publisher` | Organización publicadora |
| `architecture` | Arquitectura del modelo |
| `task_type` | Tipo de tarea (classification, etc.) |
| `dataset` | Dataset de entrenamiento |
| `tf_version` | Versión de TensorFlow requerida |
| `input_shape` | Shape esperado de entrada |
| `output_shape` | Shape de salida |
| `collection` | Colección a la que pertenece |

## 🔗 Mapeo RDF Específico

### Triples Adicionales (map_to_rdf)

```python
# Publisher → dcterms:publisher
if publisher:
    <model_uri> dcterms:publisher <publisher_literal> .

# Architecture → daimo:architecture
if architecture:
    <model_uri> daimo:architecture <architecture_literal> .

# Task Type → daimo:task
if task_type:
    <model_uri> daimo:task <task_literal> .

# Dataset → daimo:trainedOn
if dataset:
    <model_uri> daimo:trainedOn <dataset_literal> .

# TF Version → daimo:framework
if tf_version:
    <model_uri> daimo:framework <tf_version_literal> .
```

## 📊 Estadísticas Esperadas

Basado en tfhub.dev (Enero 2026):

- **Total de modelos**: ~2,500+
- **Publishers**: ~50 (Google, TensorFlow, DeepMind, etc.)
- **Categorías principales**:
  - Text: ~800 modelos
  - Image: ~1,200 modelos
  - Video: ~200 modelos
  - Audio: ~150 modelos
  - Other: ~150 modelos

## 🎯 Decisiones de Diseño

### 1. Web Scraping vs API

**Decisión**: Usar web scraping con rate limiting.

**Justificación**:
- No hay API REST pública documentada
- El sitio es público y accesible
- Implementar caching para minimizar requests
- Rate limiting de 1 request/segundo

### 2. handle como ID

**Decisión**: Usar el "handle" completo como ID.

**Justificación**:
- Es único y versionado
- Formato: `publisher/model/version`
- Ejemplo: `google/bert_uncased_L-12_H-768_A-12/1`

### 3. downloads = 0

**Decisión**: No hay métrica de downloads pública.

**Justificación**:
- TensorFlow Hub no expone contadores de descarga
- Podríamos inferir popularidad por collections
- Por ahora usar 0 para consistencia

### 4. Framework fijo

**Decisión**: Siempre usar "tensorflow" como framework.

**Justificación**:
- Todos los modelos son para TensorFlow
- Puede incluir versión específica en extra_metadata

## 🐛 Limitaciones Conocidas

1. **Sin API oficial**: Dependemos de scraping, puede romperse con cambios en el sitio
2. **Sin métricas de uso**: No hay downloads, likes, o popularidad
3. **Rate limiting manual**: Debemos implementar delays para evitar bloqueos
4. **Metadata incompleto**: Algunos campos pueden no estar disponibles
5. **Sin búsqueda avanzada**: Filtrado limitado en el sitio

## 🔮 Mejoras Futuras

1. **Caching agresivo**: Guardar modelos localmente para reducir scraping
2. **Metadata enriquecido**: Extraer info de collections y tasks
3. **Popularidad inferida**: Usar presencia en collections como proxy
4. **Monitoreo de cambios**: Detectar nuevos modelos periódicamente
5. **TensorFlow Hub Search API**: Si se documenta en el futuro

## 📚 Referencias

- [TensorFlow Hub](https://tfhub.dev)
- [TensorFlow Hub Python API](https://www.tensorflow.org/hub/api_docs/python/hub)
- [TensorFlow Hub GitHub](https://github.com/tensorflow/hub)
- [Common Saved Model APIs](https://www.tensorflow.org/hub/common_saved_model_apis)

---

**Autor**: GitHub Copilot  
**Última actualización**: Enero 2026
