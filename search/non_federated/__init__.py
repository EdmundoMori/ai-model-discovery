"""
Non-Federated Search Module

Búsqueda semántica sobre grafo RDF local usando Text-to-SPARQL

Exports:
    - SearchEngine: Motor principal de búsqueda
    - SearchAPI: API wrapper
    - EnhancedSearchEngine: Motor con mejoras Phase 2 + Phase 3 + Phase 4
    - SearchResult, SearchResponse: Tipos de datos
    
Phase 2: Templates + Post-processing (5x faster for simple queries)
Phase 3: Complex query enhancement (Specialized RAG)
Phase 4: Hybrid BM25 ↔ Method1 (Intelligent routing + fusion)
"""

from .semantic_search import (
    SearchEngine,
    SearchResult,
    SearchResponse,
    create_search_engine
)

from .api import SearchAPI, create_api

from .enhanced_engine import (
    EnhancedSearchEngine,
    create_enhanced_api
)


__all__ = [
    "SearchEngine",
    "SearchResult",
    "SearchResponse",
    "create_search_engine",
    "SearchAPI",
    "create_api",
    "EnhancedSearchEngine",
    "create_enhanced_api"
]
