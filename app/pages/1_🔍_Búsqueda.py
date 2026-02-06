"""
Página de Búsqueda - Interfaz de búsqueda semántica

Permite realizar búsquedas en lenguaje natural sobre el catálogo de modelos

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

import streamlit as st
import sys
from pathlib import Path
import time

# Configurar path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rdflib import Graph, Namespace
from search.non_federated import create_api


st.set_page_config(page_title="Búsqueda - AI Model Discovery", page_icon="🔍", layout="wide")


@st.cache_resource
def load_search_engine():
    """Cargar motor de búsqueda (cacheado)"""
    # Intentar cargar grafo real primero
    graph_path = project_root / "data" / "ai_models_multi_repo.ttl"
    
    if graph_path.exists():
        try:
            g = Graph()
            g.parse(str(graph_path), format="turtle")
            st.sidebar.success(f"✅ Grafo real cargado: {len(g):,} triples")
        except Exception as e:
            st.sidebar.warning(f"⚠️ Error cargando grafo: {e}")
            from notebooks import create_test_graph
            g = create_test_graph()
            st.sidebar.info("📊 Usando grafo de prueba (70 modelos)")
    else:
        # Crear grafo de prueba pequeño
        from notebooks import create_test_graph
        g = create_test_graph()
        st.sidebar.info("📊 Usando grafo de prueba (70 modelos)")
        st.sidebar.warning("💡 Ve a 'Gestión de Datos' para descargar modelos reales")
    
    return create_api(graph=g)


def main():
    st.title("🔍 Búsqueda Semántica")
    st.markdown("Escribe tu consulta en **lenguaje natural** y el sistema la convertirá a SPARQL automáticamente.")
    
    # Cargar motor de búsqueda
    try:
        api = load_search_engine()
        stats = api.get_statistics()
    except Exception as e:
        st.error(f"❌ Error cargando motor de búsqueda: {e}")
        st.info("💡 Ejecuta primero: `python -m knowledge_graph.build_graph`")
        return
    
    # Sidebar con configuración
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        
        max_results = st.slider(
            "Máximo de resultados",
            min_value=5,
            max_value=50,
            value=10,
            step=5
        )
        
        show_sparql = st.checkbox("Mostrar SPARQL generado", value=True)
        show_metadata = st.checkbox("Mostrar metadata completa", value=False)
        
        st.markdown("---")
        st.markdown("### 📊 Catálogo")
        st.metric("Total modelos", f"{stats['total_models']:,}")
        st.metric("Repositorios", len(stats['repositories']))
        st.metric("Tareas únicas", len(stats['tasks']))
    
    # Ejemplos rápidos
    st.markdown("### 💡 Ejemplos rápidos")
    example_cols = st.columns(3)
    
    examples = [
        "list all AI models",
        "PyTorch models for NLP",
        "high rated computer vision models",
        "models from HuggingFace",
        "most popular models by downloads",
        "count models by task"
    ]
    
    selected_example = None
    for i, example in enumerate(examples):
        col_idx = i % 3
        with example_cols[col_idx]:
            if st.button(f"📌 {example}", key=f"example_{i}", use_container_width=True):
                selected_example = example
    
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
        st.rerun()
    
    # Ejecutar búsqueda
    if search_button and query:
        with st.spinner("🔄 Convirtiendo query a SPARQL..."):
            time.sleep(0.5)  # UX
            
            try:
                results = api.search(
                    query=query,
                    max_results=max_results,
                    format="response"
                )
                
                # Resultados
                st.markdown("---")
                
                if not results.is_valid:
                    st.error("❌ Query inválida")
                    for error in results.errors:
                        st.warning(f"⚠️ {error}")
                    return
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Resultados", results.total_results)
                with col2:
                    st.metric("⏱️ Tiempo", f"{results.execution_time:.2f}s")
                with col3:
                    st.metric("📊 Mostrados", len(results.results))
                
                # SPARQL generado
                if show_sparql:
                    with st.expander("📝 SPARQL generado", expanded=False):
                        st.code(results.sparql_query, language="sparql")
                
                st.markdown("---")
                
                # Resultados
                if results.total_results == 0:
                    st.info("ℹ️ No se encontraron resultados para tu búsqueda")
                else:
                    st.markdown(f"### 📊 Top {len(results.results)} resultados")
                    
                    for i, result in enumerate(results.results, 1):
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; 
                                            border-left: 4px solid #1E88E5; margin: 1rem 0; 
                                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    <h3 style="margin: 0; color: #1E88E5;">{i}. {result.title}</h3>
                                    <p style="color: #666; margin: 0.5rem 0;">
                                        📦 <strong>Repositorio:</strong> {result.source} | 
                                        🎯 <strong>Tarea:</strong> {result.task}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.metric("⭐ Score", f"{result.score:.2f}")
                            
                            if show_metadata:
                                with st.expander("📋 Metadata completa"):
                                    metadata_col1, metadata_col2 = st.columns(2)
                                    
                                    with metadata_col1:
                                        st.markdown(f"""
                                        - **Biblioteca**: {result.metadata.get('library', 'N/A')}
                                        - **Dominio**: {result.metadata.get('domain', 'N/A')}
                                        - **Acceso**: {result.metadata.get('accessLevel', 'N/A')}
                                        """)
                                    
                                    with metadata_col2:
                                        downloads = result.metadata.get('downloads', 0)
                                        rating = result.metadata.get('rating', 0)
                                        st.markdown(f"""
                                        - **Downloads**: {int(downloads):,}
                                        - **Rating**: {float(rating):.2f} ⭐
                                        - **URI**: `{result.model_uri.split('#')[-1]}`
                                        """)
            
            except Exception as e:
                st.error(f"❌ Error ejecutando búsqueda: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    elif search_button:
        st.warning("⚠️ Por favor escribe una consulta")


if __name__ == "__main__":
    main()
