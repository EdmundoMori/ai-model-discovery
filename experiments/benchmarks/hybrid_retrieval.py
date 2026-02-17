"""
Hybrid Retrieval: BM25 + Dense (SBERT)

Combines lexical (BM25 with ontology) and semantic (SBERT) retrieval
using Reciprocal Rank Fusion (RRF) for optimal results.

Author: AI Model Discovery System  
Date: 2026-02-15
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ontology_enhanced_bm25 import OntologyEnhancedBM25, SearchResult
from dense_retrieval import DenseRetrieval, DenseResult


@dataclass
class HybridResult:
    """Result from hybrid retrieval."""
    model_uri: str
    combined_score: float
    bm25_score: float
    dense_score: float
    bm25_rank: Optional[int]
    dense_rank: Optional[int]
    final_rank: int


class HybridRetrieval:
    """
    Hybrid retrieval combining BM25 and Dense retrieval.
    
    Fusion methods:
    - RRF (Reciprocal Rank Fusion): Combines ranks robustly
    - Weighted: Linear combination of normalized scores
    """
    
    def __init__(
        self,
        bm25_engine: OntologyEnhancedBM25,
        dense_engine: DenseRetrieval,
        fusion_method: str = "rrf",
        bm25_weight: float = 0.6,
        dense_weight: float = 0.4,
        rrf_k: int = 60,
    ):
        """
        Args:
            bm25_engine: BM25 with ontology enhancements
            dense_engine: Dense retrieval with SBERT
            fusion_method: 'rrf' or 'weighted'
            bm25_weight: Weight for BM25 scores (if weighted fusion)
            dense_weight: Weight for dense scores (if weighted fusion)
            rrf_k: Constant for RRF (typically 60)
        """
        self.bm25_engine = bm25_engine
        self.dense_engine = dense_engine
        self.fusion_method = fusion_method
        self.bm25_weight = bm25_weight
        self.dense_weight = dense_weight
        self.rrf_k = rrf_k
        
        # Statistics
        self.stats = {
            "total_searches": 0,
            "bm25_only_contribution": 0,
            "dense_only_contribution": 0,
            "both_contribution": 0,
        }
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        bm25_top_k: int = 50,
        dense_top_k: int = 50,
    ) -> List[HybridResult]:
        """
        Hybrid search combining BM25 and Dense retrieval.
        
        Args:
            query: Natural language query
            top_k: Final number of results
            bm25_top_k: Retrieve top-N from BM25
            dense_top_k: Retrieve top-N from Dense
            
        Returns:
            List of HybridResult sorted by combined score
        """
        self.stats["total_searches"] += 1
        
        # Get results from both engines
        bm25_results_raw = self.bm25_engine.search(
            query.lower().split(),
            top_k=bm25_top_k
        )
        
        # Add ranks to BM25 results (SearchResult doesn't have rank attribute)
        class ResultWithRank:
            def __init__(self, result, rank):
                self.model_uri = result.model_uri
                self.score = result.score
                self.rank = rank
        
        bm25_results = [ResultWithRank(r, i+1) for i, r in enumerate(bm25_results_raw)]
        
        dense_results = self.dense_engine.search(
            query,
            top_k=dense_top_k
        )
        
        # Fusion
        if self.fusion_method == "rrf":
            combined = self._fusion_rrf(bm25_results, dense_results)
        else:  # weighted
            combined = self._fusion_weighted(bm25_results, dense_results)
        
        # Sort by combined score
        combined.sort(key=lambda x: x.combined_score, reverse=True)
        
        # Update ranks and stats
        for i, result in enumerate(combined[:top_k], 1):
            result.final_rank = i
            
            # Track contribution
            if result.bm25_rank and result.dense_rank:
                self.stats["both_contribution"] += 1
            elif result.bm25_rank:
                self.stats["bm25_only_contribution"] += 1
            elif result.dense_rank:
                self.stats["dense_only_contribution"] += 1
        
        return combined[:top_k]
    
    def _fusion_rrf(
        self,
        bm25_results: List[SearchResult],
        dense_results: List[DenseResult],
    ) -> List[HybridResult]:
        """
        Reciprocal Rank Fusion (RRF).
        
        RRF(d) = Σ(1 / (k + rank(d)))
        
        Advantages:
        - Robust to score scale differences
        - No normalization needed
        - Well-tested in IR literature
        """
        # Build maps: model_uri -> (score, rank)
        bm25_map = {r.model_uri: (r.score, r.rank) for r in bm25_results}
        dense_map = {r.model_uri: (r.score, r.rank) for r in dense_results}
        
        # Get all unique models
        all_models = set(bm25_map.keys()) | set(dense_map.keys())
        
        # Calculate RRF score for each model
        combined = []
        
        for model_uri in all_models:
            bm25_score, bm25_rank = bm25_map.get(model_uri, (0.0, None))
            dense_score, dense_rank = dense_map.get(model_uri, (0.0, None))
            
            # RRF formula
            rrf_score = 0.0
            if bm25_rank is not None:
                rrf_score += 1.0 / (self.rrf_k + bm25_rank)
            if dense_rank is not None:
                rrf_score += 1.0 / (self.rrf_k + dense_rank)
            
            combined.append(HybridResult(
                model_uri=model_uri,
                combined_score=rrf_score,
                bm25_score=bm25_score,
                dense_score=dense_score,
                bm25_rank=bm25_rank,
                dense_rank=dense_rank,
                final_rank=0,  # Will be set later
            ))
        
        return combined
    
    def _fusion_weighted(
        self,
        bm25_results: List[SearchResult],
        dense_results: List[DenseResult],
    ) -> List[HybridResult]:
        """
        Weighted score fusion with normalization.
        
        combined = α * norm(BM25) + (1-α) * norm(Dense)
        """
        # Build maps
        bm25_map = {r.model_uri: (r.score, r.rank) for r in bm25_results}
        dense_map = {r.model_uri: (r.score, r.rank) for r in dense_results}
        
        # Normalize scores to [0, 1]
        bm25_scores = [r.score for r in bm25_results]
        dense_scores = [r.score for r in dense_results]
        
        bm25_max = max(bm25_scores) if bm25_scores else 1.0
        bm25_min = min(bm25_scores) if bm25_scores else 0.0
        bm25_range = bm25_max - bm25_min if bm25_max > bm25_min else 1.0
        
        dense_max = max(dense_scores) if dense_scores else 1.0
        dense_min = min(dense_scores) if dense_scores else 0.0
        dense_range = dense_max - dense_min if dense_max > dense_min else 1.0
        
        # Get all unique models
        all_models = set(bm25_map.keys()) | set(dense_map.keys())
        
        # Calculate weighted score for each model
        combined = []
        
        for model_uri in all_models:
            bm25_score, bm25_rank = bm25_map.get(model_uri, (0.0, None))
            dense_score, dense_rank = dense_map.get(model_uri, (0.0, None))
            
            # Normalize
            bm25_norm = (bm25_score - bm25_min) / bm25_range if bm25_rank else 0.0
            dense_norm = (dense_score - dense_min) / dense_range if dense_rank else 0.0
            
            # Weighted combination
            combined_score = (
                self.bm25_weight * bm25_norm +
                self.dense_weight * dense_norm
            )
            
            combined.append(HybridResult(
                model_uri=model_uri,
                combined_score=combined_score,
                bm25_score=bm25_score,
                dense_score=dense_score,
                bm25_rank=bm25_rank,
                dense_rank=dense_rank,
                final_rank=0,  # Will be set later
            ))
        
        return combined
    
    def get_statistics(self) -> Dict:
        """Get fusion statistics."""
        total = self.stats["total_searches"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "both_contribution_rate": self.stats["both_contribution"] / total,
            "bm25_only_rate": self.stats["bm25_only_contribution"] / total,
            "dense_only_rate": self.stats["dense_only_contribution"] / total,
        }


def main():
    """Test hybrid retrieval."""
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
    
    print("="*80)
    print("🔬 HYBRID RETRIEVAL TEST: BM25 + Dense (SBERT)")
    print("="*80)
    
    # Build BM25 engine
    print("\n📊 Loading BM25 with ontology...")
    from rdflib import Graph
    graph = Graph()
    graph.parse(str(graph_path), format="turtle")
    
    bm25 = OntologyEnhancedBM25(
        graph_path=graph_path,
        enable_query_expansion=True,
        enable_property_weighting=True,
        structured_boost=1.5,
    )
    
    # Build Dense engine
    print("\n🧠 Loading Dense retrieval (SBERT)...")
    index_path = Path(__file__).parent / "dense_index.faiss"
    
    dense = DenseRetrieval(
        graph=graph,
        index_path=index_path,
        rebuild_index=False,
    )
    
    # Build Hybrid
    print("\n🔀 Creating Hybrid retrieval...")
    hybrid = HybridRetrieval(
        bm25_engine=bm25,
        dense_engine=dense,
        fusion_method="rrf",  # or "weighted"
        bm25_weight=0.6,
        dense_weight=0.4,
    )
    
    # Test queries
    test_queries = [
        "PyTorch models for computer vision",
        "transformer models for language understanding",
        "BERT models",
        "models with MIT license",
        "image generation with diffusion",
    ]
    
    print("\n" + "="*80)
    print("🔍 SEARCH COMPARISON")
    print("="*80)
    
    from rdflib import URIRef, Namespace
    from rdflib.namespace import DCTERMS
    DAIMO = Namespace("http://purl.org/pionera/daimo#")
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        # Get results from all methods
        bm25_results_raw = bm25.search(query.lower().split(), top_k=5)
        # Add ranks for display
        class ResultWithRank:
            def __init__(self, result, rank):
                self.model_uri = result.model_uri
                self.score = result.score
                self.rank = rank
        bm25_results = [ResultWithRank(r, i+1) for i, r in enumerate(bm25_results_raw)]
        
        dense_results = dense.search(query, top_k=5)
        hybrid_results = hybrid.search(query, top_k=5)
        
        # Display BM25
        print("\n📊 BM25 with Ontology:")
        for r in bm25_results:
            model_uri = URIRef(r.model_uri)
            title = "Unknown"
            for t in graph.objects(model_uri, DCTERMS.title):
                title = str(t)
                break
            print(f"  {r.rank}. [{r.score:6.2f}] {title[:55]}")
        
        # Display Dense
        print("\n🧠 Dense (SBERT):")
        for r in dense_results:
            model_uri = URIRef(r.model_uri)
            title = "Unknown"
            for t in graph.objects(model_uri, DCTERMS.title):
                title = str(t)
                break
            print(f"  {r.rank}. [{r.score:.3f}] {title[:55]}")
        
        # Display Hybrid
        print("\n🔀 Hybrid (RRF Fusion):")
        for r in hybrid_results:
            model_uri = URIRef(r.model_uri)
            title = "Unknown"
            for t in graph.objects(model_uri, DCTERMS.title):
                title = str(t)
                break
            
            bm25_indicator = f"BM25#{r.bm25_rank}" if r.bm25_rank else "----"
            dense_indicator = f"Dense#{r.dense_rank}" if r.dense_rank else "----"
            
            print(f"  {r.final_rank}. [{r.combined_score:.4f}] "
                  f"({bm25_indicator} + {dense_indicator}) {title[:40]}")
    
    # Statistics
    print("\n" + "="*80)
    print("📊 HYBRID STATISTICS")
    print("="*80)
    stats = hybrid.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
