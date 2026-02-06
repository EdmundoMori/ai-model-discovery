"""
LLM Module: Text-to-SPARQL with LangChain + RAG
================================================

Este módulo proporciona conversión de lenguaje natural a SPARQL usando:
- LangChain para orquestación de LLM
- RAG (Retrieval Augmented Generation) para selección dinámica de ejemplos
- Claude 3.5 Sonnet como backend
- ChromaDB como vector store

Uso rápido:
-----------
>>> from llm import TextToSPARQLConverter
>>> converter = TextToSPARQLConverter(use_rag=True)
>>> result = converter.convert("show me popular models")
>>> print(result.sparql_query)
"""

from .text_to_sparql import (
    TextToSPARQLConverter,
    ConversionResult,
    convert_text_to_sparql
)

from .query_validator import (
    validate_sparql,
    SPARQLValidator
)

from .rag_sparql_examples import (
    get_all_examples,
    get_examples_by_complexity,
    get_examples_by_category,
    search_examples_by_keywords,
    SPARQLExample
)

__all__ = [
    # Main converter
    'TextToSPARQLConverter',
    'ConversionResult',
    'convert_text_to_sparql',
    
    # Validator
    'validate_sparql',
    'SPARQLValidator',
    
    # RAG knowledge base
    'get_all_examples',
    'get_examples_by_complexity',
    'get_examples_by_category',
    'search_examples_by_keywords',
    'SPARQLExample',
]

__version__ = '1.0.0'
__author__ = 'AI Model Discovery Team'
