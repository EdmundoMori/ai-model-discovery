"""
Ontology-Enhanced BM25 for AI Model Discovery

Enhancement: Leverages ontology structure and domain knowledge to improve BM25 with:
1. Query expansion (semantic term variations)
2. Synonym normalization
3. Property-weighted scoring
4. Structured field boosting

This enhanced version is ONLY used in the hybrid Method1 Enhanced pipeline.
The baseline BM25 remains unchanged for comparison purposes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
import math
import re

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import DCTERMS, DCAT, FOAF, RDFS

try:
    from rdflib.namespace import ODRL
except ImportError:
    ODRL = Namespace("http://www.w3.org/ns/odrl/2/")


# Domain-specific synonym expansions for AI/ML queries
QUERY_EXPANSIONS = {
    # Programming libraries/frameworks
    "pytorch": ["pytorch", "torch", "pt"],
    "tensorflow": ["tensorflow", "tf", "keras"],
    "transformers": ["transformers", "transformer", "huggingface", "hf"],
    "scikit": ["scikit", "sklearn", "scikit-learn"],
    "jax": ["jax", "flax"],
    
    # Tasks - Computer Vision
    "image classification": ["image-classification", "image classification", "computer vision", "cv", "vision"],
    "object detection": ["object-detection", "object detection", "detection", "yolo", "rcnn"],
    "segmentation": ["segmentation", "semantic-segmentation", "instance-segmentation", "image-segmentation"],
    "image generation": ["image-generation", "text-to-image", "image generation", "diffusion", "gan"],
    
    # Tasks - NLP
    "nlp": ["nlp", "natural language", "text", "language"],
    "text classification": ["text-classification", "text classification", "sentiment", "classification"],
    "text generation": ["text-generation", "text generation", "language-modeling", "generation"],
    "translation": ["translation", "text-translation", "machine-translation"],
    "question answering": ["question-answering", "question answering", "qa", "squad"],
    "summarization": ["summarization", "text-summarization", "abstractive", "extractive"],
    
    # Tasks - Audio
    "audio": ["audio", "speech", "sound"],
    "speech recognition": ["speech-recognition", "asr", "automatic-speech-recognition", "speech-to-text"],
    
    # Tasks - Multimodal
    "multimodal": ["multimodal", "vision-language", "image-text"],
    
    # Model types
    "cnn": ["cnn", "convolutional", "convnet"],
    "rnn": ["rnn", "recurrent", "lstm", "gru"],
    "transformer": ["transformer", "attention", "bert", "gpt"],
    
    # General ML terms
    "deep learning": ["deep-learning", "deep learning", "dl", "neural network", "neural-network"],
    "machine learning": ["machine-learning", "machine learning", "ml"],
    "pretrained": ["pretrained", "pre-trained", "finetuned", "fine-tuned"],
}

# Normalize common abbreviations
ABBREVIATION_EXPANSIONS = {
    "dl": ["deep learning", "deep-learning"],
    "ml": ["machine learning", "machine-learning"],
    "cv": ["computer vision", "computer-vision"],
    "nlp": ["natural language processing", "natural-language-processing"],
    "asr": ["automatic speech recognition", "speech recognition"],
    "qa": ["question answering", "question-answering"],
    "gan": ["generative adversarial network"],
    "vae": ["variational autoencoder"],
    "bert": ["bert", "bidirectional encoder representations"],
    "gpt": ["gpt", "generative pre-trained transformer"],
}

# Property weights (higher = more important)
PROPERTY_WEIGHTS = {
    # Highly structured, precise fields
    URIRef("http://purl.org/pionera/daimo#task"): 3.0,
    URIRef("http://purl.org/pionera/daimo#library"): 3.0,
    URIRef("http://purl.org/pionera/daimo#framework"): 2.5,
    DCAT.keyword: 2.5,
    
    # Moderately important
    DCTERMS.title: 2.0,
    FOAF.name: 2.0,
    RDFS.label: 2.0,
    DCTERMS.identifier: 1.5,
    
    # Less precise (can contain noise)
    DCTERMS.description: 1.0,
    DCTERMS.subject: 1.0,
    
    # Metadata
    DCTERMS.source: 0.8,
    DCTERMS.creator: 0.8,
}


@dataclass
class SearchResult:
    model_uri: str
    score: float
    matched_terms: Optional[Set[str]] = None  # For debugging


class OntologyEnhancedBM25:
    """
    BM25 with ontology-based enhancements for semantic search over AI models.
    
    Enhancements:
    1. Query expansion using domain knowledge
    2. Abbreviation normalization  
    3. Property-weighted scoring (structured fields > descriptions)
    4. Structured field boosting (exact matches in task/library)
    """
    
    def __init__(
        self,
        graph_path: Path,
        k1: float = 1.5,
        b: float = 0.75,
        min_token_len: int = 2,
        enable_query_expansion: bool = True,
        enable_property_weighting: bool = True,
        structured_boost: float = 1.5,
    ):
        """
        Args:
            graph_path: Path to RDF graph (Turtle format)
            k1: BM25 parameter (term frequency saturation)
            b: BM25 parameter (length normalization)
            min_token_len: Minimum token length to index
            enable_query_expansion: Enable semantic query expansion
            enable_property_weighting: Enable property-specific weights
            structured_boost: Boost factor for structured field exact matches
        """
        self.graph = Graph()
        self.graph.parse(str(graph_path), format="turtle")
        self.DAIMO = Namespace("http://purl.org/pionera/daimo#")

        self.k1 = k1
        self.b = b
        self.min_token_len = min_token_len
        self.enable_query_expansion = enable_query_expansion
        self.enable_property_weighting = enable_property_weighting
        self.structured_boost = structured_boost

        # Index structures
        self._doc_tokens: Dict[str, List[str]] = {}
        self._doc_len: Dict[str, int] = {}
        self._doc_tf: Dict[str, Dict[str, int]] = {}
        self._doc_property_terms: Dict[str, Dict[str, Set[str]]] = {}  # doc -> property -> terms
        self._df: Dict[str, int] = {}
        self._idf: Dict[str, float] = {}
        self._inverted: Dict[str, List[Tuple[str, int, str]]] = {}  # term -> [(doc, tf, property)]
        self._avgdl: float = 0.0
        
        # Structured field values for exact matching
        self._structured_values: Dict[str, Dict[str, Set[str]]] = {}  # doc -> field -> values

        self._build_index()

    def _build_index(self) -> None:
        """Build inverted index with property information"""
        models = list(self.graph.subjects(RDF.type, self.DAIMO.Model))
        total_len = 0

        for model in models:
            model_uri = str(model)
            
            # Extract text with property tracking
            all_tokens, property_terms, structured_values = self._extract_model_text_enhanced(model)
            
            if not all_tokens:
                continue

            self._doc_tokens[model_uri] = all_tokens
            self._doc_len[model_uri] = len(all_tokens)
            self._doc_property_terms[model_uri] = property_terms
            self._structured_values[model_uri] = structured_values
            total_len += len(all_tokens)

            # Term frequency
            tf: Dict[str, int] = {}
            for t in all_tokens:
                tf[t] = tf.get(t, 0) + 1
            self._doc_tf[model_uri] = tf

            # Document frequency
            for term in set(all_tokens):
                self._df[term] = self._df.get(term, 0) + 1

        doc_count = max(len(self._doc_len), 1)
        self._avgdl = total_len / doc_count

        # IDF calculation with smoothing
        for term, df in self._df.items():
            self._idf[term] = math.log((doc_count - df + 0.5) / (df + 0.5) + 1.0)

        # Build inverted index with property information
        for doc_uri, terms_by_prop in self._doc_property_terms.items():
            for prop, terms in terms_by_prop.items():
                for term in terms:
                    tf = self._doc_tf[doc_uri].get(term, 0)
                    if tf > 0:
                        self._inverted.setdefault(term, []).append((doc_uri, tf, prop))

    def _extract_model_text_enhanced(
        self, model: URIRef
    ) -> Tuple[List[str], Dict[str, Set[str]], Dict[str, Set[str]]]:
        """
        Extract text with property tracking and structured values.
        
        Returns:
            (all_tokens, property_terms_map, structured_values_map)
        """
        property_terms: Dict[str, Set[str]] = {}
        structured_values: Dict[str, Set[str]] = {}
        all_tokens: List[str] = []

        # Extract from configured properties
        for prop in PROPERTY_WEIGHTS.keys():
            prop_str = str(prop)
            for obj in self.graph.objects(model, prop):
                texts = self._object_texts(obj)
                tokens = []
                for text in texts:
                    tokens.extend(self._tokenize(text))
                    # Store original value for structured matching
                    structured_values.setdefault(prop_str, set()).add(text.lower())
                
                if tokens:
                    property_terms.setdefault(prop_str, set()).update(tokens)
                    all_tokens.extend(tokens)

        # License via ODRL policy node
        for policy in self.graph.objects(model, ODRL.hasPolicy):
            for obj in self.graph.objects(policy, DCTERMS.identifier):
                texts = self._object_texts(obj)
                tokens = []
                for text in texts:
                    tokens.extend(self._tokenize(text))
                
                if tokens:
                    prop_str = str(DCTERMS.identifier)
                    property_terms.setdefault(prop_str, set()).update(tokens)
                    all_tokens.extend(tokens)

        return all_tokens, property_terms, structured_values

    def _object_texts(self, obj) -> List[str]:
        """Extract text values from RDF object"""
        if isinstance(obj, Literal):
            return [str(obj)]

        texts: List[str] = []
        if isinstance(obj, URIRef):
            # Try to get label
            for pred in [FOAF.name, RDFS.label, DCTERMS.title, DCTERMS.identifier]:
                for label in self.graph.objects(obj, pred):
                    if isinstance(label, Literal):
                        texts.append(str(label))

            if not texts:
                texts.append(self._uri_to_token(obj))
        return texts

    def _uri_to_token(self, uri: URIRef) -> str:
        """Extract readable token from URI"""
        s = str(uri)
        if "#" in s:
            return s.rsplit("#", 1)[-1]
        return s.rsplit("/", 1)[-1]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms"""
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return [t for t in tokens if len(t) >= self.min_token_len]

    def _expand_query(self, query_tokens: List[str]) -> List[str]:
        """
        Expand query with semantic variations.
        
        Example:
            ["pytorch", "image", "classification"] 
            → ["pytorch", "torch", "pt", "image", "classification", "computer", "vision", "cv"]
        """
        if not self.enable_query_expansion:
            return query_tokens

        expanded = set(query_tokens)
        query_text = " ".join(query_tokens).lower()

        # Check for multi-word expansions first
        for key, expansions in QUERY_EXPANSIONS.items():
            if key in query_text:
                # Add expanded terms
                for exp in expansions:
                    expanded.update(exp.split())

        # Check for abbreviations
        for token in query_tokens:
            if token.lower() in ABBREVIATION_EXPANSIONS:
                for exp in ABBREVIATION_EXPANSIONS[token.lower()]:
                    expanded.update(exp.split())

        return list(expanded)

    def _calculate_property_weight(self, property_uri: str) -> float:
        """Get weight for a property (higher = more important)"""
        if not self.enable_property_weighting:
            return 1.0
        
        prop = URIRef(property_uri)
        return PROPERTY_WEIGHTS.get(prop, 1.0)

    def _check_structured_match(
        self, doc_uri: str, query_tokens: List[str]
    ) -> float:
        """
        Check if query matches structured field values exactly.
        
        Example: Query "pytorch image classification" should boost models with:
        - library = "pytorch" (exact match)
        - task = "image-classification" (exact match after normalization)
        """
        if doc_uri not in self._structured_values:
            return 0.0

        structured_vals = self._structured_values[doc_uri]
        query_text = " ".join(query_tokens).lower()
        
        boost = 0.0
        
        # Check high-value structured fields
        for prop in [
            str(self.DAIMO.task),
            str(self.DAIMO.library),
            str(self.DAIMO.framework),
        ]:
            if prop in structured_vals:
                for value in structured_vals[prop]:
                    # Exact match or high overlap
                    value_tokens = set(self._tokenize(value))
                    query_token_set = set(query_tokens)
                    
                    if value_tokens.issubset(query_token_set) or query_token_set.issubset(value_tokens):
                        # Strong match
                        boost += self.structured_boost
                    elif len(value_tokens & query_token_set) >= len(value_tokens) * 0.5:
                        # Partial match
                        boost += self.structured_boost * 0.5

        return boost

    def search(self, query_tokens: Iterable[str], top_k: int = 5) -> List[SearchResult]:
        """
        Search with ontology-enhanced BM25.
        
        Args:
            query_tokens: Query terms (can be single words or phrases)
            top_k: Number of results to return
            
        Returns:
            Ranked list of SearchResult objects
        """
        tokens = [t.lower() for t in query_tokens if t]
        if not tokens:
            return []

        # 1. Query expansion
        expanded_tokens = self._expand_query(tokens)
        
        # 2. Standard BM25 scoring with property weights
        scores: Dict[str, float] = {}
        matched_terms: Dict[str, Set[str]] = {}
        
        for term in expanded_tokens:
            if term not in self._idf:
                continue
            
            idf = self._idf[term]
            postings = self._inverted.get(term, [])
            
            for doc_uri, tf, prop in postings:
                dl = self._doc_len[doc_uri]
                
                # Standard BM25 score
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / self._avgdl))
                bm25_score = idf * (tf * (self.k1 + 1.0) / denom)
                
                # Apply property weight
                prop_weight = self._calculate_property_weight(prop)
                weighted_score = bm25_score * prop_weight
                
                scores[doc_uri] = scores.get(doc_uri, 0.0) + weighted_score
                matched_terms.setdefault(doc_uri, set()).add(term)

        # 3. Apply structured field boost
        for doc_uri in list(scores.keys()):
            struct_boost = self._check_structured_match(doc_uri, tokens)
            if struct_boost > 0:
                scores[doc_uri] += struct_boost

        # 4. Rank and return
        ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        
        return [
            SearchResult(
                model_uri=uri,
                score=score,
                matched_terms=matched_terms.get(uri)
            )
            for uri, score in ranked[:top_k]
        ]


if __name__ == "__main__":
    # Quick test
    graph_path = Path(__file__).parent.parent.parent / "data" / "ai_models_multi_repo.ttl"
    
    if not graph_path.exists():
        print(f"❌ Graph not found at {graph_path}")
        exit(1)
    
    print("🔧 Building Ontology-Enhanced BM25 index...")
    engine = OntologyEnhancedBM25(graph_path)
    
    test_queries = [
        ["pytorch", "image", "classification"],
        ["nlp", "text", "generation"],
        ["transformers", "bert"],
        ["tensorflow", "object", "detection"],
    ]
    
    print("\n=== Testing Enhanced BM25 ===")
    for query in test_queries:
        print(f"\n🔍 Query: {' '.join(query)}")
        results = engine.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.model_uri.split('/')[-1]}")
            print(f"     Score: {result.score:.4f}")
            if result.matched_terms:
                print(f"     Matched: {', '.join(sorted(result.matched_terms))}")
