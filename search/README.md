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
