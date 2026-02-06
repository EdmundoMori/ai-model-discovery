"""
Constructor de Grafo RDF Multi-Repositorio.

Extensión del DAIMOGraphBuilder original para soportar modelos de múltiples
repositorios usando la interfaz StandardizedModel.

Este módulo mantiene compatibilidad con el sistema anterior (JSON de HuggingFace)
y añade soporte para el nuevo sistema multi-repositorio.

Autor: Edmundo Mori
Fecha: Enero 2026
"""

from typing import List, Dict
from pathlib import Path
import re
from urllib.parse import quote

from rdflib import Literal, URIRef, RDF, RDFS, XSD
from rdflib.namespace import FOAF, DCTERMS

from .build_graph import DAIMOGraphBuilder
from utils.model_repository import StandardizedModel, ModelRepository


def sanitize_uri(uri: str) -> str:
    """
    Sanitiza URIs para uso seguro en RDF.
    
    URL-encode caracteres especiales que pueden causar errores
    de serialización en Turtle/N3.
    
    Args:
        uri: URI a sanitizar
        
    Returns:
        URI sanitizada con caracteres especiales codificados
    """
    if not uri:
        return ""
    
    # Convertir a string si no lo es
    uri = str(uri)
    
    # Separar esquema (http://, https://) del resto
    if '://' in uri:
        scheme, rest = uri.split('://', 1)
        # Separar dominio/puerto de path
        if '/' in rest:
            authority, path = rest.split('/', 1)
            # URL-encode solo el path (después del dominio)
            # safe='/' mantiene las barras del path
            encoded_path = quote(path, safe='/:@!$&\'()*+,;=')
            return f"{scheme}://{authority}/{encoded_path}"
        else:
            # Solo dominio, no hay path
            return uri
    else:
        # No es una URL completa, codificar todo
        # Preservar caracteres comunes en URIs del namespace
        return quote(uri, safe='/:@!$&\'()*+,;=#')


def sanitize_string(value: str) -> str:
    """
    Sanitiza strings para uso seguro en RDF.
    
    Elimina o escapa caracteres problemáticos que pueden causar
    errores de sintaxis en Turtle.
    
    Args:
        value: String a sanitizar
        
    Returns:
        String sanitizado
    """
    if not value:
        return ""
    
    # Convertir a string si no lo es
    value = str(value)
    
    # Eliminar caracteres de control (excepto newline y tab)
    value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
    
    # Reemplazar comillas dobles problemáticas
    value = value.replace('"', "'")
    
    # Eliminar backslashes que no sean parte de escape válido
    value = re.sub(r'\\(?![nrt"\\])', '', value)
    
    # Limitar longitud para descripciones muy largas
    if len(value) > 5000:
        value = value[:4997] + "..."
    
    return value.strip()


class MultiRepositoryGraphBuilder(DAIMOGraphBuilder):
    """
    Constructor de grafos RDF que soporta múltiples repositorios.
    
    Extiende DAIMOGraphBuilder para trabajar con StandardizedModel
    y coordinar el mapeo específico de cada repositorio.
    """
    
    def __init__(self, ontology_path: str = "ontologies/daimo.ttl"):
        """
        Inicializa el builder multi-repositorio.
        
        Args:
            ontology_path: Ruta a la ontología DAIMO
        """
        super().__init__(ontology_path)
        self.repositories = []
        self.models_by_source = {}
    
    def add_repository(self, repository: ModelRepository):
        """
        Añade un repositorio al builder.
        
        Args:
            repository: Instancia de ModelRepository
        """
        self.repositories.append(repository)
        print(f"✅ Repositorio añadido: {repository.name}")
    
    def fetch_all_models(self, limit_per_repo: int = 50) -> List[StandardizedModel]:
        """
        Obtiene modelos de todos los repositorios registrados.
        
        Args:
            limit_per_repo: Límite de modelos por repositorio
        
        Returns:
            Lista combinada de StandardizedModel de todos los repositorios
        """
        all_models = []
        
        print(f"\n🔍 Fetching models from {len(self.repositories)} repositories...")
        print("=" * 80)
        
        for repo in self.repositories:
            models = repo.fetch_with_error_handling(limit=limit_per_repo)
            all_models.extend(models)
            
            # Rastrear por fuente
            self.models_by_source[repo.name] = models
        
        print("=" * 80)
        print(f"✅ Total models fetched: {len(all_models)}")
        
        # Mostrar distribución por fuente
        print("\n📊 Distribution by source:")
        for source, models in self.models_by_source.items():
            print(f"   - {source}: {len(models)} models")
        
        return all_models
    
    def add_standardized_model(
        self,
        model: StandardizedModel,
        repository: ModelRepository = None
    ) -> URIRef:
        """
        Añade un modelo estandarizado al grafo RDF.
        
        Este método implementa el mapeo GENÉRICO común a todos los repositorios.
        Los mapeos ESPECÍFICOS se delegan a cada repositorio vía map_to_rdf().
        
        Args:
            model: Modelo estandarizado
            repository: Repositorio de origen (para mapeo específico)
        
        Returns:
            URIRef del modelo creado
        """
        # Crear URI del modelo
        model_uri = self._create_model_uri(model.id)
        
        # === MAPEO GENÉRICO (COMÚN A TODOS LOS REPOSITORIOS) ===
        
        # Tipo: daimo:Model
        self.graph.add((model_uri, RDF.type, self.DAIMO.Model))
        self.graph.add((model_uri, RDF.type, self.DCAT.Dataset))
        
        # Identificación
        if model.id:
            safe_id = sanitize_string(model.id)
            self.graph.add((model_uri, DCTERMS.identifier, Literal(safe_id, datatype=XSD.string)))
        
        if model.title:
            safe_title = sanitize_string(model.title)
            self.graph.add((model_uri, DCTERMS.title, Literal(safe_title, datatype=XSD.string)))
        
        if model.description:
            safe_desc = sanitize_string(model.description)
            self.graph.add((model_uri, DCTERMS.description, Literal(safe_desc, datatype=XSD.string)))
        
        # Fuente
        safe_source = sanitize_string(model.source)
        self.graph.add((model_uri, self.DAIMO.source, Literal(safe_source, datatype=XSD.string)))
        self.graph.add((model_uri, DCTERMS.source, Literal(safe_source, datatype=XSD.string)))
        
        # Autor
        if model.author:
            safe_author = sanitize_string(model.author)
            author_uri = self._create_agent_uri(safe_author)
            self.graph.add((author_uri, RDF.type, FOAF.Agent))
            self.graph.add((author_uri, FOAF.name, Literal(safe_author, datatype=XSD.string)))
            self.graph.add((model_uri, DCTERMS.creator, author_uri))
        
        # Fechas
        if model.created_at:
            norm_created = self._normalize_datetime(model.created_at)
            if norm_created:
                self.graph.add((model_uri, DCTERMS.created, Literal(norm_created, datatype=XSD.dateTime)))
        
        if model.last_modified:
            norm_modified = self._normalize_datetime(model.last_modified)
            if norm_modified:
                self.graph.add((model_uri, DCTERMS.modified, Literal(norm_modified, datatype=XSD.dateTime)))
        
        # Tarea/Pipeline tag
        if model.task or model.pipeline_tag:
            task_name = model.task or model.pipeline_tag
            safe_task = sanitize_string(task_name)
            # Agregar como Literal para consultas directas
            self.graph.add((model_uri, self.DAIMO.task, Literal(safe_task, datatype=XSD.string)))
            self.graph.add((model_uri, DCTERMS.subject, Literal(safe_task, datatype=XSD.string)))
            
            task_uri = self._create_task_uri(safe_task)
            self.graph.add((task_uri, RDF.type, self.MLS.Task))
            self.graph.add((task_uri, RDFS.label, Literal(safe_task, datatype=XSD.string)))
        
        # Tags
        for tag in model.tags:
            if isinstance(tag, str) and tag:
                safe_tag = sanitize_string(tag)
                self.graph.add((model_uri, self.DCAT.keyword, Literal(safe_tag, datatype=XSD.string)))
        
        # Popularidad (asegurar que no sean None antes de comparar)
        if model.downloads is not None and model.downloads > 0:
            self.graph.add((model_uri, self.DAIMO.downloads, Literal(model.downloads, datatype=XSD.integer)))
        
        if model.likes is not None and model.likes > 0:
            self.graph.add((model_uri, self.DAIMO.likes, Literal(model.likes, datatype=XSD.integer)))
        
        # Librería/Framework
        library = model.library or model.framework
        if library:
            safe_library = sanitize_string(library)
            self.graph.add((model_uri, self.DAIMO.library, Literal(safe_library, datatype=XSD.string)))
        
        # Arquitecturas
        if model.architectures:
            for arch_name in model.architectures:
                if arch_name:
                    safe_arch = sanitize_string(arch_name)
                    arch_uri = self._create_architecture_uri(safe_arch)
                    self.graph.add((arch_uri, RDF.type, self.DAIMO.ModelArchitecture))
                    self.graph.add((arch_uri, RDFS.label, Literal(safe_arch, datatype=XSD.string)))
                    self.graph.add((model_uri, self.DAIMO.hasArchitecture, arch_uri))
        elif model.model_type:
            safe_type = sanitize_string(model.model_type)
            arch_uri = self._create_architecture_uri(safe_type)
            self.graph.add((arch_uri, RDF.type, self.DAIMO.ModelArchitecture))
            self.graph.add((arch_uri, RDFS.label, Literal(safe_type, datatype=XSD.string)))
            self.graph.add((model_uri, self.DAIMO.hasArchitecture, arch_uri))
        
        # Control de acceso
        if model.gated or model.requires_approval:
            access_uri = self._create_access_policy_uri(model.id)
            self.graph.add((access_uri, RDF.type, self.DAIMO.AccessPolicy))
            self.graph.add((access_uri, RDFS.label, Literal("Access Control Policy", datatype=XSD.string)))
            self.graph.add((model_uri, self.DAIMO.accessControl, access_uri))
            self.graph.add((model_uri, self.DAIMO.requiresApproval, Literal(True, datatype=XSD.boolean)))
        
        # Parámetros
        if model.parameter_count:
            self.graph.add((model_uri, self.DAIMO.parameterCount, Literal(model.parameter_count, datatype=XSD.long)))
        
        # Fine-tuning
        if model.fine_tuned_from or model.base_model:
            base_id = model.fine_tuned_from or f"base_{model.base_model}"
            safe_base_id = sanitize_string(base_id)
            base_uri = self._create_model_uri(safe_base_id)
            self.graph.add((base_uri, RDF.type, self.DAIMO.Model))
            self.graph.add((base_uri, DCTERMS.identifier, Literal(safe_base_id, datatype=XSD.string)))
            if model.base_model:
                safe_base_model = sanitize_string(model.base_model)
                self.graph.add((base_uri, DCTERMS.title, Literal(safe_base_model, datatype=XSD.string)))
            self.graph.add((model_uri, self.DAIMO.fineTunedFrom, base_uri))
        
        # Inference endpoint
        if model.inference_endpoint:
            self.graph.add((model_uri, self.DAIMO.inferenceEndpoint, Literal(model.inference_endpoint, datatype=XSD.anyURI)))
        
        # License (genérico - cada repo puede extender)
        if model.license:
            license_uri = self._create_license_uri(model.license)
            self.graph.add((license_uri, RDF.type, self.ODRL.Offer))
            self.graph.add((license_uri, DCTERMS.identifier, Literal(model.license, datatype=XSD.string)))
            self.graph.add((model_uri, self.ODRL.hasPolicy, license_uri))
        
        # === MAPEO ESPECÍFICO DEL REPOSITORIO ===
        if repository:
            # Delegar al repositorio para que añada triples específicos
            namespaces = {
                'DAIMO': self.DAIMO,
                'MLS': self.MLS,
                'DCAT': self.DCAT,
                'ODRL': self.ODRL,
                'PROV': self.PROV,
                'DCTERMS': DCTERMS,
                'FOAF': FOAF,
                'RDFS': RDFS,
                'XSD': XSD
            }
            repository.map_to_rdf(model, self.graph, namespaces)
        
        return model_uri
    
    def build_from_repositories(self, repositories: List[ModelRepository], limit_per_repo: int = 50) -> int:
        """
        Construye el grafo desde múltiples repositorios.
        
        Args:
            repositories: Lista de repositorios
            limit_per_repo: Límite de modelos por repositorio
        
        Returns:
            Número total de modelos añadidos
        """
        # Registrar repositorios
        for repo in repositories:
            self.add_repository(repo)
        
        # Obtener todos los modelos
        all_models = self.fetch_all_models(limit_per_repo=limit_per_repo)
        
        # Construir grafo
        print(f"\n🔨 Building RDF graph...")
        models_added = 0
        
        for model in all_models:
            try:
                # Encontrar el repositorio de origen
                repo = next((r for r in self.repositories if r.name.lower() == model.source.lower()), None)
                
                # Añadir al grafo
                self.add_standardized_model(model, repository=repo)
                models_added += 1
                
            except Exception as e:
                print(f"⚠️ Error adding model {model.id}: {e}")
                continue
        
        print(f"✅ Graph built: {len(self.graph)} total triples")
        print(f"📊 Models added: {models_added}")
        
        return models_added
    
    def get_statistics(self) -> Dict:
        """Retorna estadísticas del grafo multi-repositorio."""
        stats = {
            "total_triples": len(self.graph),
            "repositories": len(self.repositories),
            "models_by_source": {
                source: len(models)
                for source, models in self.models_by_source.items()
            },
            "repository_stats": [
                repo.get_statistics()
                for repo in self.repositories
            ]
        }
        return stats
