"""
Utilidades para recolección de metadatos de modelos de Hugging Face.

Este módulo extrae información de modelos del Hub de Hugging Face y la almacena
en formato JSON para su posterior procesamiento y mapeo a la ontología DAIMO.

Referencia conceptual:
- Hugging Face Hub API: https://huggingface.co/docs/huggingface_hub
- Inspirado en: Macaroni (metadata enrichment) y Google Dataset Search

Autor: Edmundo Mori
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import requests
from tqdm import tqdm
from huggingface_hub import HfApi

try:
    from huggingface_hub import ModelFilter
    HAS_MODEL_FILTER = True
except ImportError:
    HAS_MODEL_FILTER = False


class HuggingFaceCollector:
    """
    Recolector de metadatos de modelos desde Hugging Face Hub.
    
    Extrae información estructurada que luego se mapeará a DAIMO:
    - Nombre y identificador del modelo
    - Tarea (task) y pipeline_tag
    - Licencia
    - Descargas y likes (popularidad)
    - Tags y metadatos adicionales
    """
    
    def __init__(self, output_dir: str = "data/raw"):
        """
        Inicializa el recolector.
        
        Args:
            output_dir: Directorio donde se guardarán los metadatos
        """
        self.api = HfApi()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def collect_models(
        self, 
        limit: int = 100,
        sort: str = "downloads",
        task: Optional[str] = None,
        library: Optional[str] = None
    ) -> List[Dict]:
        """
        Recolecta metadatos de modelos del Hub.
        
        Args:
            limit: Número máximo de modelos a recolectar
            sort: Criterio de ordenamiento (downloads, likes, trending)
            task: Filtrar por tipo de tarea (ej: "text-classification")
            library: Filtrar por librería (ej: "transformers", "pytorch")
            
        Returns:
            Lista de diccionarios con metadatos de modelos
        """
        print(f"🔍 Recolectando hasta {limit} modelos de Hugging Face...")
        
        # Crear filtros (si está disponible ModelFilter)
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
            direction=-1,  # Descendente
            limit=limit
        )
        
        collected_data = []
        
        for model_info in tqdm(list(models), desc="Procesando modelos"):
            try:
                # Obtener información detallada del modelo (requiere llamada adicional)
                detailed_info = self.api.model_info(model_info.id)
                
                # Extraer información básica
                model_data = {
                    # Identificación
                    "id": detailed_info.id,
                    "modelId": detailed_info.modelId,
                    "author": detailed_info.author if hasattr(detailed_info, 'author') else None,
                    "sha": detailed_info.sha if hasattr(detailed_info, 'sha') else None,
                    
                    # Temporal
                    "created_at": str(detailed_info.created_at) if hasattr(detailed_info, 'created_at') else None,
                    "last_modified": str(detailed_info.last_modified) if hasattr(detailed_info, 'last_modified') else None,
                    
                    # Control de acceso (NIVEL 1 - CRÍTICO)
                    "private": detailed_info.private if hasattr(detailed_info, 'private') else False,
                    "disabled": detailed_info.disabled if hasattr(detailed_info, 'disabled') else False,
                    "gated": detailed_info.gated if hasattr(detailed_info, 'gated') else False,
                    
                    # Métricas de popularidad
                    "downloads": detailed_info.downloads if hasattr(detailed_info, 'downloads') else 0,
                    "likes": detailed_info.likes if hasattr(detailed_info, 'likes') else 0,
                    
                    # Taxonomía y clasificación
                    "pipeline_tag": detailed_info.pipeline_tag if hasattr(detailed_info, 'pipeline_tag') else None,
                    "tags": detailed_info.tags if (hasattr(detailed_info, 'tags') and detailed_info.tags) else [],
                    "library_name": detailed_info.library_name if hasattr(detailed_info, 'library_name') else None,
                    
                    # Arquitectura (NIVEL 1 - CRÍTICO)
                    "model_type": None,  # Se extrae de config
                    "architectures": None,  # Se extrae de config
                    
                    # Configuración técnica (NIVEL 2 - IMPORTANTE)
                    "config": detailed_info.config if hasattr(detailed_info, 'config') else None,
                    
                    # Derivación (NIVEL 2 - IMPORTANTE)
                    "base_model": None,  # Se extrae de card_data
                    
                    # Evaluaciones (NIVEL 2 - IMPORTANTE)
                    "eval_results": None,  # Se extrae de card_data
                    "model_index": None,  # Se extrae de card_data
                    
                    # Aplicaciones (NIVEL 2 - IMPORTANTE)
                    "spaces": None,  # Requiere llamada adicional
                    
                    # Parámetros del modelo (NIVEL 1 - CRÍTICO)
                    "safetensors_parameters": None,  # Se extrae de safetensors
                    "safetensors_total": None,
                    
                    # Información del modelo card
                    "card_data": detailed_info.card_data if hasattr(detailed_info, 'card_data') else None,
                    "siblings": [s.rfilename for s in detailed_info.siblings] if (hasattr(detailed_info, 'siblings') and detailed_info.siblings) else [],
                    
                    # Metadatos de recolección
                    "collected_at": datetime.now().isoformat(),
                    "source": "huggingface"
                }
                
                # Intentar extraer información adicional del card_data
                if model_data["card_data"]:
                    card = model_data["card_data"]
                    if isinstance(card, dict):
                        model_data["license"] = card.get("license")
                        model_data["language"] = card.get("language")
                        model_data["datasets"] = card.get("datasets", [])
                        model_data["metrics"] = card.get("metrics", [])
                        
                        # NIVEL 2 - Base model (derivación)
                        model_data["base_model"] = card.get("base_model")
                        
                        # NIVEL 2 - Model index y evaluaciones
                        model_data["model_index"] = card.get("model-index")
                        if model_data["model_index"]:
                            # Extraer resultados de evaluación
                            try:
                                model_idx = model_data["model_index"][0] if isinstance(model_data["model_index"], list) else model_data["model_index"]
                                model_data["eval_results"] = model_idx.get("results", [])
                            except (IndexError, KeyError, TypeError):
                                model_data["eval_results"] = None
                
                # NIVEL 1 - Arquitectura desde config
                if model_data["config"]:
                    config = model_data["config"]
                    if isinstance(config, dict):
                        model_data["model_type"] = config.get("model_type")
                        model_data["architectures"] = config.get("architectures")
                
                # NIVEL 1 - Parámetros desde safetensors
                if model_data["siblings"]:
                    for sibling in model_data["siblings"]:
                        if "model.safetensors.index.json" in sibling:
                            # Intentar obtener metadata de safetensors
                            try:
                                # Buscar info de parámetros en siblings
                                safetensors_files = [s for s in detailed_info.siblings if hasattr(s, 'rfilename') and 'safetensors' in s.rfilename]
                                if safetensors_files:
                                    # Sumar tamaños de archivos safetensors como aproximación
                                    total_params = sum(getattr(sf, 'size', 0) for sf in safetensors_files)
                                    # Aproximación: 1 parámetro ≈ 2-4 bytes (depende de precisión)
                                    model_data["safetensors_total"] = total_params
                                    # Estimación conservadora: float16 = 2 bytes
                                    model_data["safetensors_parameters"] = total_params // 2
                            except Exception:
                                pass
                            break
                
                collected_data.append(model_data)
                
            except Exception as e:
                print(f"⚠️ Error procesando {model_info.id}: {e}")
                continue
        
        print(f"✅ Recolectados {len(collected_data)} modelos exitosamente")
        return collected_data
    
    def save_to_json(self, data: List[Dict], filename: str = "hf_models.json"):
        """
        Guarda los metadatos en formato JSON.
        
        Args:
            data: Lista de diccionarios con metadatos
            filename: Nombre del archivo de salida
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Datos guardados en: {output_path}")
        print(f"📊 Total de modelos: {len(data)}")
        
        # Estadísticas básicas
        tasks = {}
        licenses = {}
        libraries = {}
        
        for model in data:
            # Contar tareas
            task = model.get("pipeline_tag", "unknown")
            tasks[task] = tasks.get(task, 0) + 1
            
            # Contar licencias
            lic = model.get("license", "unknown")
            licenses[lic] = licenses.get(lic, 0) + 1
            
            # Contar librerías
            lib = model.get("library_name", "unknown")
            libraries[lib] = libraries.get(lib, 0) + 1
        
        print("\n📈 Estadísticas:")
        print(f"  Tareas más comunes: {sorted(tasks.items(), key=lambda x: x[1], reverse=True)[:5]}")
        print(f"  Licencias: {sorted(licenses.items(), key=lambda x: x[1], reverse=True)[:5]}")
        print(f"  Librerías: {sorted(libraries.items(), key=lambda x: x[1], reverse=True)[:5]}")
        
        return output_path


def main():
    """Función principal para uso desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Recolectar metadatos de modelos de Hugging Face"
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        default=100,
        help="Número máximo de modelos a recolectar (default: 100)"
    )
    parser.add_argument(
        "--sort",
        type=str,
        default="downloads",
        choices=["downloads", "likes", "trending"],
        help="Criterio de ordenamiento (default: downloads)"
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Filtrar por tipo de tarea (ej: text-classification)"
    )
    parser.add_argument(
        "--library",
        type=str,
        default=None,
        help="Filtrar por librería (ej: transformers, pytorch)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="hf_models.json",
        help="Nombre del archivo de salida (default: hf_models.json)"
    )
    
    args = parser.parse_args()
    
    # Ejecutar recolección
    collector = HuggingFaceCollector()
    models = collector.collect_models(
        limit=args.limit,
        sort=args.sort,
        task=args.task,
        library=args.library
    )
    collector.save_to_json(models, args.output)


if __name__ == "__main__":
    main()
