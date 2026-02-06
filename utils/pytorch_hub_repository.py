from typing import List, Dict, Any
from datetime import datetime
import re
import requests
from rdflib import Literal, URIRef, XSD
from .model_repository import ModelRepository, StandardizedModel
from knowledge_graph.multi_repository_builder import sanitize_uri

class PyTorchHubRepository(ModelRepository):
    """
    Conector para PyTorch Hub usando GitHub API.
    Obtiene metadatos parseando hubconf.py SIN ejecutar código Python.
    """
    
    def __init__(self):
        super().__init__("PyTorch Hub")
        # Repositorios oficiales de PyTorch Hub con sus branches
        self.hub_repos = [
            {"repo": "pytorch/vision", "branch": "main"},
            {"repo": "ultralytics/yolov5", "branch": "master"},
            {"repo": "NVIDIA/DeepLearningExamples", "branch": "master", "subpath": "PyTorch/Classification/ConvNets"},
            {"repo": "facebookresearch/pytorchvideo", "branch": "main"},
            {"repo": "huggingface/pytorch-image-models", "branch": "main"}
        ]

    def fetch_models(self, limit: int = 10, sort: str = 'downloads') -> List[StandardizedModel]:
        """
        Obtiene modelos parseando hubconf.py desde GitHub API.
        NO ejecuta código - solo descarga y parsea texto.
        """
        standardized_models = []
        print(f"🔌 Conectando a PyTorch Hub (vía GitHub API - solo metadatos)...")
        
        count = 0
        for repo_info in self.hub_repos:
            if count >= limit:
                break
            
            repo = repo_info["repo"]
            branch = repo_info.get("branch", "main")
            subpath = repo_info.get("subpath", "")
            
            try:
                print(f"   📦 Procesando repositorio: {repo}")
                
                # Construir URL del hubconf.py en GitHub
                if subpath:
                    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{subpath}/hubconf.py"
                else:
                    url = f"https://raw.githubusercontent.com/{repo}/{branch}/hubconf.py"
                
                # Descargar el contenido del archivo (solo texto)
                response = requests.get(url, timeout=10)
                
                if response.status_code != 200:
                    print(f"      ⚠️ No se encontró hubconf.py en {repo}")
                    continue
                
                # Parsear funciones (modelos) sin ejecutar código
                models_found = self._parse_hubconf(response.text)
                
                if not models_found:
                    print(f"      ⚠️ No se encontraron modelos en hubconf.py")
                    continue
                
                # Obtener metadatos del repositorio desde GitHub API
                repo_meta = self._get_repo_metadata_from_github(repo)
                
                models_added = 0
                for model_name, model_info in models_found.items():
                    if count >= limit:
                        break
                    
                    # Inferir tarea desde el nombre del modelo
                    task = self._infer_task_from_name(model_name)
                    
                    # Crear StandardizedModel
                    std_model = StandardizedModel(
                        id=f"pytorch_{repo.replace('/', '_')}_{model_name}",
                        source="PyTorch Hub",
                        title=model_name,
                        description=model_info.get('description', f"Modelo {model_name} del repositorio {repo}"),
                        author=repo.split('/')[0],
                        created_at=str(datetime.now().isoformat()),
                        
                        # Métricas del repositorio
                        downloads=repo_meta.get('downloads', 0),
                        likes=repo_meta.get('stars', 0),
                        
                        # Taxonomía
                        library="PyTorch",
                        framework="PyTorch",
                        task=task,
                        pipeline_tag=task,
                        tags=["pytorch", "hub", repo.split('/')[1]],
                        
                        # Metadatos extra
                        extra_metadata={
                            'hubRepo': repo,
                            'entryPoint': model_name,
                            'modelUrl': f"https://pytorch.org/hub/{repo.replace('/', '_')}_{model_name}",
                            'githubUrl': f"https://github.com/{repo}",
                            'category': model_info.get('category', 'other')
                        }
                    )
                    
                    standardized_models.append(std_model)
                    count += 1
                    models_added += 1
                
                print(f"      ✅ {models_added} modelos encontrados (metadatos desde GitHub)")
                
            except requests.RequestException as e:
                print(f"   ⚠️ Error descargando desde GitHub para {repo}: {e}")
                continue
            except Exception as e:
                print(f"   ⚠️ Error procesando {repo}: {e}")
                continue
        
        if len(standardized_models) == 0:
            print("⚠️ No se pudieron obtener modelos desde GitHub API. Usando fallback...")
            return self._generate_fallback(limit)
        
        print(f"   ✅ {len(standardized_models)} modelos REALES recuperados (sin ejecutar código)")
        return standardized_models

    def _parse_hubconf(self, content: str) -> Dict[str, Dict]:
        """
        Parsea el contenido de hubconf.py para extraer nombres de modelos.
        Busca funciones públicas (def) e importaciones (from ... import).
        Maneja importaciones multi-línea con paréntesis.
        """
        models = {}
        
        # Patrón 1: Funciones definidas directamente: def model_name(...)
        def_pattern = r'^def\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\('
        
        # Patrón 2: Importaciones en una línea: from ... import model1, model2
        import_pattern = r'^from\s+[\w.]+\s+import\s+(.+)'
        
        # Para manejar imports multi-línea con paréntesis
        in_multiline_import = False
        current_import_block = []
        
        for line in content.split('\n'):
            line_stripped = line.strip()
            
            # Buscar funciones definidas
            match = re.match(def_pattern, line_stripped)
            if match:
                func_name = match.group(1)
                
                # Filtrar funciones auxiliares comunes
                if func_name in ['dependencies', 'help', 'list', 'load', '_load']:
                    continue
                
                models[func_name] = {
                    'description': f"PyTorch Hub model: {func_name}",
                    'category': self._infer_category_from_name(func_name)
                }
                continue
            
            # Detectar inicio de import multi-línea
            if 'from' in line_stripped and 'import' in line_stripped and '(' in line_stripped:
                in_multiline_import = True
                # Extraer lo que está después de "import ("
                match = re.search(r'import\s+\(?\s*(.+)', line_stripped)
                if match:
                    current_import_block.append(match.group(1))
                continue
            
            # Continuar recolectando líneas del import multi-línea
            if in_multiline_import:
                current_import_block.append(line_stripped)
                
                # Detectar fin del import multi-línea
                if ')' in line_stripped:
                    in_multiline_import = False
                    
                    # Unir todas las líneas y procesar
                    imports_str = ' '.join(current_import_block)
                    imports_str = imports_str.replace('(', '').replace(')', '').replace('#', '').replace('noqa', '')
                    imports_str = re.sub(r'[A-Z]\d+', '', imports_str)  # Remover códigos como F401, E402
                    
                    # Parsear cada nombre importado
                    for import_item in imports_str.split(','):
                        import_name = import_item.strip()
                        
                        # Filtrar imports auxiliares o privados
                        if not import_name or import_name.startswith('_'):
                            continue
                        if import_name in ['dependencies', 'help', 'list', 'load', 'get_model_weights', 'get_weight']:
                            continue
                        
                        models[import_name] = {
                            'description': f"PyTorch Hub model: {import_name}",
                            'category': self._infer_category_from_name(import_name)
                        }
                    
                    current_import_block = []
                continue
            
            # Buscar importaciones en una sola línea (sin paréntesis)
            match = re.match(import_pattern, line_stripped)
            if match and '(' not in line_stripped:
                imports_str = match.group(1)
                
                # Parsear cada nombre importado
                for import_item in imports_str.split(','):
                    import_name = import_item.strip()
                    
                    # Filtrar imports auxiliares o privados
                    if not import_name or import_name.startswith('_'):
                        continue
                    if import_name in ['dependencies', 'help', 'list', 'load', 'get_model_weights', 'get_weight']:
                        continue
                    
                    models[import_name] = {
                        'description': f"PyTorch Hub model: {import_name}",
                        'category': self._infer_category_from_name(import_name)
                    }
        
        return models
    
    def _get_repo_metadata_from_github(self, repo: str) -> Dict:
        """
        Obtiene metadatos del repositorio desde GitHub API.
        """
        try:
            url = f"https://api.github.com/repos/{repo}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'stars': data.get('stargazers_count', 0),
                    'downloads': data.get('stargazers_count', 0) * 100  # Estimación
                }
        except:
            pass
        
        # Fallback con datos estimados
        estimates = {
            "pytorch/vision": {"stars": 25000, "downloads": 5000000},
            "ultralytics/yolov5": {"stars": 45000, "downloads": 10000000},
            "NVIDIA/DeepLearningExamples": {"stars": 12000, "downloads": 2000000},
            "facebookresearch/pytorchvideo": {"stars": 3000, "downloads": 500000},
            "huggingface/pytorch-image-models": {"stars": 30000, "downloads": 6000000}
        }
        return estimates.get(repo, {"stars": 0, "downloads": 0})
    
    def _infer_category_from_name(self, model_name: str) -> str:
        """Infiere la categoría desde el nombre del modelo"""
        name_lower = model_name.lower()
        
        if any(x in name_lower for x in ['yolo', 'detect', 'fasterrcnn', 'maskrcnn']):
            return 'object-detection'
        elif any(x in name_lower for x in ['resnet', 'vgg', 'efficientnet', 'mobilenet', 'densenet']):
            return 'image-classification'
        elif any(x in name_lower for x in ['segment', 'fcn', 'deeplab']):
            return 'image-segmentation'
        elif any(x in name_lower for x in ['video', 'motion', 'action']):
            return 'video-classification'
        else:
            return 'computer-vision'
    
    def _infer_task_from_name(self, model_name: str) -> str:
        """Infiere la tarea ML desde el nombre del modelo"""
        name_lower = model_name.lower()
        
        if any(x in name_lower for x in ['yolo', 'detect', 'fasterrcnn']):
            return 'object-detection'
        elif any(x in name_lower for x in ['segment', 'fcn', 'deeplab']):
            return 'image-segmentation'
        elif any(x in name_lower for x in ['resnet', 'vgg', 'efficientnet', 'mobilenet']):
            return 'image-classification'
        elif 'video' in name_lower:
            return 'video-classification'
        else:
            return 'image-classification'
    
    def _generate_fallback(self, limit: int) -> List[StandardizedModel]:
        """Datos simulados si falla torch"""
        print("   ⚠️ Usando datos simulados de PyTorch Hub")
        
        catalog = [
            {
                "id": "pytorch_vision_resnet50",
                "title": "ResNet-50",
                "description": "Deep residual network with 50 layers for image classification",
                "author": "pytorch",
                "repo": "pytorch/vision",
                "task": "image-classification",
                "downloads": 5000000,
                "likes": 12000
            },
            {
                "id": "pytorch_vision_efficientnet_b0",
                "title": "EfficientNet-B0",
                "description": "Efficient convolutional neural network",
                "author": "pytorch",
                "repo": "pytorch/vision",
                "task": "image-classification",
                "downloads": 2100000,
                "likes": 8500
            },
            {
                "id": "ultralytics_yolov5_yolov5s",
                "title": "YOLOv5s",
                "description": "Small variant of YOLOv5 for real-time object detection",
                "author": "ultralytics",
                "repo": "ultralytics/yolov5",
                "task": "object-detection",
                "downloads": 10000000,
                "likes": 45000
            },
            {
                "id": "ultralytics_yolov5_yolov5m",
                "title": "YOLOv5m",
                "description": "Medium variant of YOLOv5",
                "author": "ultralytics",
                "repo": "ultralytics/yolov5",
                "task": "object-detection",
                "downloads": 8500000,
                "likes": 45000
            },
            {
                "id": "pytorch_audio_wav2vec2",
                "title": "Wav2Vec2",
                "description": "Self-supervised speech representation learning",
                "author": "pytorch",
                "repo": "pytorch/audio",
                "task": "audio-classification",
                "downloads": 850000,
                "likes": 3200
            }
        ]
        
        results = []
        for model_data in catalog[:limit]:
            results.append(StandardizedModel(
                id=model_data["id"],
                source="PyTorch Hub",
                title=model_data["title"],
                description=model_data["description"],
                author=model_data["author"],
                downloads=model_data["downloads"],
                likes=model_data["likes"],
                library="PyTorch",
                task=model_data["task"],
                tags=["pytorch", "hub"],
                created_at=datetime.now().isoformat(),
                extra_metadata={
                    'hubRepo': model_data["repo"],
                    'modelUrl': f"https://pytorch.org/hub/{model_data['repo'].replace('/', '_')}",
                    'frameworkVersion': '2.10.0'
                }
            ))
        
        return results

    def map_to_rdf(self, model: StandardizedModel, graph, namespaces: Dict) -> None:
        """Mapeo RDF específico para PyTorch Hub"""
        DAIMO = namespaces['DAIMO']
        XSD = namespaces['XSD']
        
        # URI del modelo
        safe_id = model.id.replace('/', '_').replace(' ', '_')
        model_uri = DAIMO[safe_id]
        
        # Mapear propiedades específicas de PyTorch Hub desde extra_metadata
        if model.extra_metadata:
            # hubRepo - Repositorio GitHub del modelo
            if 'hubRepo' in model.extra_metadata and model.extra_metadata['hubRepo']:
                graph.add((model_uri, DAIMO.hubRepo, Literal(model.extra_metadata['hubRepo'], datatype=XSD.string)))
            
            # entryPoint - Función de entrada del modelo en hubconf.py
            if 'entryPoint' in model.extra_metadata and model.extra_metadata['entryPoint']:
                graph.add((model_uri, DAIMO.entryPoint, Literal(model.extra_metadata['entryPoint'], datatype=XSD.string)))
            
            # REFACTORIZATION: githubUrl → githubURL (unified property name)
            if 'githubUrl' in model.extra_metadata and model.extra_metadata['githubUrl']:
                sanitized_github = sanitize_uri(model.extra_metadata['githubUrl'])
                graph.add((model_uri, DAIMO.githubURL, URIRef(sanitized_github)))
            
            # REFACTORIZATION: category → task (universal property)
            if 'category' in model.extra_metadata and model.extra_metadata['category']:
                graph.add((model_uri, DAIMO.task, Literal(model.extra_metadata['category'], datatype=XSD.string)))


