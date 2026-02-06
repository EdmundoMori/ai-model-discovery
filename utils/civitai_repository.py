"""
Conector para repositorio Civitai.

Implementa la interfaz ModelRepository para recolectar modelos de Civitai
(mayormente modelos de difusión/generación de imágenes) y mapearlos a DAIMO.

Mapeos CRÍTICOS específicos de Civitai:
- Base Model (SD 1.5, SDXL, etc.) → daimo:fineTunedFrom (subProperty of prov:wasDerivedFrom)
- triggerWords / generation params → daimo:HyperparameterConfiguration
- nsfw: true → daimo:requiresApproval = True

Autor: Edmundo Mori
Fecha: Enero 2026
"""

from typing import List, Dict, Optional
import requests
from rdflib import Literal, URIRef, RDF, RDFS, XSD, BNode

from .model_repository import ModelRepository, StandardizedModel
from knowledge_graph.multi_repository_builder import sanitize_uri


class CivitaiRepository(ModelRepository):
    """
    Conector para Civitai API.
    
    Civitai se especializa en modelos de difusión (Stable Diffusion, SDXL, etc.)
    y tiene metadatos específicos como base model, trigger words, y clasificación NSFW.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el conector Civitai.
        
        Args:
            api_key: API key de Civitai (opcional para acceso público)
        """
        super().__init__("Civitai")
        self.api_key = api_key
        self.base_url = "https://civitai.com/api/v1"
    
    def fetch_models(self, limit: int = 50, **kwargs) -> List[StandardizedModel]:
        """
        Obtiene modelos de Civitai usando su API pública.
        
        No requiere autenticación para consultas básicas.
        API docs: https://github.com/civitai/civitai/wiki/REST-API-Reference
        
        Args:
            limit: Número máximo de modelos
            **kwargs: Parámetros adicionales (types, sort, period)
        
        Returns:
            Lista de StandardizedModel
        """
        standardized_models = []
        
        try:
            # API pública de Civitai
            params = {
                'limit': min(limit, 100),  # Max 100 por página
                'sort': kwargs.get('sort', 'Highest Rated'),
                'nsfw': 'true'  # Incluir todos los modelos
            }
            
            print(f"📡 Consultando Civitai API...")
            response = requests.get(f"{self.base_url}/models", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            models = data.get('items', [])
            
            for model in models[:limit]:
                # NO usar try-catch - dejar que errores se propaguen
                # Extraer información del modelo
                model_id = model.get('id')
                name = model.get('name', 'Unknown')
                creator = model.get('creator', {})
                stats = model.get('stats', {})
                
                # Obtener la versión más reciente
                versions = model.get('modelVersions', [])
                latest_version = versions[0] if versions else {}
                
                # Base Model (SD 1.5, SDXL, etc.)
                base_model = latest_version.get('baseModel', '')
                
                # Trigger words para el modelo
                trained_words = latest_version.get('trainedWords', [])
                
                # NSFW level
                nsfw = model.get('nsfw', False)
                nsfw_level = model.get('nsfwLevel', 0)
                
                std_model = StandardizedModel(
                    id=f"civitai_{model_id}",
                    source="civitai",
                    title=name,
                    description=model.get('description', ''),
                    author=creator.get('username', 'unknown'),
                    created_at=latest_version.get('createdAt'),
                    last_modified=latest_version.get('updatedAt'),
                    downloads=stats.get('downloadCount', 0),
                    likes=stats.get('favoriteCount', 0),
                    library="diffusers",
                    license="unknown",
                    tags=model.get('tags', []),
                    requires_approval=nsfw or nsfw_level > 1,
                    nsfw=nsfw,
                    trigger_words=trained_words,
                    base_model=base_model,
                    extra_metadata={
                        'url': f"https://civitai.com/models/{model_id}",
                        'civitai_url': f"https://civitai.com/models/{model_id}",
                        'nsfw_level': nsfw_level,
                        'model_type': model.get('type'),
                        'rating': stats.get('rating', 0),
                        'rating_count': stats.get('ratingCount', 0),
                        'poi': model.get('poi', False),
                        'availability': model.get('availability', 'Public'),
                        'cover_image_url': model.get('modelVersions', [{}])[0].get('images', [{}])[0].get('url') if model.get('modelVersions', []) else None
                    }
                )
                
                standardized_models.append(std_model)
            
            print(f"✅ Civitai: {len(standardized_models)} modelos recolectados")
            return standardized_models
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error conectando con Civitai API: {e}")
            print("   Usando datos de ejemplo...")
            return self._get_example_data(limit)
        except Exception as e:
            print(f"⚠️  Error inesperado: {e}")
            print("   Usando datos de ejemplo...")
            return self._get_example_data(limit)
    
    def _get_example_data(self, limit: int) -> List[StandardizedModel]:
        """Genera datos de ejemplo cuando la API no está disponible."""
        standardized_models = []
        
        # Para desarrollo, estructura de ejemplo basada en API de Civitai
        example_civitai_models = [
                {
                    "id": 12345,
                    "name": "Realistic Vision v5.0",
                    "description": "Photorealistic model based on SD 1.5",
                    "type": "Checkpoint",
                    "creator": {"username": "artist123"},
                    "tags": ["realistic", "photography", "portrait"],
                    "stats": {
                        "downloadCount": 125000,
                        "favoriteCount": 8500,
                        "rating": 4.8
                    },
                    "modelVersions": [{
                        "id": 67890,
                        "name": "v5.0",
                        "baseModel": "SD 1.5",  # CRÍTICO: mapea a daimo:fineTunedFrom
                        "trainedWords": ["realistic", "photo", "portrait"],  # CRÍTICO: mapea a HyperparameterConfiguration
                        "files": [{
                            "sizeKB": 2048000,
                            "format": "SafeTensor"
                        }]
                    }],
                    "nsfw": False,  # CRÍTICO: si True → daimo:requiresApproval = True
                    "nsfwLevel": 1
                }
            ]
        
        for civitai_model in example_civitai_models[:limit]:
            try:
                # Obtener versión más reciente
                latest_version = civitai_model["modelVersions"][0] if civitai_model.get("modelVersions") else {}
                
                # MAPEO CRÍTICO: Base Model → fine_tuned_from
                base_model_name = latest_version.get("baseModel")
                if base_model_name:
                    # Normalizar nombre del base model (SD 1.5 → sd_1_5)
                    base_model_id = f"civitai_base_{base_model_name.lower().replace(' ', '_').replace('.', '_')}"
                else:
                    base_model_id = None
                
                # MAPEO CRÍTICO: triggerWords → hyperparameters
                trigger_words = latest_version.get("trainedWords", [])
                hyperparameters = {
                    "trigger_words": trigger_words,
                    "base_model": base_model_name
                } if trigger_words or base_model_name else None
                
                # MAPEO CRÍTICO: nsfw → requires_approval
                is_nsfw = civitai_model.get("nsfw", False) or civitai_model.get("nsfwLevel", 0) > 1
                
                # Estimar parámetros desde tamaño de archivo
                parameter_count = None
                if latest_version.get("files"):
                    file_size_kb = latest_version["files"][0].get("sizeKB", 0)
                    # Estimación aproximada: 2GB ≈ 2B parámetros
                    if file_size_kb > 0:
                        parameter_count = int((file_size_kb / 1024 / 1024) * 1_000_000_000)
                
                std_model = StandardizedModel(
                    id=f"civitai_{civitai_model['id']}",
                    source="civitai",
                    title=civitai_model.get("name"),
                    description=civitai_model.get("description"),
                    author=civitai_model.get("creator", {}).get("username"),
                    
                    # Taxonomía
                    tags=civitai_model.get("tags", []),
                    model_type=civitai_model.get("type"),  # Checkpoint, LoRA, Textual Inversion, etc.
                    
                    # Popularidad
                    downloads=civitai_model.get("stats", {}).get("downloadCount", 0),
                    likes=civitai_model.get("stats", {}).get("favoriteCount", 0),
                    
                    # Técnico
                    library="diffusers",  # Asumimos diffusers para modelos de difusión
                    framework="PyTorch",
                    
                    # MAPEOS CRÍTICOS CIVITAI:
                    # Base Model → fine_tuned_from
                    fine_tuned_from=base_model_id,
                    base_model=base_model_name,
                    
                    # triggerWords → hyperparameters
                    hyperparameters=hyperparameters,
                    trigger_words=trigger_words,
                    
                    # nsfw → requires_approval
                    nsfw=is_nsfw,
                    requires_approval=is_nsfw,
                    
                    # Parámetros
                    parameter_count=parameter_count,
                    
                    # Extra
                    extra_metadata={
                        "civitai_id": civitai_model["id"],
                        "civitai_url": f"https://civitai.com/models/{civitai_model['id']}",
                        "version_id": latest_version.get("id"),
                        "rating": civitai_model.get("stats", {}).get("rating"),
                        "nsfw_level": civitai_model.get("nsfwLevel")
                    }
                )
                
                standardized_models.append(std_model)
                
            except Exception as e:
                print(f"⚠️ Error processing Civitai model {civitai_model.get('id')}: {e}")
                continue
        
        return standardized_models
    
    def map_to_rdf(self, model: StandardizedModel, graph, namespaces: Dict) -> None:
        """
        Mapea metadatos específicos de Civitai a RDF según la ontología DAIMO.
        
        MAPEOS CRÍTICOS Civitai:
        1. Base Model → daimo:fineTunedFrom (subProperty of prov:wasDerivedFrom)
        2. triggerWords → daimo:HyperparameterConfiguration
        3. nsfw: true → daimo:requiresApproval = True
        
        Args:
            model: Modelo estandarizado
            graph: Grafo RDFLib
            namespaces: Dict con DAIMO, PROV, XSD, etc.
        """
        DAIMO = namespaces['DAIMO']
        PROV = namespaces['PROV']
        DCTERMS = namespaces['DCTERMS']
        RDFS = namespaces['RDFS']
        
        # Crear URI del modelo
        model_uri = DAIMO[f"model/{model.id.replace('/', '_')}"]
        
        # MAPEO CRÍTICO 1: Base Model → daimo:fineTunedFrom
        # daimo:fineTunedFrom es subProperty de prov:wasDerivedFrom
        if model.fine_tuned_from:
            base_model_uri = DAIMO[f"model/{model.fine_tuned_from.replace('/', '_')}"]
            
            # Crear el base model como entidad
            graph.add((base_model_uri, RDF.type, DAIMO.Model))
            graph.add((base_model_uri, DCTERMS.identifier, Literal(model.fine_tuned_from, datatype=XSD.string)))
            if model.base_model:
                graph.add((base_model_uri, DCTERMS.title, Literal(model.base_model, datatype=XSD.string)))
            
            # Establecer relación de derivación
            graph.add((model_uri, DAIMO.fineTunedFrom, base_model_uri))
            graph.add((model_uri, PROV.wasDerivedFrom, base_model_uri))
        
        # MAPEO CRÍTICO 2: triggerWords → daimo:HyperparameterConfiguration
        if model.trigger_words or model.hyperparameters:
            config_uri = DAIMO[f"config/{model.id.replace('/', '_')}"]
            
            graph.add((config_uri, RDF.type, DAIMO.HyperparameterConfiguration))
            graph.add((config_uri, RDFS.label, Literal(f"Configuration for {model.title}", datatype=XSD.string)))
            
            # Añadir trigger words como parámetros
            if model.trigger_words:
                for trigger_word in model.trigger_words:
                    graph.add((
                        config_uri,
                        DAIMO.triggerWord,
                        Literal(trigger_word, datatype=XSD.string)
                    ))
            
            # Añadir otros hyperparameters
            if model.hyperparameters and isinstance(model.hyperparameters, dict):
                for key, value in model.hyperparameters.items():
                    param_uri = BNode()
                    graph.add((param_uri, RDF.type, DAIMO.Parameter))
                    graph.add((param_uri, DAIMO.parameterName, Literal(key, datatype=XSD.string)))
                    graph.add((param_uri, DAIMO.parameterValue, Literal(str(value), datatype=XSD.string)))
                    graph.add((config_uri, DAIMO.hasParameter, param_uri))
            
            # Vincular configuración al modelo
            graph.add((model_uri, DAIMO.hasConfiguration, config_uri))
        
        # Rating - Civitai-specific property
        rating = model.extra_metadata.get('rating')
        if rating is not None:
            graph.add((model_uri, DAIMO.rating, Literal(float(rating), datatype=XSD.float)))
        
        # NSFW - Civitai-specific property
        graph.add((model_uri, DAIMO.isNSFW, Literal(model.nsfw, datatype=XSD.boolean)))
        if model.nsfw:
            nsfw_level = model.extra_metadata.get('nsfw_level', 1)
            graph.add((model_uri, DAIMO.nsfwLevel, Literal(nsfw_level, datatype=XSD.integer)))
        
        # POI (Person of Interest) - Civitai-specific property
        poi = model.extra_metadata.get('poi', False)
        graph.add((model_uri, DAIMO.isPOI, Literal(poi, datatype=XSD.boolean)))
        
        # Trigger Words - Civitai-specific property
        if model.trigger_words:
            trigger_words_str = ', '.join(model.trigger_words)
            graph.add((model_uri, DAIMO.triggerWords, Literal(trigger_words_str, datatype=XSD.string)))
        
        # Base Model - Civitai-specific property
        if model.base_model:
            graph.add((model_uri, DAIMO.baseModel, Literal(model.base_model, datatype=XSD.string)))
        
        # REFACTORIZATION: availability → accessLevel (universal property)
        # Civitai availability values map to accessLevel
        if model.extra_metadata.get('availability'):
            availability = model.extra_metadata['availability']
            # Map Civitai availability to standard accessLevel values
            # Civitai uses: "Public", "Private", "Limited", etc.
            access_level = availability.lower()  # Normalize to lowercase
            graph.add((model_uri, DAIMO.accessLevel, Literal(access_level, datatype=XSD.string)))
        
        # Cover Image URL - Civitai-specific property
        if model.extra_metadata.get('cover_image_url'):
            sanitized_cover = sanitize_uri(model.extra_metadata['cover_image_url'])
            graph.add((model_uri, DAIMO.coverImageURL, URIRef(sanitized_cover)))
        
        # Añadir URL de Civitai
        if model.extra_metadata.get('civitai_url'):
            graph.add((model_uri, DAIMO.sourceURL, Literal(model.extra_metadata['civitai_url'], datatype=XSD.anyURI)))
