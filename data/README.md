# Directorio de Datos

Este directorio contiene los datos del proyecto organizados en dos subdirectorios:

## `raw/`

Datos originales sin procesar:

- **`hf_models.json`**: Metadatos de modelos de Hugging Face
- **`pwc_models.json`**: Datos de Papers with Code (Fase 4)
- **`openml_models.json`**: Datos de OpenML (Fase 4)

Los archivos se generan con el script `utils/collect_hf_models.py`.

**Nota**: Los archivos JSON grandes están en `.gitignore` para no sobrecargar el repositorio.

## `processed/`

Datos transformados y procesados:

- **`knowledge_graph.ttl`**: Grafo RDF completo en formato Turtle
- **`knowledge_graph.json-ld`**: Mismo grafo en JSON-LD
- **`catalog_*.ttl`**: Grafos separados para búsqueda federada (Fase 3)

Los grafos se generan con `knowledge_graph/build_graph.py`.

## Tamaño Recomendado

Para desarrollo y pruebas:
- **50-100 modelos**: Suficiente para validación
- **500-1000 modelos**: Para experimentos representativos
- **>5000 modelos**: Solo si el disco lo permite

Dado el espacio limitado (~33 GB en D:), mantener datasets pequeños y representativos.
