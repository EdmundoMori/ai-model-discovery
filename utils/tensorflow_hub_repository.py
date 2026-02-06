from typing import List, Dict, Any
from datetime import datetime
from rdflib import Literal
from .model_repository import ModelRepository, StandardizedModel

class TensorFlowHubRepository(ModelRepository):
    """
    Repositorio para TensorFlow Hub (implementado vía Kaggle Models API).
    
    Siguiendo el procedimiento de KaggleRepository, este conector utiliza
    la API oficial de Kaggle pero filtra específicamente modelos del ecosistema
    TensorFlow para mantener la identidad del repositorio original TFHub.
    """
    
    def __init__(self):
        super().__init__("TensorFlow Hub")

    def fetch_models(self, limit: int = 10, sort: str = 'downloads') -> List[StandardizedModel]:
        """
        Obtiene modelos de TensorFlow Hub a través de la API de Kaggle.
        """
        standardized_models = []
        
        try:
            # Reutilizamos la infraestructura de Kaggle existente
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            print(f"🔌 Conectando a TensorFlow Hub (vía Kaggle API)...")
            api = KaggleApi()
            api.authenticate()
            
            # Buscamos específicamente modelos relacionados con TensorFlow
            # Usamos search="tensorflow" para filtrar el catálogo
            models_data = api.model_list(sort_by="hotness", search="tensorflow", page_size=limit)
            
            count = 0
            for model in models_data:
                if count >= limit:
                    break
                
                # Extraer framework e info técnica
                framework = "TensorFlow" # Por defecto
                if hasattr(model, 'instances') and model.instances and len(model.instances) > 0:
                    instance = model.instances[0]
                    fw = getattr(instance, 'framework', None)
                    if fw:
                        framework = fw

                # Mapeo a StandardizedModel
                std_model = StandardizedModel(
                    # Prefijo tfhub_ para diferenciar ID del repo general de Kaggle
                    id=f"tfhub_{model.ref.replace('/', '_')}", 
                    source="TensorFlow Hub",
                    title=model.title or model.ref,
                    description=getattr(model, 'subtitle', '') or getattr(model, 'description', '') or "",
                    author=getattr(model, 'ownerSlug', getattr(model, 'author', 'unknown')),
                    
                    # Fechas
                    created_at=str(getattr(model, 'publish_time', datetime.now().isoformat())),
                    last_modified=str(getattr(model, 'lastUpdated', datetime.now().isoformat())),
                    
                    # Métricas 
                    downloads=getattr(model, 'downloadCount', 0),
                    likes=getattr(model, 'voteCount', 0),
                    
                    # Taxonomía
                    library=framework,
                    tags=getattr(model, 'tags', []) or [],
                    
                    # Metadatos extra 
                    extra_metadata={
                        'modelUrl': f"https://www.kaggle.com/models/{model.ref}",
                        'tfhubHandle': f"https://tfhub.dev/{model.ref}",
                        'moduleType': 'model', 
                        'fineTunable': True,
                        'frameworkVersion': '2.x',
                        'modelFormat': 'SavedModel',
                        'kaggle_ref': model.ref
                    }
                )
                
                standardized_models.append(std_model)
                count += 1
            
            print(f"   ✅ {len(standardized_models)} modelos reales recuperados (filtro TensorFlow)")
            return standardized_models

        except ImportError:
            print("❌ Librería 'kaggle' no instalada. Usando simulación de respaldo.")
            return self._generate_tfhub_models_fallback(limit)
        except Exception as e:
            print(f"⚠️ Error conectando a API (TF Hub): {e}. Usando simulación de respaldo.")
            return self._generate_tfhub_models_fallback(limit)

    def _generate_tfhub_models_fallback(self, limit: int) -> List[StandardizedModel]:
        """Generador de respaldo (Fallback) si falla la conexión real"""
        # Catálogo hardcoded para pruebas offline
        catalog = [
            {
                "name": "google/imagenet/mobilenet_v2_100_224/classification/5",
                "title": "MobileNet V2",
                "publisher": "Google",
                "description": "MobileNet V2 es una familia de redes neuronales para visión artificial eficiente en dispositivos móviles.",
                "tags": ["image-classification", "mobile", "vision"],
                "moduleType": "image-classification",
                "fineTunable": True,
                "frameworkVersion": "2.x",
                "downloads": 150000,
                "likes": 2500,
                "assetURL": "https://storage.googleapis.com/tfhub-modules/google/imagenet/mobilenet_v2_100_224/classification/5.tar.gz"
            },
            {
                "name": "tensorflow/bert_en_uncased_L-12_H-768_A-12/4",
                "title": "BERT (Uncased)",
                "publisher": "TensorFlow",
                "description": "Representaciones bidireccionales de codificador de transformadores (BERT).",
                "tags": ["text-embedding", "transformer", "nlp"],
                "moduleType": "text-embedding",
                "fineTunable": True,
                "frameworkVersion": "2.x",
                "downloads": 450000,
                "likes": 5000,
                "assetURL": "https://storage.googleapis.com/tfhub-modules/tensorflow/bert_en_uncased_L-12_H-768_A-12/4.tar.gz"
            },
             {
                "name": "google/universal-sentence-encoder/4",
                "title": "Universal Sentence Encoder",
                "publisher": "Google",
                "description": "Codifica texto en vectores de alta dimensión para análisis semántico.",
                "tags": ["text-embedding", "sentence-similarity", "nlp"],
                "moduleType": "text-embedding",
                "fineTunable": False,
                "frameworkVersion": "2.x",
                "downloads": 890000,
                "likes": 8200,
                "assetURL": "https://storage.googleapis.com/tfhub-modules/google/universal-sentence-encoder/4.tar.gz"
            },
            {
                "name": "deepmind/gan/stylegan2/1",
                "title": "StyleGAN2",
                "publisher": "DeepMind",
                "description": "Generación de imágenes de alta calidad con redes generativas antagónicas.",
                "tags": ["image-generation", "gan", "creative"],
                "moduleType": "image-generator",
                "fineTunable": False,
                "frameworkVersion": "1.x",
                "downloads": 54000,
                "likes": 1200,
                "assetURL": "https://storage.googleapis.com/tfhub-modules/deepmind/gan/stylegan2/1.tar.gz"
            },
            {
                "name": "google/movenet/singlepose/lightning/4",
                "title": "MoveNet Lightning",
                "publisher": "Google",
                "description": "Detección de poses ultrarrápida y precisa.",
                "tags": ["pose-detection", "video", "mobile"],
                "moduleType": "image-pose-detection",
                "fineTunable": False,
                "frameworkVersion": "2.x",
                "downloads": 120000,
                "likes": 1800,
                "assetURL": "https://storage.googleapis.com/tfhub-modules/google/movenet/singlepose/lightning/4.tar.gz"
            },
             {
                "name": "facebook/wav2vec2-base-960h",
                "title": "Wav2Vec2",
                "publisher": "Facebook",
                "description": "Modelo de reconocimiento automático de voz (ASR).",
                "tags": ["audio", "speech-recognition", "asr"],
                "moduleType": "audio-pitch-extraction",
                "fineTunable": True,
                "frameworkVersion": "2.x",
                "downloads": 75000,
                "likes": 980,
                "assetURL": "https://tfhub.dev/facebook/wav2vec2-base-960h"
            },
            {
                "name": "google/ayamel/1",
                "title": "Ayamel",
                "publisher": "Google",
                "description": "Modelo de traducción automática para lenguas subrepresentadas.",
                "tags": ["text", "translation", "nlp"],
                "moduleType": "text-translation",
                "fineTunable": True,
                "frameworkVersion": "2.x",
                "downloads": 12000,
                "likes": 300,
                "assetURL": "https://storage.googleapis.com/tfhub-modules/google/ayamel/1.tar.gz"
            },
            {
                "name": "mediapipe/face_detection/short_range/1",
                "title": "MediaPipe Face Detection",
                "publisher": "MediaPipe",
                "description": "Detección de rostros ultrarrápida para dispositivos móviles.",
                "tags": ["image", "object-detection", "face"],
                "moduleType": "image-object-detection",
                "fineTunable": False,
                "frameworkVersion": "tflite",
                "downloads": 300000,
                "likes": 3400,
                "assetURL": "https://storage.googleapis.com/tfhub-modules/mediapipe/face_detection/short_range/1.tar.gz"
            },
             {
                "name": "google/esri/1",
                "title": "ESRI Super Resolution",
                "publisher": "Google",
                "description": "Mejora de resolución de imágenes satelitales.",
                "tags": ["image", "super-resolution"],
                "moduleType": "image-super-resolution",
                "fineTunable": False,
                "frameworkVersion": "2.x",
                "downloads": 8000,
                "likes": 150,
                "assetURL": "https://storage.googleapis.com/tfhub-modules/google/esri/1.tar.gz"
            },
            {
                "name": "audioset/vggish/1",
                "title": "VGGish",
                "publisher": "Google",
                "description": "Embeddings de audio para clasificación de eventos sonoros.",
                "tags": ["audio", "feature-vector"],
                "moduleType": "audio-embedding",
                "fineTunable": True,
                "frameworkVersion": "1.x",
                "downloads": 95000,
                "likes": 1100,
                "assetURL": "https://storage.googleapis.com/tfhub-modules/audioset/vggish/1.tar.gz"
            }
        ]
        
        std_models = []
        for model in catalog[:limit]:
            m = StandardizedModel(
                id=model['name'],
                source="TensorFlow Hub",
                title=model['title'],
                description=model['description'],
                tags=model['tags'],
                author=model['publisher'],
                downloads=model['downloads'],
                likes=model['likes'],
                created_at=str(datetime.now().isoformat()),
                extra_metadata={
                    'modelUrl': f"https://tfhub.dev/{model['name']}",
                    'tfhubHandle': model['name'],
                    'moduleType': model['moduleType'],
                    'fineTunable': model['fineTunable'],
                    'frameworkVersion': model['frameworkVersion'],
                    'modelFormat': 'SavedModel',
                    'assetURL': model['assetURL']
                }
            )
            std_models.append(m)
        return std_models

    def map_to_rdf(self, model: StandardizedModel, graph, namespaces: Dict) -> None:
        """Mapeo RDF específico para TensorFlow Hub"""
        DAIMO = namespaces['DAIMO']
        XSD = namespaces['XSD']
        
        # Crear URI del modelo (Misma lógica que MultiRepositoryGraphBuilder)
        safe_id = model.id.replace('/', '_')
        model_uri = DAIMO[f"model/{safe_id}"]
        
        # tfhubHandle -> daimo:tfhubHandle
        if 'tfhubHandle' in model.extra_metadata:
            graph.add((model_uri, DAIMO.tfhubHandle, Literal(model.extra_metadata['tfhubHandle'], datatype=XSD.string)))
            
        # REFACTORIZATION: moduleType → task (universal property)
        if 'moduleType' in model.extra_metadata:
            graph.add((model_uri, DAIMO.task, Literal(model.extra_metadata['moduleType'], datatype=XSD.string)))
            
        # fineTunable -> daimo:fineTunable
        if 'fineTunable' in model.extra_metadata:
            graph.add((model_uri, DAIMO.fineTunable, Literal(model.extra_metadata['fineTunable'], datatype=XSD.boolean)))
            
        # frameworkVersion -> daimo:frameworkVersion
        if 'frameworkVersion' in model.extra_metadata:
            graph.add((model_uri, DAIMO.frameworkVersion, Literal(model.extra_metadata['frameworkVersion'], datatype=XSD.string)))
            
        # modelFormat -> daimo:modelFormat
        if 'modelFormat' in model.extra_metadata:
            graph.add((model_uri, DAIMO.modelFormat, Literal(model.extra_metadata['modelFormat'], datatype=XSD.string)))

    def _map_module_type_to_pipeline(self, module_type: str) -> str:
        """
        DEPRECATED: This method is no longer used after refactorization.
        moduleType is now mapped directly to universal 'task' property.
        Kept for backward compatibility.
        """
        mapping = {
            'image-classification': 'image-classification',
            'text-embedding': 'feature-extraction',
            'image-generator': 'text-to-image',
            'image-pose-detection': 'object-detection',
            'image-object-detection': 'object-detection',
            'text-translation': 'translation',
            'audio-embedding': 'audio-classification'
        }
        return mapping.get(module_type, 'other')
