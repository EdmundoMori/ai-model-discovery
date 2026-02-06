"""
Conector para Azure AI Model Catalog.

Implementa la interfaz ModelRepository para recolectar modelos desplegados
en Azure AI y mapearlos a DAIMO con énfasis en endpoints de inferencia.

Mapeo ESPECÍFICO de Azure AI:
- Service URL / deployment target → daimo:inferenceEndpoint
- Nota: Métricas sociales (likes/downloads) usualmente no disponibles

Autor: Edmundo Mori
Fecha: Enero 2026
"""

from typing import List, Dict, Optional
from rdflib import Literal, URIRef, RDF, RDFS, XSD

from .model_repository import ModelRepository, StandardizedModel


class AzureRepository(ModelRepository):
    """
    Conector para Azure AI Model Catalog.
    
    Azure AI se enfoca en modelos desplegados como servicios en la nube.
    El mapeo principal es a endpoints de inferencia (daimo:inferenceEndpoint).
    """
    
    def __init__(self, subscription_key: Optional[str] = None, endpoint: Optional[str] = None):
        """
        Inicializa el conector Azure AI.
        
        Args:
            subscription_key: Azure subscription key
            endpoint: Azure AI endpoint URL
        """
        super().__init__("Azure AI")
        self.subscription_key = subscription_key
        self.endpoint = endpoint or "https://management.azure.com"
    
    def fetch_models(self, limit: int = 50, **kwargs) -> List[StandardizedModel]:
        """
        Obtiene modelos de Azure AI Model Catalog.
        
        Args:
            limit: Número máximo de modelos
            **kwargs: Parámetros adicionales (resource_group, workspace)
        
        Returns:
            Lista de StandardizedModel
        """
        standardized_models = []
        
        try:
            # TODO: Implementar autenticación con Azure SDK
            # from azure.ai.ml import MLClient
            # from azure.identity import DefaultAzureCredential
            # 
            # credential = DefaultAzureCredential()
            # ml_client = MLClient(
            #     credential=credential,
            #     subscription_id=kwargs.get("subscription_id"),
            #     resource_group_name=kwargs.get("resource_group"),
            #     workspace_name=kwargs.get("workspace")
            # )
            # 
            # azure_models = ml_client.models.list(max_results=limit)
            
            # Para desarrollo, estructura de ejemplo basada en Azure ML
            example_azure_models = [
                {
                    "id": "azureml://registries/azure-openai/models/gpt-4/versions/1",
                    "name": "gpt-4",
                    "version": "1",
                    "description": "GPT-4 deployed on Azure OpenAI Service",
                    "tags": {"task": "text-generation", "framework": "openai"},
                    "properties": {
                        "model_type": "gpt-4",
                        "endpoint": "https://myresource.openai.azure.com/openai/deployments/gpt-4",
                        "deployment_target": "Azure OpenAI Service",
                        "region": "eastus"
                    }
                }
            ]
            
            for azure_model in example_azure_models[:limit]:
                try:
                    properties = azure_model.get("properties", {})
                    tags = azure_model.get("tags", {})
                    
                    std_model = StandardizedModel(
                        id=f"azure_{azure_model['name']}_{azure_model.get('version', '1')}".replace('/', '_').replace('-', '_'),
                        source="azure",
                        title=azure_model.get("name"),
                        description=azure_model.get("description"),
                        
                        # Taxonomía
                        tags=list(tags.keys()) if isinstance(tags, dict) else [],
                        task=tags.get("task") if isinstance(tags, dict) else None,
                        model_type=properties.get("model_type"),
                        
                        # Técnico
                        library=tags.get("framework") if isinstance(tags, dict) else None,
                        framework=tags.get("framework") if isinstance(tags, dict) else None,
                        
                        # MAPEO CRÍTICO AZURE: endpoint → inferenceEndpoint
                        inference_endpoint=properties.get("endpoint"),
                        deployment_target=properties.get("deployment_target"),
                        
                        # Popularidad: NO DISPONIBLE en Azure AI
                        # Dejamos en 0 como se solicitó (no forzar datos fake)
                        downloads=0,
                        likes=0,
                        
                        # Extra
                        extra_metadata={
                            "azure_id": azure_model.get("id"),
                            "azure_version": azure_model.get("version"),
                            "azure_region": properties.get("region"),
                            "deployment_target": properties.get("deployment_target")
                        }
                    )
                    
                    standardized_models.append(std_model)
                    
                except Exception as e:
                    print(f"⚠️ Error processing Azure model {azure_model.get('name')}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error connecting to Azure AI: {e}")
            print("💡 Tip: Install Azure ML SDK: pip install azure-ai-ml azure-identity")
            print("   Configure: az login")
            raise
        
        return standardized_models
    
    def map_to_rdf(self, model: StandardizedModel, graph, namespaces: Dict) -> None:
        """
        Mapea metadatos específicos de Azure AI a RDF.
        
        MAPEO CRÍTICO Azure:
        - Service URL / deployment target → daimo:inferenceEndpoint
        
        Nota: Azure AI es parcial ya que se enfoca en servicios cloud.
        No tiene métricas sociales (likes/downloads), lo cual es esperado.
        
        Args:
            model: Modelo estandarizado
            graph: Grafo RDFLib
            namespaces: Dict con DAIMO, DCTERMS, etc.
        """
        DAIMO = namespaces['DAIMO']
        DCTERMS = namespaces['DCTERMS']
        RDFS = namespaces['RDFS']
        
        # Crear URI del modelo
        model_uri = DAIMO[f"model/{model.id.replace('/', '_')}"]
        
        # MAPEO CRÍTICO: inference_endpoint → daimo:inferenceEndpoint
        # (Ya se mapea en el builder genérico, pero añadimos metadata adicional)
        if model.inference_endpoint:
            # Crear un nodo para el endpoint
            endpoint_uri = DAIMO[f"endpoint/{model.id.replace('/', '_')}"]
            
            graph.add((endpoint_uri, RDF.type, DAIMO.InferenceEndpoint))
            graph.add((endpoint_uri, DAIMO.url, Literal(model.inference_endpoint, datatype=XSD.anyURI)))
            graph.add((endpoint_uri, RDFS.label, Literal(f"Endpoint for {model.title}", datatype=XSD.string)))
            
            # Vincular endpoint al modelo
            graph.add((model_uri, DAIMO.inferenceEndpoint, endpoint_uri))
        
        # Añadir deployment target
        if model.deployment_target:
            graph.add((
                model_uri,
                DAIMO.deploymentTarget,
                Literal(model.deployment_target, datatype=XSD.string)
            ))
        
        # Añadir región de Azure si está disponible
        if model.extra_metadata.get('azure_region'):
            graph.add((
                model_uri,
                DAIMO.deploymentRegion,
                Literal(model.extra_metadata['azure_region'], datatype=XSD.string)
            ))
        
        # Añadir ID de Azure
        if model.extra_metadata.get('azure_id'):
            graph.add((
                model_uri,
                DCTERMS.identifier,
                Literal(model.extra_metadata['azure_id'], datatype=XSD.string)
            ))
        
        # Añadir versión
        if model.extra_metadata.get('azure_version'):
            graph.add((
                model_uri,
                DAIMO.version,
                Literal(model.extra_metadata['azure_version'], datatype=XSD.string)
            ))
        
        # NOTA IMPORTANTE: 
        # Azure AI NO tiene métricas sociales (downloads/likes).
        # Esto es correcto y esperado para servicios cloud.
        # NO forzamos datos fake como se solicitó en las instrucciones.
