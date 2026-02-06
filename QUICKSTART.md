# Guía de Inicio Rápido

## Instalación y Configuración

### 1. Instalar Poetry (si no está instalado)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Instalar dependencias del proyecto

```bash
cd /home/edmundo/ai-model-discovery
poetry install
```

Esto instalará todas las dependencias definidas en `pyproject.toml`.

### 3. Activar el entorno virtual

```bash
poetry shell
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
nano .env  # Editar con tus API keys
```

Necesitarás al menos una API key de:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/

## Uso Básico

### Paso 1: Recolectar modelos de Hugging Face

```bash
# Recolectar 50 modelos (muestra pequeña)
poetry run python -m utils.collect_hf_models --limit 50 --output hf_models_sample.json

# Recolectar 100 modelos ordenados por descargas
poetry run python -m utils.collect_hf_models --limit 100 --sort downloads

# Filtrar por tarea específica
poetry run python -m utils.collect_hf_models --limit 50 --task text-classification
```

Los metadatos se guardan en `data/raw/`.

### Paso 2: Construir el grafo RDF

```bash
# Usando los datos recolectados
poetry run python knowledge_graph/build_graph.py \
  --input data/raw/hf_models_sample.json \
  --output data/processed/knowledge_graph.ttl \
  --format turtle
```

### Paso 3: Explorar con el notebook

```bash
# Iniciar Jupyter
poetry run jupyter notebook

# Abrir: notebooks/01_validation.ipynb
```

## Estructura del Workflow

```
1. Recolección      2. Transformación    3. Consulta
   (HF API)    →    (RDF Graph)      →    (SPARQL)
     │                   │                    │
     ├─ JSON            ├─ Turtle            ├─ Manual
     └─ Metadatos       └─ DAIMO             └─ LLM (Fase 2)
```

## Ejemplos Rápidos

### Consulta SPARQL desde Python

```python
from knowledge_graph import DAIMOGraphBuilder

# Cargar grafo
builder = DAIMOGraphBuilder()
builder.build_from_json("data/raw/hf_models_sample.json")

# Consultar
query = """
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?title ?task
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:subject ?task .
}
LIMIT 5
"""

results = builder.query(query)
for row in results:
    print(f"{row.title} - {row.task}")
```

## Solución de Problemas

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de estar en el entorno de Poetry
poetry shell
```

### Error: API keys no configuradas
```bash
# Verificar que .env existe y tiene las keys
cat .env
```

### Error: Memoria insuficiente
```bash
# Reducir el límite de modelos
poetry run python -m utils.collect_hf_models --limit 20
```

## Próximos Pasos

Una vez validada la Fase 1, continuar con:

1. **Fase 2**: Implementar Text-to-SPARQL con LLM
2. **Fase 3**: Búsqueda federada
3. **Fase 4**: Cross-repository search

Ver [README.md](README.md) para el plan completo.
