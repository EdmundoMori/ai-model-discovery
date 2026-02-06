"""
Conector para repositorio HuggingFace Hub.

Implementa la interfaz ModelRepository para recolectar modelos de HuggingFace
y mapearlos a la ontología DAIMO.

Este módulo preserva toda la funcionalidad existente del colector original
pero ahora implementa la interfaz estándar para multi-repositorio.

Autor: Edmundo Mori
Fecha: Enero 2026
"""

from typing import List, Dict, Optional
from datetime import datetime

from huggingface_hub import HfApi
try:
    from huggingface_hub import ModelFilter
    HAS_MODEL_FILTER = True
except ImportError:
    HAS_MODEL_FILTER = False

from rdflib import Literal, URIRef, RDF, RDFS, XSD

from .model_repository import ModelRepository, StandardizedModel
from knowledge_graph.multi_repository_builder import sanitize_uri


class HuggingFaceRepository(ModelRepository):
    """
    Conector para HuggingFace Hub.
    
    Implementa fetch_models() para obtener modelos del Hub y map_to_rdf()
    para mapear metadatos específicos de HF a la ontología DAIMO.
    """
    
    def __init__(self):
        super().__init__("HuggingFace")
        self.api = HfApi()
    
    def fetch_models(
        self, 
        limit: int = 50,
        sort: str = "downloads",
        task: Optional[str] = None,
        library: Optional[str] = None,
        **kwargs
    ) -> List[StandardizedModel]:
        """
        Obtiene modelos de HuggingFace Hub.
        
        Args:
            limit: Número máximo de modelos
            sort: Criterio de ordenamiento (downloads, likes, trending)
            task: Filtrar por tipo de tarea
            library: Filtrar por librería
        
        Returns:
            Lista de StandardizedModel
        """
        # Crear filtros si está disponible ModelFilter
        filters = None
        if HAS_MODEL_FILTER:
            filters = ModelFilter()
            if task:
                filters = ModelFilter(task=task)
            if library:
                filters.library = library
        
        # Obtener lista de modelos
        models = self.api.list_models(
            filter=filters,
            sort=sort,
            direction=-1,
            limit=limit
        )
        
        standardized_models = []
        
        for model_info in models:
            # NO usar try-catch - dejar que errores se propaguen
            # Obtener información detallada
            detailed_info = self.api.model_info(model_info.id)
            
            # Extraer arquitecturas desde config
            architectures = None
            model_type = None
            config = detailed_info.config if hasattr(detailed_info, 'config') else None
            
            if config and isinstance(config, dict):
                model_type = config.get("model_type")
                architectures = config.get("architectures", [])
            
            # Extraer base_model y eval_results desde card_data
            base_model = None
            eval_results = None
            
            if hasattr(detailed_info, 'card_data') and detailed_info.card_data:
                card = detailed_info.card_data
                if isinstance(card, dict):
                    base_model = card.get("base_model")
                    model_index = card.get("model-index")
                    if model_index:
                        try:
                            model_idx = model_index[0] if isinstance(model_index, list) else model_index
                            eval_results = model_idx.get("results", [])
                        except (IndexError, KeyError, TypeError):
                            pass
            
            # Estimar parámetros desde safetensors
            parameter_count = None
            if hasattr(detailed_info, 'siblings') and detailed_info.siblings:
                safetensors_files = [
                    s for s in detailed_info.siblings 
                    if hasattr(s, 'rfilename') and 'safetensors' in s.rfilename
                ]
                if safetensors_files:
                    total_bytes = sum(getattr(sf, 'size', 0) or 0 for sf in safetensors_files)
                    # Estimación: float16 = 2 bytes por parámetro
                    parameter_count = total_bytes // 2 if total_bytes > 0 else None
            
            # Crear StandardizedModel
            std_model = StandardizedModel(
                id=detailed_info.id,
                source="huggingface",
                title=detailed_info.id,
                author=detailed_info.author if hasattr(detailed_info, 'author') else None,
                created_at=str(detailed_info.created_at) if hasattr(detailed_info, 'created_at') else None,
                last_modified=str(detailed_info.last_modified) if hasattr(detailed_info, 'last_modified') else None,
                
                # Taxonomía
                tags=detailed_info.tags if hasattr(detailed_info, 'tags') and detailed_info.tags else [],
                pipeline_tag=detailed_info.pipeline_tag if hasattr(detailed_info, 'pipeline_tag') else None,
                task=detailed_info.pipeline_tag if hasattr(detailed_info, 'pipeline_tag') else None,
                
                # Popularidad (asegurar que no sean None)
                downloads=detailed_info.downloads if hasattr(detailed_info, 'downloads') and detailed_info.downloads is not None else 0,
                likes=detailed_info.likes if hasattr(detailed_info, 'likes') and detailed_info.likes is not None else 0,
                
                # Técnico
                library=detailed_info.library_name if hasattr(detailed_info, 'library_name') else None,
                architectures=architectures if architectures else [],
                model_type=model_type,
                config=config,
                
                # Acceso
                private=detailed_info.private if hasattr(detailed_info, 'private') else False,
                gated=detailed_info.gated if hasattr(detailed_info, 'gated') else False,
                requires_approval=detailed_info.gated if hasattr(detailed_info, 'gated') else False,
                
                # Derivación
                base_model=base_model,
                fine_tuned_from=base_model,
                
                # Evaluaciones
                eval_results=eval_results if eval_results else None,
                
                # Parámetros
                parameter_count=parameter_count,
                
                # Extra
                extra_metadata={
                    "sha": detailed_info.sha if hasattr(detailed_info, 'sha') else None,
                    "disabled": detailed_info.disabled if hasattr(detailed_info, 'disabled') else False,
                    "siblings": [s.rfilename for s in detailed_info.siblings] if hasattr(detailed_info, 'siblings') and detailed_info.siblings else [],
                    "cardData": detailed_info.card_data.to_dict() if hasattr(detailed_info, 'card_data') and detailed_info.card_data and hasattr(detailed_info.card_data, 'to_dict') else None,
                    "safetensors": bool(safetensors_files) if 'safetensors_files' in locals() else False
                }
            )
            
            standardized_models.append(std_model)
        
        return standardized_models
    
    def map_to_rdf(self, model: StandardizedModel, graph, namespaces: Dict) -> None:
        """
        Mapea metadatos específicos de HuggingFace a RDF.
        
        Este método añade triples ADICIONALES específicos de HF que no están
        en el mapeo genérico (como sha, siblings, etc.).
        
        Args:
            model: Modelo estandarizado
            graph: Grafo RDFLib
            namespaces: Dict con DAIMO, MLS, DCAT, etc.
        """
        DAIMO = namespaces['DAIMO']
        DCTERMS = namespaces['DCTERMS']
        
        # Crear URI del modelo
        model_uri = DAIMO[f"model/{model.id.replace('/', '_')}"]
        
        # Añadir SHA si existe
        if model.extra_metadata.get('sha'):
            graph.add((
                model_uri,
                DCTERMS.identifier,
                Literal(model.extra_metadata['sha'], datatype=XSD.string)
            ))
        
        # Pipeline Tag → Universal Task (REFACTORED)
        if model.pipeline_tag:
            graph.add((model_uri, DAIMO.task, Literal(model.pipeline_tag, datatype=XSD.string)))
        
        # Safetensors - formato específico HF
        safetensors_value = model.extra_metadata.get('safetensors', False)
        graph.add((model_uri, DAIMO.safetensors, Literal(safetensors_value, datatype=XSD.boolean)))
        
        # Control de acceso → Universal accessLevel (REFACTORED)
        # Mapear isPrivate y isGated a accessLevel
        if model.gated:
            access_level = "gated"
        elif model.private:
            access_level = "private"
        else:
            access_level = "public"
        graph.add((model_uri, DAIMO.accessLevel, Literal(access_level, datatype=XSD.string)))
        
        # Mantener propiedades legacy para compatibilidad (DEPRECATED)
        graph.add((model_uri, DAIMO.isPrivate, Literal(model.private, datatype=XSD.boolean)))
        graph.add((model_uri, DAIMO.isGated, Literal(model.gated, datatype=XSD.boolean)))
        
        # Card Data (metadata del model card) - NUEVA PROPIEDAD
        if model.extra_metadata.get('cardData'):
            import json
            card_data_str = json.dumps(model.extra_metadata['cardData'])
            graph.add((model_uri, DAIMO.cardData, Literal(card_data_str, datatype=XSD.string)))
        
        # Añadir información de siblings (archivos del modelo)
        siblings = model.extra_metadata.get('siblings', [])
        for sibling in siblings:
            if isinstance(sibling, str):
                # Crear un nodo para el archivo con URI sanitizada
                # URL-encode el nombre del archivo para evitar espacios y caracteres especiales
                from urllib.parse import quote
                safe_model_id = model.id.replace('/', '_')
                safe_sibling = quote(sibling.replace('/', '_'), safe='')
                file_uri = URIRef(f"{DAIMO}file/{safe_model_id}_{safe_sibling}")
                graph.add((file_uri, RDF.type, DAIMO.ModelFile))
                graph.add((file_uri, DCTERMS.title, Literal(sibling, datatype=XSD.string)))
                graph.add((model_uri, DAIMO.hasFile, file_uri))
        
        # Nota: El mapeo básico (arquitectura, parámetros, etc.) se hace en build_graph.py
        # Este método solo añade triples ESPECÍFICOS de HuggingFace
