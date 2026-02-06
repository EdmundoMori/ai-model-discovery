# Replicate - Mapeo de Metadatos

## 📋 Información General

**Fecha de implementación**: Enero 2025  
**Repositorio**: Replicate (https://replicate.com)  
**Tipo API**: REST API v1  
**Autenticación**: Bearer Token  
**Paginación**: Cursor-based

## 🔍 Investigación del API

### Endpoints Utilizados

1. **GET /v1/models**
   - Listado de modelos públicos
   - Soporta paginación con cursor
   - Soporta ordenamiento y filtrado
   - Límite de rate: 3000 requests/min

2. **Estructura de Respuesta**

```json
{
  "results": [
    {
      "url": "https://replicate.com/owner/name",
      "owner": "stability-ai",
      "name": "sdxl",
      "description": "A text-to-image generative AI model",
      "visibility": "public",
      "github_url": "https://github.com/...",
      "paper_url": null,
      "license_url": "https://...",
      "run_count": 1500000,
      "cover_image_url": "https://replicate.delivery/...",
      "default_example": {...},
      "latest_version": {
        "id": "39ed52f2a...",
        "created_at": "2024-02-15T10:30:00.000Z",
        "cog_version": "0.9.0"
      }
    }
  ],
  "next": "cursor_token_here"
}
```

### Características Únicas de Replicate

- **Cog Framework**: Todos los modelos usan Cog para containerización
- **run_count**: Métrica de uso real (no solo likes)
- **version_id**: Control de versiones explícito
- **cover_image_url**: 100% de modelos tienen imagen
- **Inference API**: URL directa para ejecutar predicciones

## 🗺️ Mapeo de Campos

### API → StandardizedModel

| Campo API | StandardizedModel | Notas |
|-----------|-------------------|-------|
| `owner` | `author` | Cuenta del usuario/organización |
| `name` | Parte de `id` | ID final: `owner/name` |
| `owner/name` | `id` | Formato: `stability-ai/sdxl` |
| `owner/name` | `title` | Mismo que ID (sin título separado) |
| `description` | `description` | Puede ser null |
| `latest_version.created_at` | `created_at` | Fecha de última versión |
| `latest_version.created_at` | `last_modified` | Misma fecha (no hay update_at) |
| `run_count` | `downloads` | **Métrica de uso real** |
| `N/A` | `likes` | No existe, se asigna 0 |
| `latest_version.cog_version` | `library` | Framework de Replicate |
| `latest_version.cog_version` | `framework` | Duplicado para compatibilidad |
| `visibility` | `private` | Mapeo: public→false, private→true |
| `url` | `inference_endpoint` | URL para ejecutar el modelo |
| `N/A` | `source` | Valor fijo: `"replicate"` |

### Campos en extra_metadata

| Campo | Descripción |
|-------|-------------|
| `url` | URL del modelo en Replicate |
| `github_url` | Repositorio de código fuente |
| `license_url` | URL de la licencia |
| `cover_image_url` | Imagen de portada del modelo |
| `visibility` | `"public"` o `"private"` |
| `version_id` | SHA del contenedor Docker |
| `cog_version` | Versión del framework Cog |
| `default_example` | Ejemplo de predicción |
| `run_count` | Número de ejecuciones (duplicado) |

### Tags Inferidos

Se infieren tags desde la descripción buscando keywords:
- `video`, `image`, `text`, `audio`, `multimodal`
- `generation`, `classification`, `detection`
- `diffusion`, `transformer`, `gan`

## 🔗 Mapeo RDF Específico

### Triples Adicionales (map_to_rdf)

```python
# GitHub URL → sd:SourceCode
if github_url:
    <source_code_uri> rdf:type sd:SourceCode .
    <source_code_uri> rdfs:label "Source Code" .
    <model_uri> sd:SourceCode <source_code_uri> .

# Cover image → foaf:depiction
if cover_image_url:
    <model_uri> foaf:depiction <cover_image_url> .

# Version ID → daimo:versionId
if version_id:
    <model_uri> daimo:versionId "39ed52f2a..." .

# Cog version → daimo:cogVersion
if cog_version:
    <model_uri> daimo:cogVersion "0.9.0" .

# License URL → dcterms:license
if license_url:
    <model_uri> dcterms:license <license_url> .

# Inference endpoint → daimo:inferenceEndpoint
if url:
    <model_uri> daimo:inferenceEndpoint <url> .
```

## 📊 Estadísticas de Disponibilidad

Basado en muestra de 10 modelos:

| Metadato | Disponibilidad |
|----------|----------------|
| Cover Image | 100% (10/10) |
| Version ID | 100% (10/10) |
| Cog Version | 100% (10/10) |
| Inference Endpoint | 100% (10/10) |
| Description | ~80% (8/10) |
| License URL | 20% (2/10) |
| GitHub URL | 10% (1/10) |
| Paper URL | 0% (0/10) |

## 🎯 Decisiones de Diseño

### 1. run_count como downloads

**Decisión**: Mapear `run_count` a `downloads` en lugar de crear un campo nuevo.

**Justificación**:
- `run_count` representa **uso real** del modelo
- Es más valioso que likes (refleja utilidad práctica)
- Permite comparación con otros repositorios
- El campo `downloads` en StandardizedModel representa "popularidad por uso"

### 2. likes = 0

**Decisión**: No hay sistema de likes en Replicate, se asigna 0.

**Justificación**:
- Replicate usa `run_count` como métrica principal
- No distorsiona comparaciones (es ausencia de dato, no dato falso)
- Preferencia por métricas de uso real sobre sociales

### 3. Inferencia de tags

**Decisión**: Extraer tags de la descripción usando keywords.

**Justificación**:
- Replicate no tiene sistema de tags formal
- Descripciones suelen ser técnicas y contienen keywords
- Permite búsqueda y clasificación básica
- Alternativa: usar análisis de título `owner/name`

### 4. title = id

**Decisión**: Usar `owner/name` como título.

**Justificación**:
- Replicate no tiene campo de título separado
- El formato `owner/name` es descriptivo
- Ejemplo: `stability-ai/sdxl` es claro

### 5. created_at = last_modified

**Decisión**: Usar fecha de `latest_version` para ambos campos.

**Justificación**:
- API no provee fecha de modificación separada
- `latest_version.created_at` refleja cambio más reciente
- Alternativa menos precisa que tener campos separados

## 🆕 Nuevas Propiedades en Ontología

Se requiere añadir a `daimo.ttl`:

```turtle
daimo:versionId rdf:type owl:DatatypeProperty ;
    rdfs:domain daimo:Model ;
    rdfs:range xsd:string ;
    rdfs:label "version ID" ;
    rdfs:comment "Identificador único de la versión del modelo (SHA del contenedor)" .

daimo:cogVersion rdf:type owl:DatatypeProperty ;
    rdfs:domain daimo:Model ;
    rdfs:range xsd:string ;
    rdfs:label "Cog version" ;
    rdfs:comment "Versión del framework Cog usado por Replicate para containerización" .
```

## 🔄 Comparación con Otros Repositorios

| Aspecto | Replicate | HuggingFace | Civitai | Kaggle |
|---------|-----------|-------------|---------|--------|
| **Métrica principal** | run_count | downloads | download_count | downloadCount |
| **Likes** | ❌ No | ✅ Sí | ✅ Sí | ✅ Sí |
| **GitHub URL** | ✅ Raro (10%) | ✅ Común | ❌ No | ❌ No |
| **Cover image** | ✅ 100% | ⚠️ Variable | ✅ 100% | ⚠️ Variable |
| **Versioning** | ✅ Explícito | ⚠️ Commits | ✅ Explícito | ❌ No |
| **Inference API** | ✅ Nativo | ⚠️ Premium | ❌ No | ❌ No |

## ⚡ Características Técnicas

### Paginación

```python
# Cursor-based (no offset)
params = {
    'cursor': next_cursor,  # De response.next
    'limit': 50
}
```

### Rate Limiting

- **Límite**: 3000 requests/min
- **Respuesta**: HTTP 429 con `Retry-After` header
- **Estrategia**: Exponential backoff automático

### Autenticación

```bash
# Variable de entorno
export REPLICATE_API_TOKEN="r8_..."

# Header HTTP
Authorization: Bearer r8_...
```

## 📝 Ejemplo de Uso

```python
from utils.replicate_repository import ReplicateRepository

# Inicializar (lee token de env)
repo = ReplicateRepository()

# Obtener modelos
models = repo.fetch_models(
    limit=100,
    sort_by="latest_version_created_at",
    sort_direction="desc"
)

# Mapear a RDF
for model in models:
    repo.map_to_rdf(model, graph, namespaces)

# Estadísticas
print(f"Total runs: {sum(m.downloads for m in models):,}")
print(f"Con GitHub: {sum(1 for m in models if m.extra_metadata.get('github_url'))}")
```

## 🐛 Problemas Conocidos

1. **GitHub URL raro**: Solo ~10% de modelos tienen GitHub URL
   - Muchos modelos son cerrados o propietarios
   
2. **Sin taxonomía de tareas**: No hay campo `pipeline_tag`
   - Se infiere de descripción (menos preciso)
   
3. **Fecha de modificación**: No distingue creación vs actualización
   - Ambos campos usan fecha de latest_version

4. **License**: Solo URL, no nombre de licencia
   - Requiere fetch adicional para obtener detalles

## 🔮 Mejoras Futuras

1. **Análisis de default_example**: Extraer inputs/outputs para inferir modalidad
2. **Fetch de versiones históricas**: API soporta /v1/models/{owner}/{name}/versions
3. **Parsing de nombre**: Extraer información de formato `owner/name-variant`
4. **Caché de imágenes**: Guardar cover_image_url localmente
5. **Taxonomía ML**: Clasificar modelos por arquitectura usando description

## 📚 Referencias

- [Replicate API Docs](https://replicate.com/docs/reference/http)
- [Cog Framework](https://github.com/replicate/cog)
- [Rate Limits](https://replicate.com/docs/reference/http#rate-limits)
- [Setup Guide](./REPLICATE_SETUP.md)

---

**Autor**: GitHub Copilot  
**Última actualización**: Enero 2025
