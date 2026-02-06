"""
Conector para repositorio Replicate.

Implementa la interfaz ModelRepository para recolectar modelos de Replicate
y mapearlos a la ontología DAIMO con el mapeo específico:
- run_count → daimo:downloads (métrica de uso real)
- github_url → sd:SourceCode
- paper_url → extra_metadata (para futura integración con Papers)
- latest_version → daimo:hasVersion

Replicate se especializa en:
- Inference endpoints listos para usar
- Modelos de difusión, LLMs, visión, audio
- Métricas de uso real (run_count)

Autor: Edmundo Mori
Fecha: Enero 2026
"""

from typing import List, Dict, Optional
import os
import requests
import time
from datetime import datetime

from rdflib import Literal, URIRef, RDF, RDFS, XSD

from .model_repository import ModelRepository, StandardizedModel
from knowledge_graph.multi_repository_builder import sanitize_uri


class ReplicateRepository(ModelRepository):
    """
    Conector para Replicate API.
    
    Replicate ofrece modelos con inference endpoints y métricas de uso real.
    Requiere autenticación mediante REPLICATE_API_TOKEN.
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Inicializa el conector Replicate.
        
        Args:
            api_token: Token de API de Replicate (opcional, usa variable de entorno)
        """
        super().__init__("Replicate")
        self.api_token = api_token or os.getenv('REPLICATE_API_TOKEN')
        self.base_url = "https://api.replicate.com/v1"
        
        if not self.api_token:
            raise ValueError(
                "REPLICATE_API_TOKEN no configurado. "
                "Configura la variable de entorno o pasa api_token al constructor. "
                "Ver docs/REPLICATE_SETUP.md para instrucciones."
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def fetch_models(
        self, 
        limit: int = 50,
        sort_by: str = "latest_version_created_at",
        sort_direction: str = "desc",
        **kwargs
    ) -> List[StandardizedModel]:
        """
        Obtiene modelos de Replicate usando la API oficial.
        
        Requiere autenticación con REPLICATE_API_TOKEN.
        
        Args:
            limit: Número máximo de modelos (máximo: 100 por página)
            sort_by: Campo de ordenamiento
                - "model_created_at": Por fecha de creación del modelo
                - "latest_version_created_at": Por última versión (default)
            sort_direction: Dirección de ordenamiento ("asc" o "desc")
        
        Returns:
            Lista de StandardizedModel
        
        Raises:
            ValueError: Si el token no está configurado
            requests.HTTPError: Si hay errores de API
        """
        print(f"\n🔁 Conectando a Replicate API...")
        print(f"   Límite: {limit} modelos")
        print(f"   Ordenamiento: {sort_by} ({sort_direction})")
        
        standardized_models = []
        models_fetched = 0
        next_cursor = None
        
        # Replicate usa paginación con cursor
        while models_fetched < limit:
            # Construir URL con parámetros
            url = f"{self.base_url}/models"
            params = {
                "sort_by": sort_by,
                "sort_direction": sort_direction
            }
            
            if next_cursor:
                params["cursor"] = next_cursor
            
            try:
                # Hacer request con retry automático
                response = self._make_request_with_retry(url, params)
                
                if response.status_code != 200:
                    print(f"❌ Error HTTP {response.status_code}: {response.text}")
                    break
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    print("   No hay más modelos disponibles")
                    break
                
                # Procesar cada modelo
                for model_data in results:
                    if models_fetched >= limit:
                        break
                    
                    try:
                        standardized = self._convert_to_standardized(model_data)
                        standardized_models.append(standardized)
                        models_fetched += 1
                        
                        if models_fetched % 10 == 0:
                            print(f"   ✓ {models_fetched}/{limit} modelos procesados...")
                    
                    except Exception as e:
                        # No usar try-catch para ocultar errores
                        # Propagar el error
                        raise
                
                # Verificar si hay más páginas
                next_cursor = data.get('next')
                if not next_cursor or models_fetched >= limit:
                    break
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de conexión: {e}")
                raise
        
        print(f"✅ Total modelos obtenidos de Replicate: {len(standardized_models)}")
        self.models_fetched = len(standardized_models)
        
        return standardized_models
    
    def _make_request_with_retry(
        self, 
        url: str, 
        params: Dict, 
        max_retries: int = 3
    ) -> requests.Response:
        """
        Hace un request con retry automático en caso de rate limiting.
        
        Args:
            url: URL del endpoint
            params: Parámetros de query
            max_retries: Número máximo de reintentos
        
        Returns:
            Response de requests
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                
                # Si es rate limit (429), esperar y reintentar
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    print(f"   ⏱️  Rate limit alcanzado. Esperando {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                
                return response
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"   ⏱️  Timeout. Reintentando ({attempt + 1}/{max_retries})...")
                    time.sleep(2 ** attempt)  # Backoff exponencial
                    continue
                raise
        
        return response
    
    def _convert_to_standardized(self, model_data: Dict) -> StandardizedModel:
        """
        Convierte un modelo de Replicate a StandardizedModel.
        
        Args:
            model_data: Diccionario con datos del modelo de Replicate
        
        Returns:
            StandardizedModel normalizado
        """
        # Extraer información básica
        owner = model_data.get('owner', '')
        name = model_data.get('name', '')
        model_id = f"{owner}/{name}"
        
        # URL del modelo
        url = model_data.get('url', f"https://replicate.com/{model_id}")
        
        # Descripción
        description = model_data.get('description', '')
        
        # Métricas de popularidad
        run_count = model_data.get('run_count', 0)
        
        # GitHub URL (código fuente)
        github_url = model_data.get('github_url')
        
        # Paper URL
        paper_url = model_data.get('paper_url')
        
        # License URL
        license_url = model_data.get('license_url')
        
        # Cover image
        cover_image_url = model_data.get('cover_image_url')
        
        # Visibility (public/private)
        visibility = model_data.get('visibility', 'public')
        private = (visibility != 'public')
        
        # Latest version info
        latest_version = model_data.get('latest_version', {})
        if latest_version:
            created_at = latest_version.get('created_at')
            version_id = latest_version.get('id')
            cog_version = latest_version.get('cog_version')
        else:
            created_at = None
            version_id = None
            cog_version = None
        
        # Default example (si existe)
        default_example = model_data.get('default_example')
        
        # Extraer tags/keywords del modelo
        # Replicate no tiene tags explícitos, usar categorías inferidas
        tags = []
        if description:
            # Inferir tags de palabras clave comunes
            keywords = ['diffusion', 'llm', 'vision', 'audio', 'video', 
                       'stable-diffusion', 'gpt', 'bert', 'clip', 'whisper']
            desc_lower = description.lower()
            for keyword in keywords:
                if keyword in desc_lower:
                    tags.append(keyword)
        
        # Crear StandardizedModel
        return StandardizedModel(
            id=model_id,
            source="replicate",
            title=model_id,  # Replicate usa owner/name como identificador
            description=description,
            author=owner,
            created_at=created_at,
            last_modified=created_at,  # Replicate usa created_at de la última versión
            tags=tags,
            task=None,  # Replicate no tiene taxonomía de tasks
            pipeline_tag=None,
            downloads=run_count,  # run_count es la métrica de uso
            likes=0,  # Replicate no tiene sistema de likes
            library=cog_version,  # Cog version como framework
            framework="cog" if cog_version else None,
            architectures=[],  # No disponible en la API de listado
            model_type=None,
            license=license_url,
            private=private,
            gated=False,  # Replicate no usa gating como HuggingFace
            requires_approval=False,
            nsfw=False,  # No está en la API pública
            base_model=None,
            fine_tuned_from=None,
            config=None,
            hyperparameters=None,
            trigger_words=[],
            eval_results=None,
            benchmarks=None,
            paper_url=paper_url,
            paper_title=None,
            method_name=None,
            algorithm=None,
            inference_endpoint=url,  # URL del modelo en Replicate
            deployment_target="replicate",
            parameter_count=None,  # No disponible en API de listado
            extra_metadata={
                'url': url,
                'github_url': github_url,
                'license_url': license_url,
                'cover_image_url': cover_image_url,
                'visibility': visibility,
                'version_id': version_id,
                'cog_version': cog_version,
                # 'default_example' omitido - contiene paths con espacios que causan errores RDF
                'run_count': run_count
            }
        )
    
    def map_to_rdf(
        self, 
        model: StandardizedModel, 
        graph, 
        namespaces: Dict
    ) -> None:
        """
        Mapea metadatos específicos de Replicate a triples RDF.
        
        Este método añade información ADICIONAL específica de Replicate:
        - GitHub URL → sd:SourceCode
        - Cover image → foaf:depiction
        - Version ID → daimo:versionId
        - Cog version → daimo:cogVersion
        
        El mapeo genérico (title, description, downloads, etc.) se hace
        en MultiRepositoryGraphBuilder.add_standardized_model().
        
        Args:
            model: Modelo estandarizado
            graph: Grafo RDFLib
            namespaces: Diccionario de namespaces (daimo, foaf, sd, etc.)
        """
        DAIMO = namespaces.get('DAIMO')
        SD = namespaces.get('SD')
        FOAF = namespaces.get('FOAF')
        DCTERMS = namespaces.get('DCTERMS')
        
        # Crear URI del modelo
        model_uri = URIRef(f"{DAIMO}model/{model.id.replace('/', '_')}")
        
        # GitHub URL → daimo:githubURL
        github_url = model.extra_metadata.get('github_url')
        if github_url:
            sanitized_github = sanitize_uri(github_url)
            graph.add((model_uri, DAIMO.githubURL, URIRef(sanitized_github)))
        
        # Paper URL → daimo:paperURL
        paper_url = model.extra_metadata.get('paper_url')
        if paper_url:
            sanitized_paper = sanitize_uri(paper_url)
            graph.add((model_uri, DAIMO.paperURL, URIRef(sanitized_paper)))
        
        # License URL → daimo:licenseURL  
        license_url = model.extra_metadata.get('license_url')
        if license_url:
            sanitized_license = sanitize_uri(license_url)
            graph.add((model_uri, DAIMO.licenseURL, URIRef(sanitized_license)))
        
        # Cover image → daimo:coverImageURL
        cover_image = model.extra_metadata.get('cover_image_url')
        if cover_image:
            sanitized_cover = sanitize_uri(cover_image)
            graph.add((model_uri, DAIMO.coverImageURL, URIRef(sanitized_cover)))
        
        # Version ID
        version_id = model.extra_metadata.get('version_id')
        if version_id:
            graph.add((model_uri, DAIMO.versionId, Literal(version_id, datatype=XSD.string)))
        
        # Cog version (framework de Replicate)
        cog_version = model.extra_metadata.get('cog_version')
        if cog_version:
            graph.add((model_uri, DAIMO.cogVersion, Literal(cog_version, datatype=XSD.string)))
        
        # Run count (uso real del modelo)
        run_count = model.extra_metadata.get('run_count')
        if run_count:
            graph.add((model_uri, DAIMO.runCount, Literal(run_count, datatype=XSD.integer)))
        
        # REFACTORIZATION: visibility → accessLevel (universal property)
        # Replicate uses: "public" or "private"
        visibility = model.extra_metadata.get('visibility')
        if visibility:
            # Map visibility directly to accessLevel (values are compatible)
            graph.add((model_uri, DAIMO.accessLevel, Literal(visibility, datatype=XSD.string)))
        
        # Inference endpoint (URL del modelo)
        url = model.extra_metadata.get('url')
        if url:
            sanitized_url = sanitize_uri(url)
            graph.add((model_uri, DAIMO.inferenceEndpoint, URIRef(sanitized_url)))


# Propiedades adicionales para la ontología DAIMO (para referencia)
# Estas deberían añadirse a daimo.ttl:
#
# daimo:versionId rdf:type owl:DatatypeProperty ;
#     rdfs:domain daimo:Model ;
#     rdfs:range xsd:string ;
#     rdfs:label "version ID" ;
#     rdfs:comment "Identificador único de la versión del modelo" .
#
# daimo:cogVersion rdf:type owl:DatatypeProperty ;
#     rdfs:domain daimo:Model ;
#     rdfs:range xsd:string ;
#     rdfs:label "Cog version" ;
#     rdfs:comment "Versión del framework Cog usado por Replicate" .
