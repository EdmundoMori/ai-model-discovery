"""
Conector para repositorio PapersWithCode.

Implementa la interfaz ModelRepository para recolectar métodos (modelos/algoritmos)
de PapersWithCode y mapearlos a la ontología DAIMO refactorizada.

PapersWithCode se enfoca en modelos con publicaciones académicas asociadas,
proporcionando metadatos únicos como papers, venues, y citaciones.

Autor: Edmundo Mori
Fecha: Enero 2026
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

from rdflib import Literal, URIRef, RDF, RDFS, XSD

from .model_repository import ModelRepository, StandardizedModel


class PapersWithCodeRepository(ModelRepository):
    """
    Conector para PapersWithCode.
    
    Obtiene datos de métodos (modelos/algoritmos) académicos con sus papers asociados,
    implementaciones en código, y métricas académicas.
    
    Fuentes de datos:
    - pwc-archive/methods: Métodos/modelos con metadata académica
    - pwc-archive/links-between-paper-and-code: Enlaces paper-código
    - pwc-archive/papers-with-abstracts: Papers completos con abstract
    """
    
    def __init__(self):
        super().__init__("PapersWithCode")
        self.logger = logging.getLogger(__name__)
    
    def fetch_models(
        self, 
        limit: int = 50,
        area: Optional[str] = None,
        min_papers: int = 1,
        **kwargs
    ) -> List[StandardizedModel]:
        """
        Obtiene métodos/modelos de PapersWithCode.
        
        Args:
            limit: Número máximo de modelos
            area: Filtrar por área de investigación (Computer Vision, NLP, etc.)
            min_papers: Mínimo número de papers que usan el método
        
        Returns:
            Lista de StandardizedModel con metadata académica
        """
        self.logger.info(f"Fetching up to {limit} methods from PapersWithCode")
        
        standardized_models = []
        
        try:
            # Intentar importar datasets - puede fallar por incompatibilidad NumPy/SciPy
            from datasets import load_dataset
            
            # Cargar dataset de métodos (streaming para eficiencia)
            methods_dataset = load_dataset(
                "pwc-archive/methods",
                split="train",
                streaming=True
            )
            
            # Cargar links para obtener repos de GitHub y frameworks
            links_dataset = load_dataset(
                "pwc-archive/links-between-paper-and-code",
                split="train",
                streaming=True
            )
            
            # Crear índice de links por paper_url para lookup eficiente
            links_by_paper = {}
            self.logger.info("Building paper-code links index...")
            for i, link in enumerate(links_dataset):
                if i >= 10000:  # Limitar carga de links
                    break
                paper_url = link.get('paper_url', '')
                if paper_url:
                    if paper_url not in links_by_paper:
                        links_by_paper[paper_url] = []
                    links_by_paper[paper_url].append(link)
            
            self.logger.info(f"Indexed {len(links_by_paper)} papers with code links")
            
            # Procesar métodos
            count = 0
            processed = 0
            for method in methods_dataset:
                if count >= limit:
                    break
                
                processed += 1
                if processed > limit * 50:  # Safety limit to avoid infinite loop
                    break
                
                # Filtrar spam: nombres con caracteres extraños, emojis, símbolos
                name = method.get('name', '')
                if self._is_spam(name):
                    continue
                
                # Filtrar por número mínimo de papers
                num_papers = method.get('num_papers', 0)
                if num_papers < min_papers:
                    continue
                
                # Filtrar por área si se especifica
                if area:
                    collections = method.get('collections', [])
                    areas = [c.get('area', '').lower() for c in collections if isinstance(c, dict)]
                    if area.lower() not in ' '.join(areas):
                        continue
                
                # Crear StandardizedModel
                try:
                    standardized = self._create_standardized_model(method, links_by_paper)
                    standardized_models.append(standardized)
                    count += 1
                    
                    if count % 10 == 0:
                        self.logger.info(f"Processed {count} methods...")
                        
                except Exception as e:
                    self.logger.warning(f"Error processing method {method.get('name', 'unknown')}: {e}")
                    continue
            
            self.logger.info(f"Successfully fetched {len(standardized_models)} methods")
            
        except Exception as e:
            self.logger.error(f"Error fetching models from PapersWithCode: {e}")
            raise
        
        return standardized_models
    
    def _create_standardized_model(
        self, 
        method: Dict, 
        links_by_paper: Dict
    ) -> StandardizedModel:
        """
        Crea StandardizedModel a partir de datos de método PapersWithCode.
        
        Args:
            method: Datos del método de pwc-archive/methods
            links_by_paper: Índice de links paper-código
        
        Returns:
            StandardizedModel con metadata completa
        """
        # Datos básicos
        name = method.get('name', method.get('full_name', 'Unknown Method'))
        method_url = method.get('url', '')
        
        # Generar ID único basado en URL
        model_id = method_url.split('/')[-1] if method_url else name.lower().replace(' ', '-')
        
        # Paper asociado
        paper = method.get('paper', {})
        if isinstance(paper, dict):
            paper_title = paper.get('title', '')
            paper_url = paper.get('url', '')
        else:
            paper_title = ''
            paper_url = ''
        
        # Buscar links de código para este paper
        github_url = None
        framework = None
        is_official = False
        
        if paper_url and paper_url in links_by_paper:
            links = links_by_paper[paper_url]
            # Priorizar implementaciones oficiales
            official_links = [l for l in links if l.get('is_official', False)]
            if official_links:
                link = official_links[0]
                is_official = True
            elif links:
                link = links[0]
            else:
                link = None
            
            if link:
                github_url = link.get('repo_url', '')
                framework = link.get('framework', 'none')
        
        # Collections (research areas/tasks)
        collections = method.get('collections', [])
        tasks = []
        if collections and isinstance(collections, list):
            for collection in collections:
                if isinstance(collection, dict):
                    area = collection.get('area', '')
                    collection_name = collection.get('collection', '')
                    if area:
                        tasks.append(area)
                    elif collection_name:
                        tasks.append(collection_name)
        
        # Si no hay tasks, intentar extraer del paper o descripción
        if not tasks:
            description = method.get('description', '').lower()
            if 'vision' in description or 'image' in description or 'cnn' in description:
                tasks.append('Computer Vision')
            elif 'language' in description or 'nlp' in description or 'text' in description:
                tasks.append('Natural Language Processing')
            elif 'reinforcement' in description or 'rl' in description:
                tasks.append('Reinforcement Learning')
        
        # Crear StandardizedModel usando campos directos del dataclass
        standardized = StandardizedModel(
            id=model_id,
            title=name,
            description=method.get('description', ''),
            source="PapersWithCode",
            
            # Campos estándar de StandardizedModel
            author=paper_title if paper_title else None,
            task=tasks[0] if tasks else 'Machine Learning',
            library=self._normalize_framework(framework),
            likes=method.get('num_papers', 0),
            paper_url=paper_url if paper_url else method.get('source_url', ''),
            paper_title=paper_title,
            method_name=name,
            
            # Metadata adicional específica de PapersWithCode
            extra_metadata={
                'sourceURL': method_url,  # URL al método en PapersWithCode
                'creator': paper_title if paper_title else 'Unknown',
                'accessLevel': 'official' if is_official else 'community',
                'githubURL': github_url,
                
                # PapersWithCode-specific properties
                'arxivId': self._extract_arxiv_id(method.get('source_url', '')),
                'venue': self._extract_venue(method.get('source_title', '')),
                'yearIntroduced': method.get('introduced_year', None),
                'citationCount': None,  # Not available in current dataset
                'isOfficial': is_official,
                
                # Additional metadata
                'full_name': method.get('full_name', name),
                'source_title': method.get('source_title', ''),
                'collections': collections,
                'num_papers': method.get('num_papers', 0),
            }
        )
        
        return standardized
    
    def _extract_arxiv_id(self, source_url: str) -> Optional[str]:
        """
        Extrae arXiv ID de una URL.
        
        Args:
            source_url: URL del paper (puede ser arXiv)
        
        Returns:
            arXiv ID o None
        """
        if not source_url:
            return None
        
        # Formato típico: https://arxiv.org/abs/1512.03385v2
        if 'arxiv.org' in source_url:
            parts = source_url.split('/')
            if 'abs' in parts or 'pdf' in parts:
                # Obtener ID después de /abs/ o /pdf/
                for i, part in enumerate(parts):
                    if part in ['abs', 'pdf'] and i + 1 < len(parts):
                        arxiv_id = parts[i + 1]
                        # Remover versión (v1, v2, etc.) y extensión
                        arxiv_id = arxiv_id.split('v')[0]
                        arxiv_id = arxiv_id.replace('.pdf', '')
                        return arxiv_id
        
        return None
    
    def _is_spam(self, name: str) -> bool:
        """
        Detecta nombres de métodos spam.
        
        Args:
            name: Nombre del método
        
        Returns:
            True si es spam
        """
        if not name:
            return True
        
        # Spam indicators
        spam_indicators = [
            '[[', ']]', '{{', '}}',  # Markdown/wiki syntax
            '™', '®', '©',  # Trademark symbols
            'phone number', 'customer service', 'contact',  # Customer service spam
            'hotline', 'helpline', 'support number',
            'airline', 'cruise', 'booking', 'refund', 'cancel',  # Travel spam
            'complaint', 'ticket', 'reservation',
            'call now', 'dial', '800-', '1-800', '+1-',  # Phone numbers
            'discord', 'twitter', 'facebook', 'telegram',  # Social media spam
            'wallet', 'crypto', 'bitcoin', 'ethereum',  # Crypto spam
            'settlement', 'cash app', 'robinhood',  # Finance spam
            '¿cómo', '¿cuál', 'como', 'teléfono',  # Spanish customer service
            'expedia', 'qatar', 'american airlines', 'delta',  # Airline names
            'disney', 'carnival', 'princess', 'royal caribbean',  # Cruise names
        ]
        
        name_lower = name.lower()
        for indicator in spam_indicators:
            if indicator in name_lower:
                return True
        
        # Check for excessive punctuation
        punct_count = sum(1 for c in name if not c.isalnum() and c != ' ' and c != '-')
        if len(name) > 0 and punct_count / len(name) > 0.3:
            return True
        
        # Check for phone number patterns
        import re
        if re.search(r'\d{3}[-.]?\d{3}[-.]?\d{4}', name):
            return True
        
        return False
    
    def _extract_arxiv_id_old(self, source_url: str) -> Optional[str]:
        """
        Extrae arXiv ID de una URL (old method - renamed).
        """
        pass
    
    def _extract_venue(self, source_title: str) -> Optional[str]:
        """
        Extrae venue (conferencia/journal) del título del paper.
        
        Args:
            source_title: Título del paper que puede incluir venue
        
        Returns:
            Venue extraído o None
        """
        if not source_title:
            return None
        
        # Venues comunes en títulos
        venues = ['NeurIPS', 'ICLR', 'ICML', 'CVPR', 'ICCV', 'ECCV', 'ACL', 'EMNLP', 
                  'AAAI', 'IJCAI', 'KDD', 'WWW', 'SIGIR', 'NAACL', 'CoNLL']
        
        for venue in venues:
            if venue.lower() in source_title.lower():
                # Extraer año si está presente
                import re
                year_match = re.search(r'(19|20)\d{2}', source_title)
                if year_match:
                    return f"{venue} {year_match.group()}"
                return venue
        
        return None
    
    def _normalize_framework(self, framework: Optional[str]) -> Optional[str]:
        """
        Normaliza nombre de framework a formato estándar.
        
        Args:
            framework: Nombre del framework (puede ser 'none', 'pytorch', etc.)
        
        Returns:
            Nombre normalizado o None
        """
        if not framework or framework == 'none':
            return None
        
        framework_lower = framework.lower()
        
        # Mapeo de nombres comunes
        if 'pytorch' in framework_lower:
            return 'PyTorch'
        elif 'tensorflow' in framework_lower or 'tf' in framework_lower:
            return 'TensorFlow'
        elif 'keras' in framework_lower:
            return 'Keras'
        elif 'jax' in framework_lower:
            return 'JAX'
        elif 'mxnet' in framework_lower:
            return 'MXNet'
        
        return framework.capitalize()
    
    def map_to_rdf(self, model: StandardizedModel, graph, namespaces: dict):
        """
        Mapea StandardizedModel a RDF usando ontología DAIMO refactorizada.
        
        Reutiliza 10 propiedades universales y agrega 6 propiedades específicas
        de PapersWithCode para mantener 0% redundancia.
        
        Args:
            model: StandardizedModel con metadata académica
            graph: RDFLib Graph
            namespaces: Diccionario con namespaces (DAIMO, MLS, etc.)
        """
        DAIMO = namespaces['DAIMO']
        base_uri = str(DAIMO)
        model_uri = URIRef(f"{base_uri}{model.id}")
        
        # Tipo
        graph.add((model_uri, RDF.type, DAIMO.AIModel))
        
        # --- Universal Properties (10) ---
        
        # 1. title (nombre del método)
        if model.title:
            graph.add((model_uri, DAIMO.title, Literal(model.title, datatype=XSD.string)))
        
        # 2. description (descripción del método)
        if model.description:
            graph.add((model_uri, DAIMO.description, Literal(model.description, datatype=XSD.string)))
        
        # 3. source (siempre "PapersWithCode")
        graph.add((model_uri, DAIMO.source, Literal("PapersWithCode", datatype=XSD.string)))
        
        # 4. sourceURL (URL del método en PapersWithCode)
        source_url = model.extra_metadata.get('sourceURL')
        if source_url:
            graph.add((model_uri, DAIMO.sourceURL, Literal(source_url, datatype=XSD.string)))
        
        # 5. creator (autores del paper)
        creator = model.extra_metadata.get('creator') or model.author
        if creator:
            graph.add((model_uri, DAIMO.creator, Literal(creator, datatype=XSD.string)))
        
        # 6. task (área de investigación)
        task = model.task or model.extra_metadata.get('task')
        if task:
            graph.add((model_uri, DAIMO.task, Literal(task, datatype=XSD.string)))
        
        # 7. library (framework usado)
        library = model.library or model.extra_metadata.get('library')
        if library:
            graph.add((model_uri, DAIMO.library, Literal(library, datatype=XSD.string)))
        
        # 8. likes (número de papers que usan el método)
        likes = model.likes
        if likes is not None and likes > 0:
            graph.add((model_uri, DAIMO.likes, Literal(likes, datatype=XSD.integer)))
        
        # 9. accessLevel (official vs community implementation)
        access_level = model.extra_metadata.get('accessLevel')
        if access_level:
            graph.add((model_uri, DAIMO.accessLevel, Literal(access_level, datatype=XSD.string)))
        
        # 10. githubURL (repositorio de código)
        github_url = model.extra_metadata.get('githubURL')
        if github_url:
            graph.add((model_uri, DAIMO.githubURL, Literal(github_url, datatype=XSD.string)))
        
        # --- PapersWithCode-Specific Properties (6) ---
        
        # 1. arxivId (identificador académico único)
        arxiv_id = model.extra_metadata.get('arxivId')
        if arxiv_id:
            graph.add((model_uri, DAIMO.arxivId, Literal(arxiv_id, datatype=XSD.string)))
        
        # 2. paper (URL del paper asociado)
        paper = model.paper_url or model.extra_metadata.get('paper')
        if paper:
            graph.add((model_uri, DAIMO.paper, Literal(paper, datatype=XSD.string)))
        
        # 3. venue (conferencia/journal de publicación)
        venue = model.extra_metadata.get('venue')
        if venue:
            graph.add((model_uri, DAIMO.venue, Literal(venue, datatype=XSD.string)))
        
        # 4. yearIntroduced (año de introducción del método)
        year = model.extra_metadata.get('yearIntroduced')
        if year:
            graph.add((model_uri, DAIMO.yearIntroduced, Literal(year, datatype=XSD.integer)))
        
        # 5. citationCount (número de citaciones)
        citations = model.extra_metadata.get('citationCount')
        if citations is not None:
            graph.add((model_uri, DAIMO.citationCount, Literal(citations, datatype=XSD.integer)))
        
        # 6. isOfficial (implementación oficial del paper)
        is_official = model.extra_metadata.get('isOfficial')
        if is_official is not None:
            graph.add((model_uri, DAIMO.isOfficial, Literal(is_official, datatype=XSD.boolean)))
