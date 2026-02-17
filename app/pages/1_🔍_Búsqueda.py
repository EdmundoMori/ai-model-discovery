"""
Página de Búsqueda - Interfaz de búsqueda con múltiples métodos

Permite realizar búsquedas en lenguaje natural sobre el catálogo de modelos
usando 3 métodos diferentes: Búsqueda Rápida, Inteligente y Experta

Autor: Edmundo Mori
Fecha: 2026-02-16
"""

import streamlit as st
import sys
from pathlib import Path
import time
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

# Configurar path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "experiments" / "benchmarks"))

from rdflib import Graph, Namespace


st.set_page_config(page_title="Búsqueda - AI Model Discovery", page_icon="🔍", layout="wide")


# ==================== SEARCH UTILITIES ====================

def detect_query_type(query: str, sparql: Optional[str] = None) -> Tuple[str, str]:
    """
    Detecta el tipo de query: listado, agregación u ordenamiento
    
    Returns:
        (tipo, descripcion)
        - tipo: "list", "aggregation", "ordering", "complex"
        - descripcion: explicación del tipo detectado
    """
    query_lower = query.lower()
    
    # Check SPARQL first if available
    if sparql:
        sparql_lower = sparql.lower()
        
        # Aggregation patterns
        agg_keywords = ["count(", "sum(", "avg(", "min(", "max(", "group by"]
        if any(keyword in sparql_lower for keyword in agg_keywords):
            return "aggregation", "Consulta de agregación (COUNT, SUM, AVG, etc.)"
        
        # Ordering patterns
        if "order by" in sparql_lower:
            return "ordering", "Consulta con ordenamiento (ORDER BY)"
    
    # Check natural language
    agg_patterns = [
        "count", "how many", "cuántos", "cuántas", "suma", "sum", 
        "average", "promedio", "avg", "total", "máximo", "mínimo",
        "max", "min", "group by", "agrupar"
    ]
    
    ordering_patterns = [
        "top", "best", "worst", "most", "least", "highest", "lowest",
        "mayor", "menor", "mejor", "peor", "más", "menos",
        "sort", "order", "ordenar", "ordenados"
    ]
    
    if any(pattern in query_lower for pattern in agg_patterns):
        return "aggregation", "Consulta de agregación detectada"
    
    if any(pattern in query_lower for pattern in ordering_patterns):
        return "ordering", "Consulta con ordenamiento detectada"
    
    # Default: listing
    return "list", "Consulta de listado simple"


def is_complex_query(query: str) -> bool:
    """Determina si una query es compleja (necesita LLM)"""
    query_lower = query.lower()
    
    complex_patterns = [
        "count", "how many", "cuántos", "average", "sum", "max", "min",
        "group by", "order by", "filter", "where", "having",
        "compare", "difference", "between", "versus",
        "all", "none", "every", "any", "not"
    ]
    
    # Si tiene 2+ palabras complejas, es compleja
    matches = sum(1 for pattern in complex_patterns if pattern in query_lower)
    return matches >= 2 or any(pattern in query_lower for pattern in ["count", "how many", "cuántos", "average", "sum"])


def format_query_results_suggestion(query: str, method: str) -> str:
    """Genera sugerencias si un método no aplica"""
    suggestions = {
        "fast": "💡 **Sugerencia**: Para queries simples de búsqueda por palabras clave, prueba: 'PyTorch models', 'computer vision models', 'models from HuggingFace'",
        "smart": "💡 **Sugerencia**: Este método funciona mejor con queries que requieren filtrado o ranking: 'top 10 PyTorch models', 'high rated NLP models'",
        "expert": "💡 **Sugerencia**: Este método es ideal para queries complejas: 'count models by framework', 'average rating of computer vision models', 'models with more than 1000 downloads'"
    }
    return suggestions.get(method, "")


# ==================== CACHE RESOURCES ====================

@st.cache_resource
def load_graph():
    """Cargar grafo RDF (cacheado)"""
    graph_path = project_root / "data" / "ai_models_multi_repo.ttl"
    
    if graph_path.exists():
        try:
            g = Graph()
            g.parse(str(graph_path), format="turtle")
            return g, f"✅ Grafo real cargado: {len(g):,} triples"
        except Exception as e:
            st.sidebar.warning(f"⚠️ Error cargando grafo: {e}")
    
    return None, "❌ No se pudo cargar el grafo"


@st.cache_resource
def load_bm25_engine():
    """Cargar motor BM25 (Búsqueda Rápida)"""
    graph_path = project_root / "data" / "ai_models_multi_repo.ttl"
    
    if not graph_path.exists():
        return None, "❌ Grafo no encontrado"
    
    try:
        from keyword_bm25 import KeywordBM25Baseline
        engine = KeywordBM25Baseline(graph_path=graph_path)
        return engine, "✅ Motor BM25 cargado"
    except Exception as e:
        return None, f"❌ Error: {e}"


@st.cache_resource
def load_hybrid_engine():
    """Cargar motor híbrido (Búsqueda Inteligente)"""
    graph_path = project_root / "data" / "ai_models_multi_repo.ttl"
    
    if not graph_path.exists():
        return None, "❌ Grafo no encontrado"
    
    try:
        from ontology_enhanced_bm25 import OntologyEnhancedBM25
        from dense_retrieval import DenseRetrieval
        from hybrid_retrieval import HybridRetrieval
        
        bm25_engine = OntologyEnhancedBM25(graph_path=graph_path)
        dense_engine = DenseRetrieval(graph_path=graph_path)
        hybrid_engine = HybridRetrieval(
            bm25_engine=bm25_engine,
            dense_engine=dense_engine,
            fusion_method="rrf"
        )
        
        return hybrid_engine, "✅ Motor Híbrido cargado"
    except Exception as e:
        return None, f"❌ Error: {e}"


@st.cache_resource
def load_llm_engine():
    """Cargar motor LLM con RAG (Búsqueda Experta)"""
    graph, _ = load_graph()
    
    if graph is None:
        return None, "❌ Grafo no encontrado"
    
    try:
        from llm.text_to_sparql import TextToSPARQLConverter
        
        llm_engine = TextToSPARQLConverter(
            model="deepseek-r1:7b",
            use_rag=True,
            top_k_examples=3,
            temperature=0.0,
            llm_provider="ollama",
            validation_graph=graph
        )
        
        return llm_engine, "✅ Motor LLM+RAG cargado"
    except Exception as e:
        return None, f"❌ Error: {e}"


# ==================== SEARCH METHODS ====================

def execute_fast_search(query: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Búsqueda Rápida: BM25 Baseline
    - Más rápido (~1ms)
    - Búsqueda por palabras clave
    - Ideal para queries simples
    """
    engine, status = load_bm25_engine()
    
    if engine is None:
        return {
            "success": False,
            "error": status,
            "results": [],
            "execution_time": 0,
            "method": "fast",
            "applicable": False,
            "suggestion": format_query_results_suggestion(query, "fast")
        }
    
    try:
        start = time.time()
        
        # Tokenize query (BM25 needs tokens)
        tokens = query.lower().split()
        results = engine.search(tokens, top_k=top_k)
        
        execution_time = time.time() - start
        
        # Convert to dict format
        formatted_results = []
        graph, _ = load_graph()
        
        for result in results:
            model_uri = result.model_uri
            score = result.score
            
            # Extract metadata from graph
            metadata = extract_model_metadata(graph, model_uri)
            formatted_results.append({
                "model_uri": model_uri,
                "score": score,
                **metadata
            })
        
        return {
            "success": True,
            "results": formatted_results,
            "total_results": len(formatted_results),
            "execution_time": execution_time,
            "method": "fast",
            "sparql": None,
            "applicable": True,
            "confidence": "medium" if len(formatted_results) > 0 else "low"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Este método no puede procesar esta consulta",
            "results": [],
            "execution_time": 0,
            "method": "fast",
            "applicable": False,
            "suggestion": format_query_results_suggestion(query, "fast")
        }


def execute_smart_search(query: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Búsqueda Inteligente: Router (Hybrid para básicas, LLM para complejas)
    - Balance entre velocidad y precisión
    - Usa Hybrid (BM25+Dense) para queries simples
    - Usa LLM+RAG para queries complejas
    """
    # Determinar si es compleja
    is_complex = is_complex_query(query)
    
    if is_complex:
        # Usar LLM para queries complejas
        llm_engine, status = load_llm_engine()
        graph, _ = load_graph()
        
        if llm_engine is None or graph is None:
            return {
                "success": False,
                "error": status,
                "results": [],
                "execution_time": 0,
                "method": "smart",
                "sub_method": "llm",
                "applicable": False,
                "suggestion": format_query_results_suggestion(query, "smart")
            }
        
        try:
            start = time.time()
            
            # Convert to SPARQL
            conversion_result = llm_engine.convert(query, validate=False)
            
            if not conversion_result.is_valid:
                return {
                    "success": False,
                    "error": "Este método no puede procesar esta consulta. Prueba reformular tu pregunta.",
                    "results": [],
                    "execution_time": time.time() - start,
                    "method": "smart",
                    "sub_method": "llm",
                    "applicable": False,
                    "suggestion": format_query_results_suggestion(query, "smart")
                }
            
            # Execute SPARQL
            results = graph.query(conversion_result.sparql_query)
            
            execution_time = time.time() - start
            
            # Format results
            formatted_results = format_sparql_results(graph, results, query, top_k)
            
            return {
                "success": True,
                "results": formatted_results,
                "total_results": len(formatted_results),
                "execution_time": execution_time,
                "method": "smart",
                "sub_method": "llm",
                "sparql": conversion_result.sparql_query,
                "applicable": True,
                "confidence": conversion_result.confidence
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Este método no puede procesar esta consulta completamente.",
                "results": [],
                "execution_time": 0,
                "method": "smart",
                "sub_method": "llm",
                "applicable": False,
                "suggestion": format_query_results_suggestion(query, "smart")
            }
    
    else:
        # Usar Hybrid para queries simples
        engine, status = load_hybrid_engine()
        
        if engine is None:
            return {
                "success": False,
                "error": status,
                "results": [],
                "execution_time": 0,
                "method": "smart",
                "sub_method": "hybrid",
                "applicable": False,
                "suggestion": format_query_results_suggestion(query, "smart")
            }
        
        try:
            start = time.time()
            
            results = engine.search(query, top_k=top_k)
            
            execution_time = time.time() - start
            
            # Convert to dict format
            formatted_results = []
            graph, _ = load_graph()
            
            for result in results:
                model_uri = result.model_uri
                score = result.combined_score
                
                # Extract metadata from graph
                metadata = extract_model_metadata(graph, model_uri)
                formatted_results.append({
                    "model_uri": model_uri,
                    "score": score,
                    "bm25_score": result.bm25_score,
                    "dense_score": result.dense_score,
                    **metadata
                })
            
            return {
                "success": True,
                "results": formatted_results,
                "total_results": len(formatted_results),
                "execution_time": execution_time,
                "method": "smart",
                "sub_method": "hybrid",
                "sparql": None,
                "applicable": True,
                "confidence": "high" if len(formatted_results) > 0 else "medium"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Este método no puede procesar esta consulta.",
                "results": [],
                "execution_time": 0,
                "method": "smart",
                "sub_method": "hybrid",
                "applicable": False,
                "suggestion": format_query_results_suggestion(query, "smart")
            }


def execute_expert_search(query: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Búsqueda Experta: LLM + Ontology Dictionary + RAG
    - Más lento (~3-6s)
    - Comprensión semántica completa
    - Ideal para queries complejas y agregaciones
    """
    llm_engine, status = load_llm_engine()
    graph, _ = load_graph()
    
    if llm_engine is None or graph is None:
        return {
            "success": False,
            "error": status,
            "results": [],
            "execution_time": 0,
            "method": "expert",
            "applicable": False,
            "suggestion": format_query_results_suggestion(query, "expert")
        }
    
    try:
        start = time.time()
        
        # Convert to SPARQL
        conversion_result = llm_engine.convert(query, validate=False)
        
        if not conversion_result.is_valid:
            return {
                "success": False,
                "error": "Este método no puede procesar esta consulta en su forma actual.",
                "results": [],
                "execution_time": time.time() - start,
                "method": "expert",
                "applicable": False,
                "suggestion": format_query_results_suggestion(query, "expert")
            }
        
        # Execute SPARQL
        results = graph.query(conversion_result.sparql_query)
        
        execution_time = time.time() - start
        
        # Format results
        formatted_results = format_sparql_results(graph, results, query, top_k)
        
        return {
            "success": True,
            "results": formatted_results,
            "total_results": len(formatted_results),
            "execution_time": execution_time,
            "method": "expert",
            "sparql": conversion_result.sparql_query,
            "applicable": True,
            "confidence": conversion_result.confidence,
            "retrieved_examples": conversion_result.retrieved_examples
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Este método no es aplicable para esta consulta específica.",
            "results": [],
            "execution_time": 0,
            "method": "expert",
            "applicable": False,
            "suggestion": format_query_results_suggestion(query, "expert")
        }


# ==================== HELPER FUNCTIONS ====================

def extract_model_metadata(graph: Graph, model_uri: str) -> Dict[str, Any]:
    """Extrae metadata de un modelo desde el grafo"""
    DAIMO = Namespace("http://purl.org/pionera/daimo#")
    DCTERMS = Namespace("http://purl.org/dc/terms/")
    
    from rdflib import URIRef, Literal
    
    model_ref = URIRef(model_uri)
    
    metadata = {
        "title": None,
        "source": None,
        "task": None,
        "library": None,
        "domain": None,
        "rating": 0,
        "downloads": 0
    }
    
    # Extract properties
    for pred, obj in graph.predicate_objects(model_ref):
        pred_str = str(pred)
        obj_str = str(obj)
        
        if "title" in pred_str.lower() or "name" in pred_str.lower():
            metadata["title"] = obj_str
        elif "source" in pred_str.lower():
            metadata["source"] = obj_str
        elif "task" in pred_str.lower():
            metadata["task"] = obj_str
        elif "library" in pred_str.lower():
            metadata["library"] = obj_str
        elif "domain" in pred_str.lower():
            metadata["domain"] = obj_str
        elif "rating" in pred_str.lower() or "score" in pred_str.lower():
            try:
                metadata["rating"] = float(obj_str)
            except:
                pass
        elif "downloads" in pred_str.lower():
            try:
                metadata["downloads"] = int(float(obj_str))
            except:
                pass
    
    # Default title if not found
    if not metadata["title"]:
        metadata["title"] = model_uri.split("#")[-1].split("/")[-1]
    
    return metadata


def format_sparql_results(graph: Graph, results: Any, query: str, top_k: int) -> List[Dict[str, Any]]:
    """
    Formatea resultados de SPARQL según el tipo de query
    - Listado: devuelve modelos con metadata
    - Agregación: devuelve tabla agregada
    """
    formatted_results = []
    
    # Detectar tipo de query
    query_type, _ = detect_query_type(query)
    
    if query_type == "aggregation":
        # Para agregaciones, retornar los valores tal cual
        for row in results:
            result_dict = {}
            for var in results.vars:
                value = row[var]
                result_dict[str(var)] = str(value) if value else "N/A"
            formatted_results.append(result_dict)
    else:
        # Para listados, extraer URIs y metadata
        count = 0
        for row in results:
            if count >= top_k:
                break
            
            # Try to find model URI in row
            model_uri = None
            for value in row:
                value_str = str(value)
                if "http" in value_str and "#" in value_str:
                    model_uri = value_str
                    break
            
            if model_uri:
                metadata = extract_model_metadata(graph, model_uri)
                formatted_results.append({
                    "model_uri": model_uri,
                    "score": count + 1,  # Rank as score
                    **metadata
                })
                count += 1
    
    return formatted_results


# ==================== MAIN APP ====================

def main():
    st.title("🔍 Búsqueda Multi-Método")
    st.markdown("Elige entre 3 métodos de búsqueda según tus necesidades: rapidez, balance o precisión máxima.")
    
    # Initialize session state
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    if "current_results" not in st.session_state:
        st.session_state.current_results = {}
    
    # Sidebar con configuración
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        
        # Method Selection
        st.markdown("#### 🎯 Método de Búsqueda")
        
        search_methods = {
            "fast": {
                "name": "⚡ Rápida",
                "description": "BM25 - Búsqueda por palabras clave (~1ms)",
                "icon": "⚡",
                "best_for": "Búsquedas simples y listados"
            },
            "smart": {
                "name": "🎯 Inteligente",
                "description": "Router - Hybrid o LLM según complejidad (~100-1000ms)",
                "icon": "🎯",
                "best_for": "Queries variadas con filtros"
            },
            "expert": {
                "name": "🧠 Experta",
                "description": "LLM+RAG - Comprensión semántica completa (~3-6s)",
                "icon": "🧠",
                "best_for": "Agregaciones y queries complejas"
            }
        }
        
        selected_method = st.radio(
            "Selecciona método:",
            options=list(search_methods.keys()),
            format_func=lambda x: search_methods[x]["name"],
            help="Cada método tiene diferentes fortalezas"
        )
        
        # Show method info
        method_info = search_methods[selected_method]
        st.info(f"""
        **{method_info['icon']} {method_info['description']}**
        
        ✅ Mejor para: {method_info['best_for']}
        """)
        
        st.markdown("---")
        
        # Additional settings
        max_results = st.slider(
            "Máximo de resultados",
            min_value=5,
            max_value=50,
            value=10,
            step=5
        )
        
        show_sparql = st.checkbox("Mostrar SPARQL generado", value=True)
        show_metadata = st.checkbox("Mostrar metadata completa", value=False)
        compare_mode = st.checkbox("Modo comparación (ejecutar 3 métodos)", value=False)
        
        st.markdown("---")
        
        # Graph stats
        graph, graph_status = load_graph()
        st.markdown("### 📊 Catálogo")
        if graph:
            DAIMO = Namespace("http://purl.org/pionera/daimo#")
            from rdflib import RDF
            
            # Count models
            model_count = sum(1 for _ in graph.subjects(RDF.type, DAIMO.Model))
            st.metric("Total modelos", f"{model_count:,}")
            st.metric("Total triples", f"{len(graph):,}")
        else:
            st.warning(graph_status)
    
    # Ejemplos por categoría
    st.markdown("### 💡 Ejemplos por Categoría")
    
    example_tabs = st.tabs(["📋 Listados", "📊 Agregaciones", "🔍 Filtros Complejos"])
    
    with example_tabs[0]:
        st.markdown("**Consultas de listado simple:**")
        list_examples = [
            "list all AI models",
            "PyTorch models for NLP",
            "models from HuggingFace"
        ]
        selected_list = None
        cols = st.columns(3)
        for i, ex in enumerate(list_examples):
            with cols[i]:
                if st.button(f"📌 {ex}", key=f"list_{i}", use_container_width=True):
                    selected_list = ex
    
    with example_tabs[1]:
        st.markdown("**Consultas de agregación:**")
        agg_examples = [
            "count models by task",
            "average rating of computer vision models",
            "total downloads by framework"
        ]
        selected_agg = None
        cols = st.columns(3)
        for i, ex in enumerate(agg_examples):
            with cols[i]:
                if st.button(f"📊 {ex}", key=f"agg_{i}", use_container_width=True):
                    selected_agg = ex
    
    with example_tabs[2]:
        st.markdown("**Filtros complejos:**")
        complex_examples = [
            "top 10 PyTorch models by rating",
            "high rated computer vision models with more than 1000 downloads",
            "models from HuggingFace ordered by popularity"
        ]
        selected_complex = None
        cols = st.columns(3)
        for i, ex in enumerate(complex_examples):
            with cols[i]:
                if st.button(f"🔍 {ex}", key=f"complex_{i}", use_container_width=True):
                    selected_complex = ex
    
    # Select example if clicked
    selected_example = selected_list or selected_agg or selected_complex
    
    st.markdown("---")
    
    # Input de búsqueda
    query = st.text_input(
        "🔍 Tu consulta:",
        value=selected_example if selected_example else "",
        placeholder="Ej: PyTorch models for computer vision",
        help="Escribe en lenguaje natural (español o inglés)"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        search_button = st.button("🚀 Buscar", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Limpiar", use_container_width=True)
    
    if clear_button:
        st.session_state.current_results = {}
        st.rerun()
    
    # Ejecutar búsqueda
    if search_button and query:
        
        if compare_mode:
            # Execute all 3 methods
            st.markdown("---")
            st.markdown("## 🔄 Modo Comparación: Ejecutando 3 métodos...")
            
            with st.spinner("Ejecutando búsquedas..."):
                fast_result = execute_fast_search(query, max_results)
                smart_result = execute_smart_search(query, max_results)
                expert_result = execute_expert_search(query, max_results)
            
            # Show comparison
            st.markdown("### 📊 Resultados Comparativos")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### ⚡ Rápida")
                if fast_result["success"]:
                    st.success(f"✅ {fast_result['total_results']} resultados")
                    st.metric("⏱️ Tiempo", f"{fast_result['execution_time']*1000:.1f}ms")
                    st.metric("🎯 Confianza", fast_result.get("confidence", "N/A"))
                else:
                    st.error("❌ No aplicable")
                    if fast_result.get("suggestion"):
                        st.info(fast_result["suggestion"])
            
            with col2:
                st.markdown("#### 🎯 Inteligente")
                if smart_result["success"]:
                    st.success(f"✅ {smart_result['total_results']} resultados")
                    st.metric("⏱️ Tiempo", f"{smart_result['execution_time']*1000:.1f}ms")
                    st.metric("🎯 Confianza", smart_result.get("confidence", "N/A"))
                    sub_method = smart_result.get("sub_method", "N/A")
                    st.info(f"Método usado: {sub_method}")
                else:
                    st.error("❌ No aplicable")
                    if smart_result.get("suggestion"):
                        st.info(smart_result["suggestion"])
            
            with col3:
                st.markdown("#### 🧠 Experta")
                if expert_result["success"]:
                    st.success(f"✅ {expert_result['total_results']} resultados")
                    st.metric("⏱️ Tiempo", f"{expert_result['execution_time']*1000:.1f}ms")
                    st.metric("🎯 Confianza", expert_result.get("confidence", "N/A"))
                else:
                    st.error("❌ No aplicable")
                    if expert_result.get("suggestion"):
                        st.info(expert_result["suggestion"])
            
            # Store all results
            st.session_state.current_results = {
                "fast": fast_result,
                "smart": smart_result,
                "expert": expert_result
            }
            
            # Show best result
            best_method = None
            best_count = 0
            
            for method, result in st.session_state.current_results.items():
                if result["success"] and result["total_results"] > best_count:
                    best_method = method
                    best_count = result["total_results"]
            
            if best_method:
                st.markdown("---")
                st.markdown(f"### 🏆 Mostrando resultados del mejor método: **{search_methods[best_method]['name']}**")
                display_results(st.session_state.current_results[best_method], query, show_sparql, show_metadata)
            
        else:
            # Execute only selected method
            st.markdown("---")
            
            with st.spinner(f"🔄 Ejecutando búsqueda {search_methods[selected_method]['icon']}..."):
                if selected_method == "fast":
                    result = execute_fast_search(query, max_results)
                elif selected_method == "smart":
                    result = execute_smart_search(query, max_results)
                else:  # expert
                    result = execute_expert_search(query, max_results)
            
            # Store result
            st.session_state.current_results = {selected_method: result}
            
            # Add to history
            st.session_state.search_history.insert(0, {
                "query": query,
                "method": selected_method,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": result["total_results"] if result["success"] else 0,
                "time": result["execution_time"]
            })
            st.session_state.search_history = st.session_state.search_history[:5]  # Keep last 5
            
            # Display result
            display_results(result, query, show_sparql, show_metadata)
    
    elif search_button:
        st.warning("⚠️ Por favor escribe una consulta")
    
    # Search history
    if st.session_state.search_history:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 📜 Historial Reciente")
            for i, entry in enumerate(st.session_state.search_history[:5]):
                with st.expander(f"{i+1}. {entry['query'][:30]}...", expanded=False):
                    st.text(f"Método: {search_methods[entry['method']]['icon']}")
                    st.text(f"Resultados: {entry['results']}")
                    st.text(f"Tiempo: {entry['time']*1000:.1f}ms")
                    st.text(f"Hora: {entry['timestamp']}")


def display_results(result: Dict[str, Any], query: str, show_sparql: bool, show_metadata: bool):
    """Muestra los resultados de una búsqueda"""
    
    if not result["success"]:
        st.error(f"❌ {result.get('error', 'Error desconocido')}")
        
        if result.get("suggestion"):
            st.markdown(result["suggestion"])
        
        return
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Resultados", result["total_results"])
    with col2:
        st.metric("⏱️ Tiempo", f"{result['execution_time']*1000:.1f}ms")
    with col3:
        confidence = result.get("confidence", "N/A")
        confidence_color = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(confidence, "⚪")
        st.metric("🎯 Confianza", f"{confidence_color} {confidence}")
    with col4:
        method_name = {
            "fast": "⚡ Rápida",
            "smart": "🎯 Inteligente",
            "expert": "🧠 Experta"
        }.get(result["method"], result["method"])
        st.metric("🔧 Método", method_name)
    
    # SPARQL generado
    if show_sparql and result.get("sparql"):
        with st.expander("📝 SPARQL generado", expanded=False):
            st.code(result["sparql"], language="sparql")
            
            if result.get("retrieved_examples"):
                st.info(f"📚 Ejemplos RAG usados: {', '.join(result['retrieved_examples'][:3])}")
    
    st.markdown("---")
    
    # Detectar tipo de query y mostrar resultados apropiadamente
    query_type, type_desc = detect_query_type(query, result.get("sparql"))
    
    st.info(f"📊 **Tipo de consulta detectado**: {type_desc}")
    
    if result["total_results"] == 0:
        st.info("ℹ️ No se encontraron resultados para tu búsqueda")
        return
    
    if query_type == "aggregation":
        # Mostrar como tabla para agregaciones
        st.markdown(f"### 📊 Resultados de Agregación")
        
        df = pd.DataFrame(result["results"])
        
        # Renombrar columnas para que sean más legibles
        col_mapping = {
            "count": "Cantidad",
            "sum": "Suma",
            "avg": "Promedio",
            "max": "Máximo",
            "min": "Mínimo",
            "task": "Tarea",
            "framework": "Framework",
            "library": "Biblioteca",
            "source": "Fuente"
        }
        
        df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
        
        st.dataframe(df, use_container_width=True, height=400)
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar tabla (CSV)",
            data=csv,
            file_name=f"aggregation_results_{int(time.time())}.csv",
            mime="text/csv",
        )
        
    else:
        # Mostrar como listado de modelos
        st.markdown(f"### 📋 Top {len(result['results'])} Modelos")
        
        for i, model_result in enumerate(result["results"], 1):
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    model_uri = model_result.get("model_uri", "N/A")
                    title = model_result.get("title", model_uri.split("#")[-1] if "#" in model_uri else "Sin título")
                    source = model_result.get("source", "N/A")
                    task = model_result.get("task", "N/A")
                    
                    st.markdown(f"""
                    <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                                border-left: 4px solid #1E88E5; margin: 1rem 0; 
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="margin: 0; color: #1E88E5;">{i}. {title}</h3>
                        <p style="color: #666; margin: 0.5rem 0;">
                            📦 <strong>Repositorio:</strong> {source} | 
                            🎯 <strong>Tarea:</strong> {task}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    score = model_result.get("score", 0)
                    st.metric("⭐ Score", f"{float(score):.2f}")
                
                if show_metadata:
                    with st.expander("📋 Metadata completa"):
                        metadata_col1, metadata_col2 = st.columns(2)
                        
                        with metadata_col1:
                            library = model_result.get("library", "N/A")
                            domain = model_result.get("domain", "N/A")
                            st.markdown(f"""
                            - **Biblioteca**: {library}
                            - **Dominio**: {domain}
                            """)
                        
                        with metadata_col2:
                            downloads = model_result.get("downloads", 0)
                            rating = model_result.get("rating", 0)
                            st.markdown(f"""
                            - **Downloads**: {int(downloads):,}
                            - **Rating**: {float(rating):.2f} ⭐
                            - **URI**: `{model_uri.split('#')[-1] if '#' in model_uri else model_uri}`
                            """)
                            
                            # Show BM25 and Dense scores if available (for smart/hybrid)
                            if "bm25_score" in model_result:
                                st.markdown(f"""
                                - **BM25 Score**: {model_result['bm25_score']:.3f}
                                - **Dense Score**: {model_result['dense_score']:.3f}
                                """)
        
        # Download results as JSON
        json_str = json.dumps(result["results"], indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Descargar resultados (JSON)",
            data=json_str,
            file_name=f"search_results_{int(time.time())}.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
