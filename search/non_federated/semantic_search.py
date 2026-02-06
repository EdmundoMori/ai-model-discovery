"""
Semantic Search Engine - Búsqueda no federada sobre grafo RDF local

Este módulo implementa el motor de búsqueda semántico que combina:
1. Conversión de lenguaje natural a SPARQL (Text-to-SPARQL)
2. Ejecución de queries contra grafo RDF
3. Ranking de resultados por relevancia

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging
from datetime import datetime

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS

# Imports del proyecto
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from llm import TextToSPARQLConverter, ConversionResult


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Resultado individual de búsqueda"""
    model_uri: str
    title: str
    source: str
    task: str
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "model_uri": self.model_uri,
            "title": self.title,
            "source": self.source,
            "task": self.task,
            "score": self.score,
            **self.metadata
        }


@dataclass
class SearchResponse:
    """Respuesta completa de búsqueda"""
    query: str
    results: List[SearchResult]
    total_results: int
    sparql_query: str
    execution_time: float
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
            "sparql_query": self.sparql_query,
            "execution_time": self.execution_time,
            "is_valid": self.is_valid,
            "errors": self.errors
        }


class SearchEngine:
    """
    Motor de búsqueda semántico sobre grafo RDF de modelos de IA
    
    Características:
    - Conversión automática de lenguaje natural a SPARQL
    - Validación de queries con ejecución real
    - Ranking de resultados por relevancia
    - Soporte para múltiples repositorios
    """
    
    def __init__(
        self,
        graph_path: Optional[Path] = None,
        graph: Optional[Graph] = None,
        llm_provider: str = "ollama",
        model: str = "deepseek-r1:7b",
        use_rag: bool = True,
        top_k_examples: int = 3,
        temperature: float = 0.1
    ):
        """
        Inicializar motor de búsqueda
        
        Args:
            graph_path: Ruta al grafo RDF serializado (opcional)
            graph: Grafo RDF ya cargado (opcional)
            llm_provider: Proveedor LLM (ollama, anthropic)
            model: Modelo a usar
            use_rag: Activar RAG con ejemplos SPARQL
            top_k_examples: Número de ejemplos RAG
            temperature: Temperatura del LLM
        """
        self.DAIMO = Namespace("http://purl.org/pionera/daimo#")
        
        # Cargar o usar grafo existente
        if graph is not None:
            self.graph = graph
            logger.info("✅ Usando grafo RDF proporcionado")
        elif graph_path is not None:
            self.graph = self._load_graph(graph_path)
            logger.info(f"✅ Grafo cargado desde {graph_path}")
        else:
            raise ValueError("Se debe proporcionar 'graph' o 'graph_path'")
        
        # Estadísticas del grafo
        self.total_models = len(list(self.graph.subjects(RDF.type, self.DAIMO.Model)))
        self.total_triples = len(self.graph)
        
        logger.info(f"📊 Grafo: {self.total_models} modelos, {self.total_triples:,} triples")
        
        # Inicializar conversor Text-to-SPARQL
        self.converter = TextToSPARQLConverter(
            llm_provider=llm_provider,
            model=model,
            use_rag=use_rag,
            top_k_examples=top_k_examples,
            temperature=temperature,
            validation_graph=self.graph
        )
        
        logger.info(f"✅ SearchEngine inicializado ({llm_provider}/{model})")
    
    def _load_graph(self, path: Path) -> Graph:
        """Cargar grafo RDF desde archivo"""
        g = Graph()
        g.parse(str(path), format="turtle")
        return g
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        min_score: float = 0.0
    ) -> SearchResponse:
        """
        Ejecutar búsqueda semántica
        
        Args:
            query: Query en lenguaje natural
            max_results: Número máximo de resultados
            min_score: Score mínimo para incluir resultado
            
        Returns:
            SearchResponse con resultados rankeados
        """
        start_time = datetime.now()
        
        logger.info(f"🔍 Búsqueda: '{query}'")
        
        # 1. Convertir a SPARQL
        conversion = self.converter.convert(query, validate=True)
        
        if not conversion.is_valid:
            logger.warning(f"❌ Query inválida: {conversion.validation_errors}")
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                sparql_query=conversion.sparql_query,
                execution_time=0.0,
                is_valid=False,
                errors=conversion.validation_errors
            )
        
        # 2. Ejecutar SPARQL contra grafo
        try:
            sparql_results = self.graph.query(conversion.sparql_query)
            raw_results = list(sparql_results)
            
            logger.info(f"✅ {len(raw_results)} resultados encontrados")
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando SPARQL: {e}")
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                sparql_query=conversion.sparql_query,
                execution_time=0.0,
                is_valid=False,
                errors=[str(e)]
            )
        
        # 3. Parsear y rankear resultados
        search_results = self._parse_results(raw_results, query)
        ranked_results = self._rank_results(search_results, query)
        
        # 4. Filtrar y limitar
        filtered = [r for r in ranked_results if r.score >= min_score]
        limited = filtered[:max_results]
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ {len(limited)} resultados retornados ({execution_time:.2f}s)")
        
        return SearchResponse(
            query=query,
            results=limited,
            total_results=len(raw_results),
            sparql_query=conversion.sparql_query,
            execution_time=execution_time,
            is_valid=True
        )
    
    def _parse_results(self, raw_results: List, query: str) -> List[SearchResult]:
        """Parsear resultados SPARQL a SearchResult"""
        results = []
        
        for row in raw_results:
            # Convertir row a diccionario para acceso flexible
            row_dict = row.asdict() if hasattr(row, 'asdict') else {}
            
            # Intentar obtener el URI del modelo de varias formas
            model_uri = None
            if 'model' in row_dict:
                model_uri = str(row_dict['model'])
            elif hasattr(row, 'model'):
                model_uri = str(row.model)
            elif len(row) > 0 and str(row[0]).startswith('http'):
                # Fallback: primer elemento si parece un URI
                model_uri = str(row[0])
            
            if not model_uri:
                # Si no encontramos el URI, skip este resultado
                logger.warning(f"No se pudo extraer model_uri de resultado SPARQL")
                continue
            
            # Obtener metadatos completos del grafo
            metadata = self._get_model_metadata(URIRef(model_uri))
            
            # Usar datos del query SPARQL si están disponibles, sino del grafo
            title = row_dict.get('title', metadata.get('title', 'Unknown'))
            source = row_dict.get('source', metadata.get('source', 'Unknown'))
            task = row_dict.get('task', metadata.get('task', 'Unknown'))
            
            # Convertir a string si es necesario
            if title and not isinstance(title, str):
                title = str(title)
            if source and not isinstance(source, str):
                source = str(source)
            if task and not isinstance(task, str):
                task = str(task)
            
            result = SearchResult(
                model_uri=model_uri,
                title=title,
                source=source,
                task=task,
                score=0.0,  # Se calcula en ranking
                metadata=metadata
            )
            
            results.append(result)
        
        return results
    
    def _get_model_metadata(self, model_uri: URIRef) -> Dict[str, Any]:
        """Obtener metadatos completos de un modelo"""
        metadata = {}
        
        # Propiedades a extraer (usando namespaces correctos)
        properties = [
            ("title", DCTERMS.title),           # dcterms:title
            ("source", DCTERMS.source),         # dcterms:source
            ("description", DCTERMS.description), # dcterms:description
            ("task", self.DAIMO.task),          # daimo:task
            ("library", self.DAIMO.library),    # daimo:library
            ("downloads", self.DAIMO.downloads), # daimo:downloads
            ("likes", self.DAIMO.likes),        # daimo:likes (rating)
            ("accessLevel", self.DAIMO.accessLevel), # daimo:accessLevel
            ("domain", self.DAIMO.domain),      # daimo:domain
            ("sourceURL", self.DAIMO.sourceURL) # daimo:sourceURL
        ]
        
        for prop_name, prop_uri in properties:
            value = self.graph.value(model_uri, prop_uri)
            if value:
                metadata[prop_name] = str(value)
        
        # Mapear 'likes' a 'rating' para compatibilidad
        if 'likes' in metadata:
            try:
                metadata['rating'] = float(metadata['likes']) / 100.0  # Normalizar a escala 0-5
            except:
                metadata['rating'] = 0.0
        
        return metadata
    
    def _rank_results(
        self,
        results: List[SearchResult],
        query: str
    ) -> List[SearchResult]:
        """
        Rankear resultados por relevancia
        
        Estrategia simple:
        - Score base: 1.0
        - Boost por coincidencia en título
        - Boost por popularidad (downloads)
        - Boost por rating
        """
        query_lower = query.lower()
        
        for result in results:
            score = 1.0
            
            # Boost por coincidencia en título
            if query_lower in result.title.lower():
                score += 2.0
            
            # Boost por popularidad (normalizado)
            downloads = int(result.metadata.get("downloads", 0))
            if downloads > 0:
                score += min(downloads / 10_000_000, 2.0)
            
            # Boost por rating
            rating = float(result.metadata.get("rating", 0))
            if rating > 0:
                score += rating / 5.0  # Normalizar a 0-1
            
            result.score = round(score, 2)
        
        # Ordenar por score descendente
        return sorted(results, key=lambda r: r.score, reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del grafo"""
        stats = {
            "total_models": self.total_models,
            "total_triples": self.total_triples,
            "repositories": self._count_by_property(self.DAIMO.source),
            "tasks": self._count_by_property(self.DAIMO.task),
            "libraries": self._count_by_property(self.DAIMO.library),
            "access_levels": self._count_by_property(self.DAIMO.accessLevel)
        }
        
        return stats
    
    def _count_by_property(self, property_uri: URIRef) -> Dict[str, int]:
        """Contar valores únicos de una propiedad"""
        counts = {}
        
        for model in self.graph.subjects(RDF.type, self.DAIMO.Model):
            value = self.graph.value(model, property_uri)
            if value:
                value_str = str(value)
                counts[value_str] = counts.get(value_str, 0) + 1
        
        return counts


# Función de conveniencia para uso rápido
def create_search_engine(
    graph_path: Optional[Path] = None,
    graph: Optional[Graph] = None,
    **kwargs
) -> SearchEngine:
    """
    Crear instancia de SearchEngine con configuración por defecto
    
    Args:
        graph_path: Ruta al grafo RDF
        graph: Grafo RDF ya cargado
        **kwargs: Argumentos adicionales para SearchEngine
    
    Returns:
        SearchEngine configurado
    """
    return SearchEngine(graph_path=graph_path, graph=graph, **kwargs)
