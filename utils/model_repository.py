"""
Interfaz abstracta para repositorios de modelos de IA.

Este módulo define la interfaz base que todos los conectores de repositorios
deben implementar, siguiendo el patrón Strategy para permitir descubrimiento
de modelos desde múltiples fuentes (HuggingFace, Kaggle, Civitai, etc.).

Autor: Edmundo Mori
Fecha: Enero 2026
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class StandardizedModel:
    """
    Estructura de datos estandarizada para modelos de cualquier repositorio.
    
    Esta clase normaliza los metadatos de diferentes fuentes a un formato común
    que luego se mapea a la ontología DAIMO.
    """
    # Identificación (requerido)
    id: str
    source: str  # "huggingface", "kaggle", "civitai", "paperswithcode", "azure"
    
    # Metadatos básicos
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[str] = None
    last_modified: Optional[str] = None
    
    # Clasificación y taxonomía
    tags: List[str] = field(default_factory=list)
    task: Optional[str] = None
    pipeline_tag: Optional[str] = None
    
    # Popularidad y métricas sociales
    downloads: int = 0
    likes: int = 0
    
    # Técnico
    library: Optional[str] = None  # transformers, diffusers, pytorch, tensorflow
    framework: Optional[str] = None  # Alias para library
    architectures: List[str] = field(default_factory=list)
    model_type: Optional[str] = None
    
    # Control de acceso
    license: Optional[str] = None
    private: bool = False
    gated: bool = False
    requires_approval: bool = False
    nsfw: bool = False
    
    # Derivación y fine-tuning
    base_model: Optional[str] = None
    fine_tuned_from: Optional[str] = None
    
    # Configuración
    config: Optional[Dict] = None
    hyperparameters: Optional[Dict] = None
    trigger_words: List[str] = field(default_factory=list)
    
    # Evaluaciones
    eval_results: Optional[List[Dict]] = None
    benchmarks: Optional[List[Dict]] = None
    
    # Papers y research
    paper_url: Optional[str] = None
    paper_title: Optional[str] = None
    method_name: Optional[str] = None
    algorithm: Optional[str] = None
    
    # Deployment
    inference_endpoint: Optional[str] = None
    deployment_target: Optional[str] = None
    
    # Parámetros
    parameter_count: Optional[int] = None
    
    # Metadata adicional (específico por repositorio)
    extra_metadata: Dict = field(default_factory=dict)
    
    # Timestamp de recolección
    collected_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ModelRepository(ABC):
    """
    Clase abstracta base para todos los conectores de repositorios.
    
    Todos los repositorios deben implementar:
    - fetch_models(): Obtener modelos del repositorio
    - map_to_rdf(): Mapear un modelo a triples RDF específicos del repositorio
    """
    
    def __init__(self, name: str):
        """
        Inicializa el repositorio.
        
        Args:
            name: Nombre identificador del repositorio
        """
        self.name = name
        self.models_fetched = 0
        self.errors = []
    
    @abstractmethod
    def fetch_models(self, limit: int = 50, **kwargs) -> List[StandardizedModel]:
        """
        Obtiene modelos del repositorio y los normaliza a StandardizedModel.
        
        Args:
            limit: Número máximo de modelos a obtener
            **kwargs: Parámetros adicionales específicos del repositorio
        
        Returns:
            Lista de objetos StandardizedModel
        
        Raises:
            Exception: Si hay errores críticos en la conexión
        """
        pass
    
    @abstractmethod
    def map_to_rdf(self, model: StandardizedModel, graph, namespaces: Dict) -> None:
        """
        Mapea un modelo estandarizado a triples RDF específicos del repositorio.
        
        Este método añade triples ADICIONALES específicos de cada repositorio
        al grafo RDF. El mapeo básico (común a todos) se hace en build_graph.py.
        
        Args:
            model: Modelo estandarizado
            graph: Grafo RDFLib donde añadir triples
            namespaces: Diccionario con namespaces (DAIMO, MLS, ODRL, etc.)
        """
        pass
    
    def fetch_with_error_handling(self, limit: int = 50, **kwargs) -> List[StandardizedModel]:
        """
        Envoltorio con manejo de errores para fetch_models.
        
        Captura excepciones y permite que el sistema continúe con otros repositorios.
        """
        try:
            print(f"🔍 Fetching from {self.name}...")
            models = self.fetch_models(limit=limit, **kwargs)
            self.models_fetched = len(models)
            print(f"✅ {self.name}: {self.models_fetched} models fetched")
            return models
        except Exception as e:
            error_msg = f"❌ {self.name}: {str(e)}"
            print(error_msg)
            self.errors.append(error_msg)
            return []
    
    def get_statistics(self) -> Dict:
        """Retorna estadísticas del repositorio."""
        return {
            "name": self.name,
            "models_fetched": self.models_fetched,
            "errors": self.errors,
            "success": len(self.errors) == 0
        }
