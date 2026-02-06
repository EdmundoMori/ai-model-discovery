"""
Utilities para notebooks - Funciones auxiliares reutilizables

Incluye:
- create_test_graph(): Crear grafo RDF de prueba con 70 modelos
- Otras utilidades para notebooks

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD


def create_test_graph() -> Graph:
    """
    Crear grafo RDF de prueba con 70 modelos reales
    
    Returns:
        Graph: Grafo RDF con modelos de 7 repositorios
    """
    g = Graph()
    DAIMO = Namespace("http://purl.org/pionera/daimo#")
    g.bind("daimo", DAIMO)
    
    # 70 modelos reales distribuidos en 7 repositorios (~10 por repositorio)
    models_data = [
        # HuggingFace (10 modelos)
        ("bert-base-uncased", "HuggingFace", "text-classification", "PyTorch", 50000000, 4.8, "public", "nlp"),
        ("gpt2", "HuggingFace", "text-generation", "PyTorch", 45000000, 4.7, "public", "nlp"),
        ("distilbert-base-uncased", "HuggingFace", "question-answering", "PyTorch", 38000000, 4.6, "public", "nlp"),
        ("roberta-base", "HuggingFace", "sentiment-analysis", "PyTorch", 35000000, 4.7, "public", "nlp"),
        ("stable-diffusion-v1-5", "HuggingFace", "text-to-image", "PyTorch", 30000000, 4.9, "public", "computer-vision"),
        ("whisper-large-v2", "HuggingFace", "automatic-speech-recognition", "PyTorch", 25000000, 4.8, "public", "audio"),
        ("clip-vit-base-patch32", "HuggingFace", "zero-shot-image-classification", "PyTorch", 22000000, 4.7, "public", "multimodal"),
        ("t5-base", "HuggingFace", "text2text-generation", "PyTorch", 20000000, 4.6, "public", "nlp"),
        ("bart-large-cnn", "HuggingFace", "summarization", "PyTorch", 18000000, 4.5, "public", "nlp"),
        ("vit-base-patch16-224", "HuggingFace", "image-classification", "PyTorch", 15000000, 4.6, "public", "computer-vision"),
        
        # TensorFlow Hub (10 modelos)
        ("efficientnet-b0", "TensorFlow Hub", "image-classification", "TensorFlow", 28000000, 4.7, "public", "computer-vision"),
        ("mobilenet-v2", "TensorFlow Hub", "image-classification", "TensorFlow", 25000000, 4.5, "public", "computer-vision"),
        ("inception-v3", "TensorFlow Hub", "image-classification", "TensorFlow", 23000000, 4.6, "public", "computer-vision"),
        ("resnet-50", "TensorFlow Hub", "image-classification", "TensorFlow", 22000000, 4.5, "public", "computer-vision"),
        ("universal-sentence-encoder", "TensorFlow Hub", "text-embedding", "TensorFlow", 20000000, 4.8, "public", "nlp"),
        ("bert-en-uncased-L-12-H-768-A-12", "TensorFlow Hub", "text-embedding", "TensorFlow", 18000000, 4.7, "public", "nlp"),
        ("efficientnet-b7", "TensorFlow Hub", "image-classification", "TensorFlow", 15000000, 4.8, "public", "computer-vision"),
        ("nasnet-large", "TensorFlow Hub", "image-classification", "TensorFlow", 12000000, 4.4, "public", "computer-vision"),
        ("elmo", "TensorFlow Hub", "text-embedding", "TensorFlow", 10000000, 4.6, "public", "nlp"),
        ("inception-resnet-v2", "TensorFlow Hub", "image-classification", "TensorFlow", 9000000, 4.5, "public", "computer-vision"),
        
        # PyTorch Hub (10 modelos)
        ("resnet50", "PyTorch Hub", "image-classification", "PyTorch", 32000000, 4.7, "public", "computer-vision"),
        ("resnet101", "PyTorch Hub", "image-classification", "PyTorch", 28000000, 4.6, "public", "computer-vision"),
        ("densenet121", "PyTorch Hub", "image-classification", "PyTorch", 20000000, 4.5, "public", "computer-vision"),
        ("vgg16", "PyTorch Hub", "image-classification", "PyTorch", 18000000, 4.4, "public", "computer-vision"),
        ("squeezenet1_0", "PyTorch Hub", "image-classification", "PyTorch", 15000000, 4.3, "public", "computer-vision"),
        ("alexnet", "PyTorch Hub", "image-classification", "PyTorch", 12000000, 4.2, "public", "computer-vision"),
        ("deeplabv3_resnet101", "PyTorch Hub", "semantic-segmentation", "PyTorch", 10000000, 4.6, "public", "computer-vision"),
        ("maskrcnn_resnet50_fpn", "PyTorch Hub", "instance-segmentation", "PyTorch", 9000000, 4.7, "public", "computer-vision"),
        ("fasterrcnn_resnet50_fpn", "PyTorch Hub", "object-detection", "PyTorch", 8500000, 4.6, "public", "computer-vision"),
        ("retinanet_resnet50_fpn", "PyTorch Hub", "object-detection", "PyTorch", 8000000, 4.5, "public", "computer-vision"),
        
        # Replicate (10 modelos)
        ("stable-diffusion", "Replicate", "text-to-image", "PyTorch", 35000000, 4.9, "public", "computer-vision"),
        ("llama-2-70b-chat", "Replicate", "text-generation", "PyTorch", 30000000, 4.8, "public", "nlp"),
        ("whisper", "Replicate", "speech-to-text", "PyTorch", 25000000, 4.7, "public", "audio"),
        ("musicgen", "Replicate", "text-to-music", "PyTorch", 15000000, 4.6, "public", "audio"),
        ("controlnet", "Replicate", "image-to-image", "PyTorch", 12000000, 4.8, "public", "computer-vision"),
        ("real-esrgan", "Replicate", "image-upscaling", "PyTorch", 10000000, 4.7, "public", "computer-vision"),
        ("blip-2", "Replicate", "image-to-text", "PyTorch", 9000000, 4.6, "public", "multimodal"),
        ("instruct-pix2pix", "Replicate", "image-editing", "PyTorch", 8000000, 4.5, "public", "computer-vision"),
        ("riffusion", "Replicate", "text-to-audio", "PyTorch", 7000000, 4.4, "public", "audio"),
        ("CodeLlama-34b", "Replicate", "code-generation", "PyTorch", 6500000, 4.7, "public", "nlp"),
        
        # Kaggle (10 modelos)
        ("efficientnet-b3", "Kaggle", "image-classification", "TensorFlow", 18000000, 4.6, "public", "computer-vision"),
        ("yolov5s", "Kaggle", "object-detection", "PyTorch", 22000000, 4.7, "public", "computer-vision"),
        ("yolov5m", "Kaggle", "object-detection", "PyTorch", 20000000, 4.6, "public", "computer-vision"),
        ("yolov5l", "Kaggle", "object-detection", "PyTorch", 18000000, 4.7, "public", "computer-vision"),
        ("sentence-transformers", "Kaggle", "text-embedding", "PyTorch", 16000000, 4.8, "public", "nlp"),
        ("xgboost-classifier", "Kaggle", "tabular-classification", "XGBoost", 14000000, 4.5, "public", "tabular"),
        ("lightgbm-classifier", "Kaggle", "tabular-classification", "LightGBM", 13000000, 4.6, "public", "tabular"),
        ("catboost-classifier", "Kaggle", "tabular-classification", "CatBoost", 12000000, 4.7, "public", "tabular"),
        ("fastai-resnet34", "Kaggle", "image-classification", "PyTorch", 10000000, 4.5, "public", "computer-vision"),
        ("prophet-forecasting", "Kaggle", "time-series", "Prophet", 9000000, 4.4, "public", "tabular"),
        
        # PapersWithCode (10 modelos)
        ("llama-2-13b", "PapersWithCode", "text-generation", "PyTorch", 28000000, 4.8, "public", "nlp"),
        ("flan-t5-xxl", "PapersWithCode", "text2text-generation", "PyTorch", 25000000, 4.7, "public", "nlp"),
        ("bloom-7b1", "PapersWithCode", "text-generation", "PyTorch", 20000000, 4.6, "public", "nlp"),
        ("opt-6.7b", "PapersWithCode", "text-generation", "PyTorch", 18000000, 4.5, "public", "nlp"),
        ("swin-transformer-base", "PapersWithCode", "image-classification", "PyTorch", 15000000, 4.7, "public", "computer-vision"),
        ("dino-vitb16", "PapersWithCode", "self-supervised-learning", "PyTorch", 12000000, 4.8, "public", "computer-vision"),
        ("sam-vit-h", "PapersWithCode", "image-segmentation", "PyTorch", 10000000, 4.9, "public", "computer-vision"),
        ("grounding-dino", "PapersWithCode", "object-detection", "PyTorch", 8000000, 4.6, "public", "computer-vision"),
        ("alpaca-7b", "PapersWithCode", "instruction-following", "PyTorch", 7000000, 4.5, "public", "nlp"),
        ("vicuna-13b", "PapersWithCode", "conversational", "PyTorch", 6500000, 4.6, "public", "nlp"),
        
        # GitHub (10 modelos)
        ("yolov8n", "GitHub", "object-detection", "PyTorch", 26000000, 4.8, "public", "computer-vision"),
        ("yolov8s", "GitHub", "object-detection", "PyTorch", 24000000, 4.7, "public", "computer-vision"),
        ("yolov7", "GitHub", "object-detection", "PyTorch", 22000000, 4.6, "public", "computer-vision"),
        ("detectron2-resnet50", "GitHub", "object-detection", "PyTorch", 20000000, 4.7, "public", "computer-vision"),
        ("mmdetection-faster-rcnn", "GitHub", "object-detection", "PyTorch", 18000000, 4.6, "public", "computer-vision"),
        ("pytorch-image-models", "GitHub", "image-classification", "PyTorch", 16000000, 4.8, "public", "computer-vision"),
        ("openai-clip", "GitHub", "zero-shot-classification", "PyTorch", 14000000, 4.9, "public", "multimodal"),
        ("fairseq-transformer", "GitHub", "machine-translation", "PyTorch", 12000000, 4.5, "public", "nlp"),
        ("espnet-asr", "GitHub", "speech-recognition", "PyTorch", 10000000, 4.6, "public", "audio"),
        ("nemo-tts", "GitHub", "text-to-speech", "PyTorch", 9000000, 4.5, "public", "audio"),
    ]
    
    # Agregar modelos al grafo
    for i, (title, source, task, library, downloads, rating, access, domain) in enumerate(models_data, 1):
        model_uri = URIRef(f"http://purl.org/pionera/daimo#model_{i}")
        
        g.add((model_uri, RDF.type, DAIMO.AIModel))
        g.add((model_uri, DAIMO.title, Literal(title, datatype=XSD.string)))
        g.add((model_uri, DAIMO.source, Literal(source, datatype=XSD.string)))
        g.add((model_uri, DAIMO.task, Literal(task, datatype=XSD.string)))
        g.add((model_uri, DAIMO.library, Literal(library, datatype=XSD.string)))
        g.add((model_uri, DAIMO.downloads, Literal(downloads, datatype=XSD.integer)))
        g.add((model_uri, DAIMO.rating, Literal(rating, datatype=XSD.float)))
        g.add((model_uri, DAIMO.accessLevel, Literal(access, datatype=XSD.string)))
        g.add((model_uri, DAIMO.domain, Literal(domain, datatype=XSD.string)))
    
    return g


__all__ = ["create_test_graph"]
