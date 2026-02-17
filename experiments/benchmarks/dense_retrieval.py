"""
Dense Retrieval with SBERT for AI Model Discovery

Uses Sentence-BERT embeddings for semantic search over AI models.
Integrates with BM25 for hybrid retrieval.

Author: AI Model Discovery System
Date: 2026-02-15
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, RDFS

try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False
    print("⚠️ sentence-transformers not installed. Run: pip install sentence-transformers")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ faiss not installed. Run: pip install faiss-cpu")


@dataclass
class DenseResult:
    """Result from dense retrieval."""
    model_uri: str
    score: float  # Cosine similarity (0-1)
    rank: int


class DenseRetrieval:
    """
    Dense retrieval using Sentence-BERT embeddings.
    
    Features:
    - Pre-computed embeddings with FAISS index
    - Fast similarity search (~10-20ms)
    - Semantic understanding beyond exact matches
    """
    
    def __init__(
        self,
        graph_path: Optional[Path] = None,
        graph: Optional[Graph] = None,
        model_name: str = "all-MiniLM-L6-v2",
        index_path: Optional[Path] = None,
        rebuild_index: bool = False,
    ):
        """
        Args:
            graph_path: Path to RDF graph (Turtle format)
            graph: Pre-loaded RDF graph (alternative to graph_path)
            model_name: Sentence transformer model
            index_path: Path to save/load FAISS index
            rebuild_index: Force rebuild of index
        """
        if not SBERT_AVAILABLE:
            raise ImportError("sentence-transformers required. Install: pip install sentence-transformers")
        
        if not FAISS_AVAILABLE:
            raise ImportError("faiss required. Install: pip install faiss-cpu")
        
        # Load graph
        if graph is not None:
            self.graph = graph
        elif graph_path is not None:
            self.graph = Graph()
            self.graph.parse(str(graph_path), format="turtle")
        else:
            raise ValueError("Provide either graph_path or graph")
        
        self.DAIMO = Namespace("http://purl.org/pionera/daimo#")
        
        # Load SBERT model
        print(f"📦 Loading Sentence-BERT model: {model_name}")
        self.encoder = SentenceTransformer(model_name)
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
        
        # Index structures
        self.model_uris: List[str] = []
        self.model_texts: List[str] = []
        self.index: Optional[faiss.Index] = None
        
        # Build or load index
        self.index_path = index_path or Path("dense_index.faiss")
        self.metadata_path = self.index_path.with_suffix(".pkl")
        
        if rebuild_index or not self.index_path.exists():
            self._build_index()
        else:
            self._load_index()
    
    def _extract_model_text(self, model: URIRef) -> str:
        """
        Extract comprehensive text representation of a model.
        
        Includes: title, description, task, library, keywords, etc.
        """
        texts = []
        
        # Title (highest weight - repeat 3x)
        for title in self.graph.objects(model, DCTERMS.title):
            if isinstance(title, Literal):
                texts.extend([str(title)] * 3)
        
        for name in self.graph.objects(model, FOAF.name):
            if isinstance(name, Literal):
                texts.extend([str(name)] * 3)
        
        # Description (repeat 2x)
        for desc in self.graph.objects(model, DCTERMS.description):
            if isinstance(desc, Literal):
                texts.extend([str(desc)] * 2)
        
        # Task (repeat 2x for importance)
        for task in self.graph.objects(model, self.DAIMO.task):
            if isinstance(task, Literal):
                texts.extend([str(task)] * 2)
        
        # Library/Framework (repeat 2x)
        for lib in self.graph.objects(model, self.DAIMO.library):
            if isinstance(lib, Literal):
                texts.extend([str(lib)] * 2)
        
        for fw in self.graph.objects(model, self.DAIMO.framework):
            if isinstance(fw, Literal):
                texts.extend([str(fw)] * 2)
        
        # Keywords
        for kw in self.graph.objects(model, DCAT.keyword):
            if isinstance(kw, Literal):
                texts.append(str(kw))
        
        # Other properties (single weight)
        single_weight_props = [
            DCTERMS.identifier,
            RDFS.label,
            self.DAIMO.architecture,
            self.DAIMO.modelType,
            DCTERMS.source,
        ]
        
        for prop in single_weight_props:
            for obj in self.graph.objects(model, prop):
                if isinstance(obj, Literal):
                    texts.append(str(obj))
        
        # Join with spaces and clean
        full_text = " ".join(texts)
        full_text = " ".join(full_text.split())  # Normalize whitespace
        
        return full_text if full_text else f"Model {model}"
    
    def _build_index(self):
        """Build FAISS index with model embeddings."""
        print("🔨 Building dense retrieval index...")
        
        # Extract all models
        models = list(self.graph.subjects(RDF.type, self.DAIMO.Model))
        print(f"   Found {len(models)} models")
        
        if not models:
            raise ValueError("No models found in graph")
        
        # Extract text for each model
        self.model_uris = []
        self.model_texts = []
        
        for model in models:
            text = self._extract_model_text(model)
            self.model_uris.append(str(model))
            self.model_texts.append(text)
        
        # Generate embeddings
        print(f"   Generating embeddings with {self.encoder._first_module().auto_model.config._name_or_path}")
        embeddings = self.encoder.encode(
            self.model_texts,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True,
        )
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Build FAISS index (Inner Product = Cosine after normalization)
        print(f"   Building FAISS index (dimension={self.embedding_dim})")
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embeddings.astype(np.float32))
        
        # Save index and metadata
        print(f"   Saving index to {self.index_path}")
        faiss.write_index(self.index, str(self.index_path))
        
        with open(self.metadata_path, "wb") as f:
            pickle.dump({
                "model_uris": self.model_uris,
                "model_texts": self.model_texts,
                "model_name": self.encoder._first_module().auto_model.config._name_or_path,
            }, f)
        
        print(f"✅ Dense index built: {len(self.model_uris)} models indexed")
    
    def _load_index(self):
        """Load pre-built FAISS index."""
        print(f"📂 Loading dense index from {self.index_path}")
        
        self.index = faiss.read_index(str(self.index_path))
        
        with open(self.metadata_path, "rb") as f:
            metadata = pickle.load(f)
            self.model_uris = metadata["model_uris"]
            self.model_texts = metadata["model_texts"]
            model_name = metadata.get("model_name", "unknown")
        
        print(f"✅ Loaded {len(self.model_uris)} models (indexed with {model_name})")
    
    def search(self, query: str, top_k: int = 5) -> List[DenseResult]:
        """
        Search for models using dense retrieval.
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            
        Returns:
            List of DenseResult sorted by score (descending)
        """
        if self.index is None:
            raise RuntimeError("Index not built. Call _build_index() first.")
        
        # Encode query
        query_emb = self.encoder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_emb)  # Normalize for cosine similarity
        
        # Search
        scores, indices = self.index.search(query_emb.astype(np.float32), top_k)
        
        # Build results
        results = []
        for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), 1):
            if idx < len(self.model_uris):  # Valid index
                results.append(DenseResult(
                    model_uri=self.model_uris[idx],
                    score=float(score),  # Cosine similarity [0, 1]
                    rank=rank
                ))
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get index statistics."""
        return {
            "num_models": len(self.model_uris),
            "embedding_dim": self.embedding_dim,
            "model_name": self.encoder._first_module().auto_model.config._name_or_path,
            "index_type": type(self.index).__name__ if self.index else None,
        }


def main():
    """Test dense retrieval."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # Load graph
    graph_path = project_root / "data" / "ai_models_multi_repo.ttl"
    
    if not graph_path.exists():
        print(f"❌ Graph not found: {graph_path}")
        return
    
    # Build dense retrieval
    index_path = Path(__file__).parent / "dense_index.faiss"
    
    dense = DenseRetrieval(
        graph_path=graph_path,
        index_path=index_path,
        rebuild_index=False,  # Set True to rebuild
    )
    
    # Test queries
    test_queries = [
        "PyTorch models for image classification",
        "transformer models for NLP",
        "BERT models",
        "models with MIT license",
        "diffusion models for image generation",
    ]
    
    print("\n" + "="*80)
    print("🔍 DENSE RETRIEVAL TEST")
    print("="*80)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = dense.search(query, top_k=5)
        
        for result in results:
            # Get model title
            model_uri = URIRef(result.model_uri)
            title = "Unknown"
            for t in dense.graph.objects(model_uri, DCTERMS.title):
                title = str(t)
                break
            
            print(f"  {result.rank}. [{result.score:.3f}] {title[:60]}")
    
    # Statistics
    print("\n" + "="*80)
    print("📊 STATISTICS")
    print("="*80)
    stats = dense.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
