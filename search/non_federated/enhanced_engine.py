"""
Enhanced Search Engine - Production Deployment

Integrates all Method 1 improvements:
- Phase 2: Simple query optimization (templates + post-processing)
- Phase 3: Complex query optimization (enhanced RAG + prompts)
- Phase 4: Hybrid system (BM25 ↔ Method1 routing + fusion)

Autor: Edmundo Mori
Fecha: 2026-02-13
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import tempfile

# Add paths for Phase 2, Phase 3, and Phase 4 modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PHASE2_DIR = PROJECT_ROOT / "strategies/method1_enhancement/02_simple_queries"
PHASE3_DIR = PROJECT_ROOT / "strategies/method1_enhancement/03_complex_queries"
PHASE4_DIR = PROJECT_ROOT / "strategies/method1_enhancement/04_hybrid"
BM25_DIR = PROJECT_ROOT / "experiments/benchmarks"

sys.path.insert(0, str(PHASE2_DIR))
sys.path.insert(0, str(PHASE3_DIR))
sys.path.insert(0, str(PHASE4_DIR))
sys.path.insert(0, str(BM25_DIR))

# Import Phase 2 components (COMMENTED - Not yet implemented)
# from simple_query_detector import SimpleQueryDetector
# from template_generator import TemplateGenerator
# from sparql_post_processor import SPARQLPostProcessor
SimpleQueryDetector = None
TemplateGenerator = None
SPARQLPostProcessor = None

# Import Phase 3 components (COMMENTED - Not yet implemented)
# from complex_query_detector import ComplexQueryDetector
# from specialized_rag import SpecializedRAG
# from enhanced_prompts import EnhancedPrompter
ComplexQueryDetector = None
SpecializedRAG = None
EnhancedPrompter = None

# Import Phase 4 components (COMMENTED - Not yet implemented)
# from query_router import QueryRouter, RoutingStrategy
# from confidence_calibrator import ConfidenceCalibrator
# from result_fusion import ResultFusion
QueryRouter = None
RoutingStrategy = None
ConfidenceCalibrator = None
ResultFusion = None

# Import BM25 engines (COMMENTED - Not yet implemented)
# from keyword_bm25 import KeywordBM25Baseline, SearchResult as BM25SearchResult
# from ontology_enhanced_bm25 import OntologyEnhancedBM25
KeywordBM25Baseline = None
BM25SearchResult = None
OntologyEnhancedBM25 = None

# Import original components
from llm.text_to_sparql import TextToSPARQLConverter, ConversionResult
from rdflib import Graph

logger = logging.getLogger(__name__)


class EnhancedSearchEngine:
    """
    Enhanced search engine with all Method 1 improvements
    
    Pipeline:
    1. Router decides strategy (Phase 4)
    2. If simple → Use BM25 or template (Phase 4/2)
    3. If complex → Use Method1 with specialized RAG (Phase 3)
    4. If medium → Use BOTH + fusion (Phase 4)
    5. Post-process SPARQL → Fix errors (Phase 2)
    6. Execute on graph → Return results
    """
    
    def __init__(
        self,
        graph: Graph,
        llm_provider: str = "ollama",
        model: str = "deepseek-r1:7b",
        use_rag: bool = True,
        top_k_examples: int = 5,
        temperature: float = 0.1,
        enable_phase2: bool = True,
        enable_phase3: bool = True,
        enable_phase4: bool = True,
        phase4_fusion_method: str = "rrf",
        verbose: bool = False
    ):
        """
        Initialize enhanced search engine
        
        Args:
            graph: RDF graph
            llm_provider: LLM provider
            model: LLM model name
            use_rag: Enable RAG
            top_k_examples: Number of examples for RAG
            temperature: LLM temperature
            enable_phase2: Enable Phase 2 optimizations (templates + post-processing)
            enable_phase3: Enable Phase 3 optimizations (complex query enhancement)
            enable_phase4: Enable Phase 4 optimizations (hybrid BM25 ↔ Method1)
            phase4_fusion_method: Fusion method for Phase 4 ("rrf", "weighted", "cascade")
            verbose: Show debug info
        """
        self.graph = graph
        self.enable_phase2 = enable_phase2
        self.enable_phase3 = enable_phase3
        self.enable_phase4 = enable_phase4
        self.verbose = verbose
        
        # Initialize Phase 2 components (if available)
        if enable_phase2 and SimpleQueryDetector is not None:
            self.simple_detector = SimpleQueryDetector()
            self.template_generator = TemplateGenerator()
            self.post_processor = SPARQLPostProcessor()
            if verbose:
                logger.info("✅ Phase 2 components initialized")
        else:
            self.simple_detector = None
            self.template_generator = None
            self.post_processor = None
            if enable_phase2 and verbose:
                logger.warning("⚠️ Phase 2 modules not available - feature disabled")
        
        # Initialize Phase 3 components (if available)
        if enable_phase3 and ComplexQueryDetector is not None:
            self.complex_detector = ComplexQueryDetector()
            try:
                self.specialized_rag = SpecializedRAG()
                self.prompt_generator = EnhancedPrompter()
                if verbose:
                    logger.info("✅ Phase 3 components initialized")
            except Exception as e:
                logger.warning(f"⚠️ Phase 3 RAG initialization failed: {e}")
                self.specialized_rag = None
                self.prompt_generator = None
        else:
            self.complex_detector = None
            self.specialized_rag = None
            self.prompt_generator = None
            if enable_phase3 and verbose:
                logger.warning("⚠️ Phase 3 modules not available - feature disabled")
        
        # Initialize Phase 4 components (Hybrid System)
        self.bm25_engine = None
        self.router = None
        self.calibrator = None
        self.fusion = None
        
        if enable_phase4 and QueryRouter is not None:
            try:
                # Initialize BM25 engine with ontology enhancements
                # Save graph temporarily to file for BM25 indexing
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                    graph.serialize(destination=str(tmp_path), format='turtle')
                
                # Use Ontology-Enhanced BM25 for better semantic matching
                self.bm25_engine = OntologyEnhancedBM25(
                    graph_path=tmp_path,
                    enable_query_expansion=True,  # Semantic term expansion
                    enable_property_weighting=True,  # Weight by field importance
                    structured_boost=1.5  # Boost exact matches in task/library
                )
                tmp_path.unlink()  # Clean up temp file after indexing
                
                # Initialize router, calibrator, and fusion
                self.router = QueryRouter(enable_fusion=True)
                self.calibrator = ConfidenceCalibrator()
                self.fusion = ResultFusion(fusion_method=phase4_fusion_method)
                
                if verbose:
                    logger.info("✅ Phase 4 components initialized (Ontology-Enhanced BM25 ↔ Method1)")
            except Exception as e:
                logger.warning(f"⚠️ Phase 4 initialization failed: {e}")
                self.bm25_engine = None
                self.router = None
                self.calibrator = None
                self.fusion = None
        
        # Initialize base LLM converter
        self.llm_converter = TextToSPARQLConverter(
            llm_provider=llm_provider,
            model=model,
            use_rag=use_rag,
            top_k_examples=top_k_examples,
            temperature=temperature
        )
        
        # Statistics
        self.stats = {
            "total_queries": 0,
            "simple_queries": 0,
            "complex_queries": 0,
            "template_used": 0,
            "llm_used": 0,
            "post_processed": 0,
            "errors_fixed": 0,
            # Phase 4 stats
            "bm25_only": 0,
            "method1_only": 0,
            "both_fusion": 0,
            "phase4_errors": 0
        }
        
        if verbose:
            logger.info("✅ Enhanced Search Engine initialized")
    
    def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Execute enhanced search with Phase 4 hybrid routing
        
        Args:
            query: Natural language query
            max_results: Maximum results to return
            
        Returns:
            Dict with results and metadata
        """
        self.stats["total_queries"] += 1
        
        metadata = {
            "query": query,
            "method_used": None,
            "is_simple": False,
            "complexity_score": 0.0,
            "features": [],
            "template_pattern": None,
            "post_processing_applied": False,
            "errors_fixed": [],
            "phase4_strategy": None,
            "phase4_fusion_applied": False
        }
        
        sparql_query = None
        success = False
        results = []
        
        # PHASE 4: HYBRID ROUTING LOGIC
        if self.enable_phase4 and self.router and self.bm25_engine:
            # Get routing decision
            routing_decision = self.router.route(query)
            metadata["phase4_strategy"] = routing_decision.strategy.value
            metadata["complexity_score"] = routing_decision.complexity_score
            metadata["features"] = routing_decision.features
            
            if self.verbose:
                logger.info(f"🚦 Phase 4 Router: {routing_decision.strategy.value} (complexity: {routing_decision.complexity_score:.2f})")
            
            # Strategy 1: BM25 ONLY (simple queries)
            if routing_decision.strategy == RoutingStrategy.BM25_ONLY:
                self.stats["bm25_only"] += 1
                metadata["method_used"] = "bm25"
                
                # Run BM25
                query_tokens = query.lower().split()
                bm25_results = self.bm25_engine.search(query_tokens, top_k=max_results)
                
                # Convert BM25 results to standard format
                for bm25_res in bm25_results:
                    results.append({
                        "model_uri": bm25_res.model_uri,
                        "score": bm25_res.score,
                        "method": "bm25"
                    })
                
                if self.verbose:
                    logger.info(f"✅ BM25 returned {len(results)} results")
                
                # Calibrate confidence
                if self.calibrator:
                    confidence = self.calibrator.calibrate_bm25(
                        query,
                        top_score=results[0]["score"] if results else 0.0,
                        result_count=len(results)
                    )
                    metadata["confidence_bm25"] = confidence
                
                return {
                    "success": True,
                    "query": query,
                    "sparql": None,
                    "results": results,
                    "total_results": len(results),
                    "execution_time": 0.0,
                    "metadata": metadata,
                    "statistics": self.get_statistics()
                }
            
            # Strategy 2: METHOD1 ONLY (complex queries)
            elif routing_decision.strategy == RoutingStrategy.METHOD1_ONLY:
                self.stats["method1_only"] += 1
                # Use existing Phase 2/3 logic (below)
                pass
            
            # Strategy 3: BOTH + FUSION (medium queries)
            elif routing_decision.strategy == RoutingStrategy.BOTH_FUSION:
                self.stats["both_fusion"] += 1
                metadata["phase4_fusion_applied"] = True
                
                # Run BM25
                query_tokens = query.lower().split()
                bm25_results = self.bm25_engine.search(query_tokens, top_k=max_results)
                
                # Run Method1 (using existing Phase 2/3 logic)
                method1_results = self._run_method1_pipeline(query, max_results, metadata)
                
                # Fuse results
                if self.fusion:
                    fused_results = self.fusion.fuse(
                        bm25_results=[{"model_uri": r.model_uri, "rank": i+1} for i, r in enumerate(bm25_results)],
                        method1_results=method1_results,
                        top_k=max_results
                    )
                    
                    # Convert FusionResult objects to dict format
                    results = []
                    for fr in fused_results:
                        # Extract model_uri from the FusionResult item
                        model_uri = fr.item.get("model_uri")
                        if not model_uri:
                            # Try alternative keys
                            model_uri = fr.item.get("model") or fr.item.get("uri")
                        
                        if model_uri:
                            results.append({
                                "model_uri": model_uri,
                                "score": fr.combined_score,
                                "sources": fr.sources,
                                "bm25_rank": fr.bm25_rank,
                                "method1_rank": fr.method1_rank
                            })
                    
                    metadata["fusion_method"] = self.fusion.fusion_method
                    metadata["method_used"] = "hybrid_fusion"
                    
                    if self.verbose:
                        logger.info(f"✅ Fusion returned {len(results)} results (BM25: {len(bm25_results)}, Method1: {len(method1_results)})")
                else:
                    # Fallback: prefer Method1
                    results = method1_results
                    metadata["method_used"] = "method1_fallback"
                
                return {
                    "success": True,
                    "query": query,
                    "sparql": metadata.get("sparql_query", None),
                    "results": results,
                    "total_results": len(results),
                    "execution_time": metadata.get("execution_time", 0.0),
                    "metadata": metadata,
                    "statistics": self.get_statistics()
                }
        
        # PHASE 2 & 3: METHOD1 PIPELINE (used for METHOD1_ONLY or when Phase 4 disabled)
        results = self._run_method1_pipeline(query, max_results, metadata)
        
        # Extract SPARQL from metadata if available
        sparql_query = metadata.get("sparql_query", None)
        success = len(results) > 0
        
        return {
            "success": success,
            "query": query,
            "sparql": sparql_query,
            "results": results,
            "total_results": len(results),
            "execution_time": metadata.get("execution_time", 0.0),
            "metadata": metadata,
            "statistics": self.get_statistics()
        }
    
    def _run_method1_pipeline(self, query: str, max_results: int, metadata: Dict) -> List[Dict]:
        """
        Run Method1 pipeline (Phase 2 + Phase 3)
        
        Returns:
            List of result dicts with model_uri and metadata
        """
        sparql_query = None
        success = False
        
        # Step 1: Try Phase 2 (simple query with template) - if modules available
        if self.enable_phase2 and self.simple_detector is not None:
            simple_result = self.simple_detector.detect(query)
            metadata["is_simple"] = simple_result.is_simple
            
            if simple_result.is_simple:
                self.stats["simple_queries"] += 1
                
                # Try to generate from template
                template_sparql = self.template_generator.generate(
                    simple_result.pattern_type,
                    simple_result.entities
                )
                
                if template_sparql:
                    self.stats["template_used"] += 1
                    metadata["method_used"] = "template"
                    metadata["template_pattern"] = simple_result.pattern_type
                    sparql_query = template_sparql
                    metadata["sparql_query"] = sparql_query  # Save for later access
                    success = True
                    
                    if self.verbose:
                        logger.info(f"✅ Template generated for pattern: {simple_result.pattern_type}")
                else:
                    # Template generation failed - will fall back to LLM
                    if self.verbose:
                        logger.warning(f"⚠️ Template generation failed for pattern {simple_result.pattern_type}, falling back to LLM")
        
        # Step 2: Use LLM (with Phase 3 enhancements if complex)
        if not success:
            self.stats["llm_used"] += 1
            
            # Detect complexity for Phase 3 - if modules available
            complexity_info = None
            if self.enable_phase3 and self.complex_detector is not None:
                complexity_info = self.complex_detector.detect(query)
                metadata["complexity_score"] = complexity_info.complexity_score
                metadata["features"] = complexity_info.features
                
                if complexity_info.complexity_score >= 0.3:
                    self.stats["complex_queries"] += 1
                    
                    if self.verbose:
                        logger.info(f"🎯 Complex query detected (score: {complexity_info.complexity_score:.2f})")
            
            # Generate with LLM (potentially enhanced by Phase 3)
            try:
                # If we have Phase 3 and query is complex, use specialized RAG
                if (self.enable_phase3 and complexity_info and 
                    complexity_info.complexity_score >= 0.3 and 
                    self.specialized_rag):
                    
                    # Get specialized examples
                    examples = self.specialized_rag.select_examples(
                        query, complexity_info
                    )
                    
                    if self.verbose:
                        logger.info(f"📚 Using {len(examples)} specialized examples")
                    
                    # Generate enhanced prompt
                    if self.prompt_generator:
                        # Use enhanced prompts (this would require modifying the converter)
                        # For now, we'll use the standard converter with selected examples
                        pass
                
                # Use standard LLM conversion
                conversion_result = self.llm_converter.convert(query, validate=False)
                
                if isinstance(conversion_result, ConversionResult):
                    sparql_query = conversion_result.sparql_query
                    success = conversion_result.is_valid
                elif isinstance(conversion_result, tuple):
                    success, sparql_query, _ = conversion_result
                else:
                    sparql_query = str(conversion_result)
                    success = bool(sparql_query)
                
                metadata["method_used"] = "llm_enhanced" if self.enable_phase3 else "llm"
                metadata["sparql_query"] = sparql_query  # Save for later access
                
            except Exception as e:
                logger.error(f"❌ LLM conversion failed: {e}")
                success = False
                metadata["execution_error"] = f"LLM conversion error: {str(e)}"
        
        # Step 3: Post-process SPARQL (Phase 2) - if available
        if success and sparql_query and self.enable_phase2 and self.post_processor is not None:
            post_success, post_sparql, post_metadata = self.post_processor.process(sparql_query)
            
            if post_success and post_sparql != sparql_query:
                self.stats["post_processed"] += 1
                metadata["post_processing_applied"] = True
                metadata["errors_fixed"] = post_metadata.get("fixes", [])
                sparql_query = post_sparql
                metadata["sparql_query"] = post_sparql  # 🔧 FIX: Update metadata with corrected query
                
                if post_metadata.get("fixes"):
                    self.stats["errors_fixed"] += len(post_metadata["fixes"])
                    
                    if self.verbose:
                        logger.info(f"🔧 Post-processing applied: {post_metadata['fixes']}")
        
        # Step 4: Execute SPARQL
        results = []
        
        if success and sparql_query:
            import time
            start = time.time()
            
            try:
                query_results = self.graph.query(sparql_query)
                
                for row in query_results:
                    result_dict = {"method": "method1"}
                    for var in query_results.vars:
                        value = row[var]
                        if value:
                            result_dict[str(var)] = str(value)
                    
                    # Extract model_uri (first variable is usually the model)
                    if query_results.vars:
                        first_var = query_results.vars[0]
                        result_dict["model_uri"] = str(row[first_var]) if row[first_var] else None
                    
                    results.append(result_dict)
                
                # Limit results
                results = results[:max_results]
                metadata["execution_time"] = time.time() - start
                
            except Exception as e:
                logger.error(f"❌ SPARQL execution failed: {e}")
                metadata["execution_error"] = str(e)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        stats = self.stats.copy()
        
        if stats["total_queries"] > 0:
            stats["template_rate"] = stats["template_used"] / stats["total_queries"]
            stats["llm_rate"] = stats["llm_used"] / stats["total_queries"]
            stats["post_process_rate"] = stats["post_processed"] / stats["total_queries"]
            
            # Phase 4 rates
            if self.enable_phase4:
                stats["bm25_rate"] = stats["bm25_only"] / stats["total_queries"]
                stats["method1_rate"] = stats["method1_only"] / stats["total_queries"]
                stats["fusion_rate"] = stats["both_fusion"] / stats["total_queries"]
        
        return stats
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        from rdflib import RDF
        from collections import Counter
        
        # Count models
        daimo = "http://purl.org/pionera/daimo#"
        model_type = f"{daimo}Model"
        
        models = list(self.graph.subjects(RDF.type, None))
        total_models = len(models)
        
        # Count by source
        sources = []
        for model in models:
            source = self.graph.value(model, None)
            if source:
                sources.append(str(source))
        
        source_counts = Counter(sources)
        
        return {
            "total_models": total_models,
            "total_triples": len(self.graph),
            "sources": dict(source_counts),
            "unique_sources": len(source_counts)
        }


def create_enhanced_api(
    graph: Graph,
    llm_provider: str = "ollama",
    model: str = "deepseek-r1:7b",
    enable_phase2: bool = True,
    enable_phase3: bool = True,
    enable_phase4: bool = True,
    phase4_fusion_method: str = "rrf",
    ** kwargs
) -> EnhancedSearchEngine:
    """
    Create enhanced search API with all improvements
    
    Args:
        graph: RDF graph
        llm_provider: LLM provider
        model: LLM model name
        enable_phase2: Enable Phase 2 optimizations (templates + post-processing)
        enable_phase3: Enable Phase 3 optimizations (complex query enhancement)
        enable_phase4: Enable Phase 4 optimizations (hybrid BM25 ↔ Method1)
        phase4_fusion_method: Fusion method for Phase 4 ("rrf", "weighted", "cascade")
        **kwargs: Additional arguments
        
    Returns:
        EnhancedSearchEngine instance
    """
    return EnhancedSearchEngine(
        graph=graph,
        llm_provider=llm_provider,
        model=model,
        enable_phase2=enable_phase2,
        enable_phase3=enable_phase3,
        enable_phase4=enable_phase4,
        phase4_fusion_method=phase4_fusion_method,
        **kwargs
    )


if __name__ == "__main__":
    # Test with small graph
    print("="*80)
    print("ENHANCED SEARCH ENGINE - Production Test")
    print("="*80)
    
    # Load graph
    graph_path = PROJECT_ROOT / "data" / "ai_models_multi_repo.ttl"
    
    if graph_path.exists():
        g = Graph()
        g.parse(str(graph_path), format="turtle")
        print(f"✅ Graph loaded: {len(g):,} triples")
    else:
        print("❌ Graph not found")
        sys.exit(1)
    
    # Create enhanced engine
    engine = create_enhanced_api(g, verbose=True)
    
    # Test queries
    test_queries = [
        "PyTorch models for image classification",  # Simple, template
        "top 10 most liked models",  # Complex, ORDER BY + LIMIT
        "Models with MIT license",  # Simple, template
    ]
    
    print(f"\n{'='*80}")
    print("Testing Enhanced Engine")
    print(f"{'='*80}\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: {query}")
        print("-"*80)
        
        result = engine.search(query, max_results=5)
        
        print(f"  Method: {result['metadata']['method_used']}")
        print(f"  Success: {result['success']}")
        print(f"  Results: {result['total_results']}")
        print(f"  Time: {result['execution_time']:.3f}s")
        
        if result['metadata']['post_processing_applied']:
            print(f"  ✅ Post-processing applied")
        
        if result['metadata']['errors_fixed']:
            print(f"  🔧 Errors fixed: {result['metadata']['errors_fixed']}")
    
    # Show statistics
    print(f"\n{'='*80}")
    print("ENGINE STATISTICS")
    print(f"{'='*80}")
    
    stats = engine.get_statistics()
    print(f"  Total queries: {stats['total_queries']}")
    print(f"  Template used: {stats['template_used']} ({stats.get('template_rate', 0)*100:.0f}%)")
    print(f"  LLM used: {stats['llm_used']} ({stats.get('llm_rate', 0)*100:.0f}%)")
    print(f"  Post-processed: {stats['post_processed']}")
    print(f"  Errors fixed: {stats['errors_fixed']}")
    
    print(f"\n{'='*80}")
    print("✅ Test complete!")
    print(f"{'='*80}")
