"""
Conector para repositorio Kaggle Models.

Implementa la interfaz ModelRepository para recolectar modelos de Kaggle
y mapearlos a la ontología DAIMO con el mapeo específico:
- upvotes/votes → daimo:likes
- downloadCount → daimo:downloads  
- framework → daimo:library
- license → odrl:Policy

Autor: Edmundo Mori
Fecha: Enero 2026
"""

from typing import List, Dict, Optional
import requests
from rdflib import Literal, URIRef, RDF, RDFS, XSD

from .model_repository import ModelRepository, StandardizedModel


class KaggleRepository(ModelRepository):
    """
    Conector para Kaggle Models API.
    
    Kaggle ofrece modelos de ML especialmente en PyTorch, TensorFlow y otros frameworks.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el conector Kaggle.
        
        Args:
            api_key: API key de Kaggle (opcional, puede usar credenciales del sistema)
        """
        super().__init__("Kaggle")
        self.api_key = api_key
        self.base_url = "https://www.kaggle.com/api/v1"
    
    def fetch_models(self, limit: int = 50, **kwargs) -> List[StandardizedModel]:
        """
        Obtiene modelos de Kaggle usando la API oficial.
        
        Requiere autenticación:
        - Opción 1: Archivo ~/.kaggle/kaggle.json con {"username": "...", "key": "..."}
        - Opción 2: Variables de entorno KAGGLE_USERNAME y KAGGLE_KEY
        
        Args:
            limit: Número máximo de modelos
        
        Returns:
            Lista de StandardizedModel
        """
        standardized_models = []
        
        try:
            # Intentar importar kaggle SDK
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            api = KaggleApi()
            api.authenticate()
            
            print(f"🔑 Autenticado en Kaggle API")
            
            # Listar modelos (API de Kaggle Models)
            # La API soporta: sort_by, search, owner, page_size, page_token
            try:
                # Usar page_size para obtener el número deseado de modelos
                models_data = api.model_list(page_size=limit)
                
                # Imprimir información de paginación si está disponible
                if hasattr(models_data, 'next_page_token') and models_data.next_page_token:
                    print(f"Next Page Token = {models_data.next_page_token}")
            except Exception as e:
                print(f"⚠️  API model_list() no disponible: {e}")
                models_data = []
            
            count = 0
            for model in models_data:
                if count >= limit:
                    break
                
                # NO usar try-catch - dejar que errores se propaguen
                # Obtener información del modelo
                # ApiModel tiene: id, ref, title, subtitle, author, slug, is_private, 
                # description, instances, tags, publish_time, url
                
                # Extraer framework de la primera instancia
                framework = None
                license_name = None
                if model.instances and len(model.instances) > 0:
                    instance = model.instances[0]
                    framework = getattr(instance, 'framework', 'unknown')
                    license_name = getattr(instance, 'license_name', 'unknown')
                
                std_model = StandardizedModel(
                    id=f"kaggle_{model.ref.replace('/', '_')}",
                    source="kaggle",
                    title=model.title or model.ref,
                    description=model.description or model.subtitle or "",
                    author=model.author or "unknown",
                    created_at=model.publish_time,  # Puede ser None
                    last_modified=model.publish_time,  # Kaggle no tiene lastUpdated en API
                    downloads=0,  # No disponible en ApiModel
                    likes=0,  # No disponible en ApiModel
                    library=framework or "unknown",
                    license=license_name or "unknown",
                    tags=model.tags or [],
                    private=model.is_private,
                    extra_metadata={
                        'url': model.url,
                        'kaggle_ref': model.ref,
                        'kaggle_slug': model.slug,
                        'framework': framework,
                        'is_private': model.is_private,
                        'instances_count': len(model.instances) if model.instances else 0,
                        'subtitle': model.subtitle if hasattr(model, 'subtitle') else None,
                        'licenseName': license_name
                    }
                )
                
                standardized_models.append(std_model)
                count += 1
            
            print(f"✅ Kaggle: {len(standardized_models)} modelos recolectados")
            return standardized_models
            
        except ImportError:
            print("⚠️  Kaggle SDK no instalado. Instalar con: pip install kaggle")
            print("   Usando datos de ejemplo...")
            return self._get_example_data(limit)
        except Exception as e:
            print(f"⚠️  Error con Kaggle API: {e}")
            print("   Usando datos de ejemplo...")
            return self._get_example_data(limit)
    
    def _get_example_data(self, limit: int) -> List[StandardizedModel]:
        """Genera datos de ejemplo cuando la API no está disponible."""
        standardized_models = []
        
        try:
            # TODO: Implementar autenticación con Kaggle API
            # from kaggle.api.kaggle_api_extended import KaggleApi
            # api = KaggleApi()
            # api.authenticate()
            
            # TODO: Llamar a Kaggle API para obtener modelos
            # Por ahora, estructura de ejemplo basada en la documentación de Kaggle
            
            # EJEMPLO de cómo sería la estructura de datos de Kaggle:
            # kaggle_models = api.models_list(page_size=limit, sort_by="hotness")
            
            # Para desarrollo, generamos datos de ejemplo variados
            frameworks = ["PyTorch", "TensorFlow", "Keras", "JAX", "scikit-learn"]
            tasks = ["nlp", "computer-vision", "audio", "tabular", "time-series"]
            licenses = ["apache-2.0", "mit", "bsd-3-clause", "gpl-3.0", "cc-by-4.0"]
            
            example_kaggle_models = []
            for i in range(min(limit, 70)):
                model_num = i + 1
                task = tasks[i % len(tasks)]
                framework = frameworks[i % len(frameworks)]
                
                example_kaggle_models.append({
                    "ref": f"kaggle/{task}/model_{model_num}",
                    "title": f"Kaggle {task.upper()} Model {model_num}",
                    "author": f"kaggle_user_{(i % 20) + 1}",
                    "framework": framework,
                    "license": licenses[i % len(licenses)],
                    "upvotes": 500 + (i * 10),
                    "downloadCount": 10000 + (i * 500),
                    "tags": [task, framework.lower(), f"model-{model_num}"],
                    "lastUpdated": f"2025-{(i % 12) + 1:02d}-15T10:30:00Z",
                    "description": f"Kaggle example model for {task} task using {framework}"
                })
            
            for kaggle_model in example_kaggle_models[:limit]:
                try:
                    std_model = StandardizedModel(
                        id=f"kaggle_{kaggle_model['ref'].replace('/', '_')}",
                        source="kaggle",
                        title=kaggle_model.get("title", kaggle_model["ref"]),
                        description=kaggle_model.get("description"),
                        author=kaggle_model.get("author"),
                        last_modified=kaggle_model.get("lastUpdated"),
                        
                        # Taxonomía
                        tags=kaggle_model.get("tags", []),
                        task=kaggle_model.get("task"),  # Puede inferirse de tags
                        
                        # MAPEO ESPECÍFICO KAGGLE:
                        # upvotes → daimo:likes
                        likes=kaggle_model.get("upvotes", 0),
                        # downloadCount → daimo:downloads
                        downloads=kaggle_model.get("downloadCount", 0),
                        # framework → daimo:library
                        library=kaggle_model.get("framework"),
                        framework=kaggle_model.get("framework"),
                        
                        # Acceso
                        # license → odrl:Policy (se mapea en map_to_rdf)
                        license=kaggle_model.get("license"),
                        
                        # Extra
                        extra_metadata={
                            "kaggle_ref": kaggle_model.get("ref"),
                            "kaggle_url": f"https://www.kaggle.com/models/{kaggle_model.get('ref')}"
                        }
                    )
                    
                    standardized_models.append(std_model)
                    
                except Exception as e:
                    print(f"⚠️ Error processing Kaggle model {kaggle_model.get('ref')}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error connecting to Kaggle API: {e}")
            print("💡 Tip: Make sure you have kaggle API credentials configured")
            print("   Run: pip install kaggle && kaggle configure")
            raise
        
        return standardized_models
    
    def map_to_rdf(self, model: StandardizedModel, graph, namespaces: Dict) -> None:
        """
        Mapea metadatos específicos de Kaggle a RDF según la ontología DAIMO.
        
        Mapeos específicos:
        - upvotes → daimo:likes (ya en StandardizedModel)
        - downloadCount → daimo:downloads (ya en StandardizedModel)
        - framework → daimo:library (ya en StandardizedModel via universal property)
        - license → odrl:Policy (SE MAPEA AQUÍ)
        
        Args:
            model: Modelo estandarizado
            graph: Grafo RDFLib
            namespaces: Dict con DAIMO, ODRL, DCTERMS, etc.
        """
        DAIMO = namespaces['DAIMO']
        ODRL = namespaces['ODRL']
        DCTERMS = namespaces['DCTERMS']
        
        # Crear URI del modelo
        model_uri = DAIMO[f"model/{model.id.replace('/', '_')}"]
        
        # REFACTORIZATION: voteCount removed - use universal "likes" property from StandardizedModel
        # (already mapped by base class)
        
        # REFACTORIZATION: usabilityRating removed - use universal "rating" property
        # Note: Kaggle usabilityRating is 0-1, rating is typically 0-5
        # Map usabilityRating to rating by scaling: rating = usabilityRating * 5
        if model.extra_metadata.get('usabilityRating'):
            # If model.rating is not already set, compute from usabilityRating
            rating_value = model.extra_metadata['usabilityRating'] * 5.0
            graph.add((model_uri, DAIMO.rating, Literal(rating_value, datatype=XSD.float)))
        
        # REFACTORIZATION: framework removed - use universal "library" property from StandardizedModel
        # (already mapped by base class)
        
        # REFACTORIZATION: subtitle removed - redundant with description
        # Kaggle subtitle is just a shorter description, which is already captured in description field
        
        # License Name - KAGGLE-SPECIFIC PROPIEDAD
        if model.extra_metadata.get('licenseName'):
            graph.add((model_uri, DAIMO.licenseName, Literal(model.extra_metadata['licenseName'], datatype=XSD.string)))
        
        # MAPEO CRÍTICO: License → odrl:Policy
        if model.license:
            license_uri = DAIMO[f"license/{model.license.replace(' ', '_').replace('-', '_')}"]
            graph.add((license_uri, RDF.type, ODRL.Policy))
            graph.add((license_uri, RDF.type, ODRL.Offer))
            graph.add((license_uri, DCTERMS.identifier, Literal(model.license, datatype=XSD.string)))
            graph.add((license_uri, RDFS.label, Literal(f"Kaggle License: {model.license}", datatype=XSD.string)))
            graph.add((model_uri, ODRL.hasPolicy, license_uri))
        
        # Añadir URL de Kaggle
        if model.extra_metadata.get('kaggle_url'):
            graph.add((
                model_uri,
                DAIMO.sourceURL,
                Literal(model.extra_metadata['kaggle_url'], datatype=XSD.anyURI)
            ))
        
        # Añadir referencia de Kaggle
        if model.extra_metadata.get('kaggle_ref'):
            graph.add((
                model_uri,
                DCTERMS.identifier,
                Literal(model.extra_metadata['kaggle_ref'], datatype=XSD.string)
            ))
        
        # Nota: downloads, likes, library ya se mapean en el builder genérico
        # Solo añadimos triples ESPECÍFICOS de Kaggle aquí
