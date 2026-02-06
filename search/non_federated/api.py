"""
API Wrapper para SearchEngine

Proporciona una interfaz simple para integrar el motor de búsqueda
con interfaces de usuario (CLI, Web UI, etc.)

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import logging

from .semantic_search import SearchEngine, SearchResponse, create_search_engine


logger = logging.getLogger(__name__)


class SearchAPI:
    """
    API simplificada para interactuar con SearchEngine
    
    Proporciona métodos de alto nivel para:
    - Búsqueda semántica
    - Estadísticas del grafo
    - Gestión de configuración
    """
    
    def __init__(
        self,
        graph_path: Optional[Path] = None,
        graph=None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializar API
        
        Args:
            graph_path: Ruta al grafo RDF
            graph: Grafo RDF ya cargado
            config: Configuración personalizada
        """
        # Configuración por defecto
        default_config = {
            "llm_provider": "ollama",
            "model": "deepseek-r1:7b",
            "use_rag": True,
            "top_k_examples": 3,
            "temperature": 0.1,
            "max_results": 10,
            "min_score": 0.0
        }
        
        self.config = {**default_config, **(config or {})}
        
        # Inicializar motor de búsqueda
        self.engine = create_search_engine(
            graph_path=graph_path,
            graph=graph,
            llm_provider=self.config["llm_provider"],
            model=self.config["model"],
            use_rag=self.config["use_rag"],
            top_k_examples=self.config["top_k_examples"],
            temperature=self.config["temperature"]
        )
        
        logger.info("✅ SearchAPI inicializada")
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        min_score: Optional[float] = None,
        format: str = "dict"
    ) -> Any:
        """
        Ejecutar búsqueda semántica
        
        Args:
            query: Query en lenguaje natural
            max_results: Número máximo de resultados (None = usar config)
            min_score: Score mínimo (None = usar config)
            format: Formato de salida ('dict', 'json', 'response')
            
        Returns:
            Resultados en el formato especificado
        """
        max_results = max_results or self.config["max_results"]
        min_score = min_score or self.config["min_score"]
        
        response = self.engine.search(
            query=query,
            max_results=max_results,
            min_score=min_score
        )
        
        if format == "response":
            return response
        elif format == "json":
            return json.dumps(response.to_dict(), indent=2, ensure_ascii=False)
        else:  # dict
            return response.to_dict()
    
    def get_statistics(self, format: str = "dict") -> Any:
        """
        Obtener estadísticas del grafo
        
        Args:
            format: Formato de salida ('dict', 'json')
            
        Returns:
            Estadísticas en el formato especificado
        """
        stats = self.engine.get_statistics()
        
        if format == "json":
            return json.dumps(stats, indent=2, ensure_ascii=False)
        else:
            return stats
    
    def get_sparql(self, query: str) -> str:
        """
        Obtener query SPARQL sin ejecutarla
        
        Args:
            query: Query en lenguaje natural
            
        Returns:
            Query SPARQL generada
        """
        conversion = self.engine.converter.convert(query, validate=False)
        return conversion.sparql_query
    
    def get_config(self) -> Dict[str, Any]:
        """Obtener configuración actual"""
        return self.config.copy()
    
    def update_config(self, **kwargs):
        """Actualizar configuración"""
        self.config.update(kwargs)
        logger.info(f"✅ Configuración actualizada: {kwargs}")


def create_api(
    graph_path: Optional[Path] = None,
    graph=None,
    **config
) -> SearchAPI:
    """
    Crear instancia de SearchAPI
    
    Args:
        graph_path: Ruta al grafo RDF
        graph: Grafo RDF ya cargado
        **config: Parámetros de configuración
        
    Returns:
        SearchAPI configurada
    """
    return SearchAPI(graph_path=graph_path, graph=graph, config=config)
