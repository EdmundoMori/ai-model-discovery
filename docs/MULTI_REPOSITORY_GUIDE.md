# Multi-Repository AI Model Discovery

Sistema extensible para descubrir y catalogar modelos de IA desde múltiples fuentes en un grafo RDF unificado usando la ontología DAIMO.

## 🎯 Características

- **Arquitectura modular (Strategy Pattern)**: Fácil de extender con nuevos repositorios
- **Normalización de datos**: StandardizedModel unifica metadatos de diferentes fuentes
- **Mapeo RDF específico**: Cada repositorio implementa su lógica de mapeo a DAIMO
- **Manejo robusto de errores**: Si un repositorio falla, el sistema continúa con los otros
- **Compatibilidad retroactiva**: Mantiene funcionalidad del colector HuggingFace original

## 📦 Repositorios Soportados

### ✅ Implementados

1. **HuggingFace Hub** (`HuggingFaceRepository`)
   - Modelos de ML/DL (transformers, diffusers, etc.)
   - Mapeo: Arquitecturas, parámetros, evaluaciones

2. **Kaggle Models** (`KaggleRepository`)
   - Modelos compartidos por la comunidad Kaggle
   - Mapeo: `upvotes → daimo:likes`, `downloadCount → daimo:downloads`, `framework → daimo:library`

3. **Civitai** (`CivitaiRepository`)
   - Modelos de difusión (Stable Diffusion, SDXL)
   - Mapeo CRÍTICO: 
     - `Base Model → daimo:fineTunedFrom`
     - `triggerWords → daimo:HyperparameterConfiguration`
     - `nsfw: true → daimo:requiresApproval`

### ❌ Descontinuados

- **Papers With Code** - API no funcional (devuelve HTML en lugar de JSON)
- **Azure AI** - Requiere suscripción de pago (pendiente de implementación)

## 🏗️ Arquitectura

```
utils/
├── model_repository.py          # Interfaz abstracta base
├── huggingface_repository.py    # Conector HuggingFace
├── kaggle_repository.py          # Conector Kaggle
├── civitai_repository.py         # Conector Civitai
└── azure_repository.py           # Conector Azure AI (stub)

knowledge_graph/
├── build_graph.py                # Builder original (mantiene compatibilidad)
└── multi_repository_builder.py  # Builder multi-repositorio

collect_multi_repository.py       # Script de orquestación principal
```

### Flujo de Datos

```
┌─────────────────┐
│  Repositorios   │
│  (HF, Kaggle,   │
│   Civitai...)   │
└────────┬────────┘
         │
         │ fetch_models()
         ▼
┌─────────────────────┐
│ StandardizedModel   │  ◄── Normalización
│  (formato común)    │
└────────┬────────────┘
         │
         │ add_standardized_model()
         ▼
┌─────────────────────┐
│  RDF Graph Builder  │
│  (mapeo genérico)   │
└────────┬────────────┘
         │
         │ map_to_rdf()  (por repositorio)
         ▼
┌─────────────────────┐
│   Grafo RDF DAIMO   │
│   (kg_multi.ttl)    │
└─────────────────────┘
```

## 🚀 Uso

### Instalación

```bash
# Instalar dependencias
pip install rdflib huggingface_hub

# Opcional: Para repositorios adicionales
pip install kaggle            # Para Kaggle
pip install azure-ai-ml       # Para Azure AI
```

### Uso Básico

```bash
# Recolectar de todos los repositorios (50 modelos c/u)
python collect_multi_repository.py --limit 50

# Solo HuggingFace y Kaggle
python collect_multi_repository.py --repos huggingface kaggle --limit 25

# Especificar archivo de salida
python collect_multi_repository.py --output my_graph.ttl --limit 100
```

### Uso Programático

```python
from utils.huggingface_repository import HuggingFaceRepository
from utils.kaggle_repository import KaggleRepository
from knowledge_graph.multi_repository_builder import MultiRepositoryGraphBuilder

# Crear builder
builder = MultiRepositoryGraphBuilder()

# Crear repositorios
hf_repo = HuggingFaceRepository()
kaggle_repo = KaggleRepository()

# Construir grafo
models_added = builder.build_from_repositories(
    repositories=[hf_repo, kaggle_repo],
    limit_per_repo=50
)

# Guardar
builder.save("data/processed/my_graph.ttl")
```

## 🗺️ Mapeo a Ontología DAIMO

### Mapeo Genérico (Común a Todos)

| Campo StandardizedModel | Propiedad RDF | Tipo |
|------------------------|---------------|------|
| `id` | `dcterms:identifier` | string |
| `title` | `dcterms:title` | string |
| `author` | `dcterms:creator` | URI (foaf:Agent) |
| `downloads` | `daimo:downloads` | integer |
| `likes` | `daimo:likes` | integer |
| `library` | `daimo:library` | string |
| `architectures` | `daimo:hasArchitecture` | URI (daimo:ModelArchitecture) |
| `requires_approval` | `daimo:requiresApproval` | boolean |
| `parameter_count` | `daimo:parameterCount` | long |
| `fine_tuned_from` | `daimo:fineTunedFrom` | URI (daimo:Model) |
| `inference_endpoint` | `daimo:inferenceEndpoint` | anyURI |

### Mapeos Específicos por Repositorio

#### HuggingFace
- `sha` → `dcterms:identifier`
- `siblings` → `daimo:hasFile` (daimo:ModelFile)

#### Kaggle
- `license` → `odrl:Policy` (odrl:Offer)
- `kaggle_ref` → `dcterms:identifier`

#### Civitai (CRÍTICO)
- `base_model` → `daimo:fineTunedFrom` + `prov:wasDerivedFrom`
- `trigger_words` → `daimo:HyperparameterConfiguration` + `daimo:triggerWord`
- `nsfw: true` → `daimo:requiresApproval = true` + `daimo:nsfwLevel`

#### Papers With Code (CRÍTICO)
- `paper/method` → `mls:Algorithm`
- Relación: `model mls:implements algorithm`
- `paper_url` → `dcterms:references` (foaf:Document)
- `arxiv_id` → `dcterms:identifier` (en paper)

#### Azure AI
- `endpoint` → `daimo:InferenceEndpoint` (URI node)
- `deployment_target` → `daimo:deploymentTarget`
- `region` → `daimo:deploymentRegion`

## 🧪 Ejemplo de Consultas SPARQL

### Modelos por Fuente

```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/DC/terms/>

SELECT ?source (COUNT(?model) as ?count)
WHERE {
    ?model a daimo:Model ;
           dcterms:source ?source .
}
GROUP BY ?source
ORDER BY DESC(?count)
```

### Modelos Fine-tuned de Civitai

```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/DC/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>

SELECT ?model ?base_model
WHERE {
    ?model a daimo:Model ;
           dcterms:source "civitai" ;
           daimo:fineTunedFrom ?base .
    ?base dcterms:title ?base_model .
}
```

### Papers y sus Implementaciones

```sparql
PREFIX mls: <http://www.w3.org/ns/mls#>
PREFIX dcterms: <http://purl.org/DC/terms/>

SELECT ?model ?algorithm ?paper_title
WHERE {
    ?model mls:implements ?algorithm .
    ?algorithm a mls:Algorithm .
    ?model dcterms:references ?paper .
    ?paper dcterms:title ?paper_title .
}
```

## 🔧 Extender con Nuevos Repositorios

### 1. Crear Nueva Clase Repositorio

```python
from utils.model_repository import ModelRepository, StandardizedModel
from rdflib import Literal, URIRef, RDF, XSD

class MyNewRepository(ModelRepository):
    def __init__(self):
        super().__init__("MyNewRepo")
    
    def fetch_models(self, limit=50, **kwargs) -> List[StandardizedModel]:
        # TODO: Llamar a API y obtener datos
        models = []
        
        for raw_model in api_response:
            std_model = StandardizedModel(
                id=f"mynewrepo_{raw_model['id']}",
                source="mynewrepo",
                title=raw_model['name'],
                # ... mapear campos
            )
            models.append(std_model)
        
        return models
    
    def map_to_rdf(self, model: StandardizedModel, graph, namespaces: Dict):
        DAIMO = namespaces['DAIMO']
        model_uri = DAIMO[f"model/{model.id}"]
        
        # Añadir triples ESPECÍFICOS de este repositorio
        # (El mapeo genérico ya se hace en MultiRepositoryGraphBuilder)
```

### 2. Registrar en Script Principal

```python
# En collect_multi_repository.py
from utils.mynew_repository import MyNewRepository

if "mynewrepo" in repo_list:
    repositories.append(MyNewRepository())
```

## 📊 Ventajas del Diseño

1. **Separación de Responsabilidades**
   - `StandardizedModel`: Normalización de datos
   - `ModelRepository`: Recolección de datos
   - `MultiRepositoryGraphBuilder`: Mapeo RDF genérico
   - `map_to_rdf()`: Mapeo RDF específico

2. **Extensibilidad**
   - Añadir nuevo repositorio = 1 clase nueva
   - No requiere modificar código existente

3. **Robustez**
   - Error en un repositorio no afecta a otros
   - Manejo graceful de APIs no disponibles

4. **Trazabilidad**
   - Cada modelo tiene `dcterms:source`
   - Estadísticas por repositorio

5. **Compatibilidad**
   - Sistema original (HuggingFace JSON) sigue funcionando
   - `DAIMOGraphBuilder` intacto

## 📝 Notas Importantes

### Autenticación de APIs

- **Kaggle**: Requiere `~/.kaggle/kaggle.json` o variable de entorno
- **Azure**: Requiere `az login` o credenciales en variables de entorno
- **Civitai**: API pública, pero rate limits aplican
- **HuggingFace**: Opcional, pero recomendado para evitar rate limits

### Limitaciones Conocidas

1. **Kaggle & Azure**: APIs no implementadas completamente (usar TODOs como guía)
2. **Civitai & PWC**: Usando datos de ejemplo (fácil de reemplazar con APIs reales)
3. **Métricas sociales**: No todos los repositorios tienen downloads/likes (Azure)

### Performance

- HuggingFace: ~1-2 segundos por modelo (llamadas a `model_info()`)
- Otros: Depende de API, típicamente más rápidos
- Para 50 modelos × 5 repos: ~5-10 minutos

## 🎓 Referencias

- DAIMO Ontology: `ontologies/daimo.ttl`
- ML-Schema: http://www.w3.org/ns/mls
- DCAT: http://www.w3.org/ns/dcat
- ODRL: http://www.w3.org/ns/odrl/2/
- PROV-O: http://www.w3.org/ns/prov

---

**Autor:** Edmundo Mori  
**Fecha:** Enero 2026  
**Versión:** 2.0 (Multi-Repository)
