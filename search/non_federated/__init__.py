"""
Non-Federated Search Module

Búsqueda semántica sobre grafo RDF local usando Text-to-SPARQL

Exports:
    - SearchEngine: Motor principal de búsqueda
    - SearchAPI: API wrapper
    - SearchResult, SearchResponse: Tipos de datos
"""

from .semantic_search import (
    SearchEngine,
    SearchResult,
    SearchResponse,
    create_search_engine
)

from .api import SearchAPI, create_api


__all__ = [
    "SearchEngine",
    "SearchResult",
    "SearchResponse",
    "create_search_engine",
    "SearchAPI",
    "create_api"
]
