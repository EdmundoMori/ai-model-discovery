"""
Página de Dashboard - Estadísticas del catálogo

Muestra métricas y visualizaciones del grafo RDF

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configurar path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rdflib import Graph
from search.non_federated import create_api


st.set_page_config(page_title="Dashboard - AI Model Discovery", page_icon="📊", layout="wide")


@st.cache_resource
def load_api():
    """Cargar API (cacheado)"""
    # Intentar cargar grafo real primero
    graph_path = project_root / "data" / "ai_models_multi_repo.ttl"
    
    if graph_path.exists():
        try:
            g = Graph()
            g.parse(str(graph_path), format="turtle")
            st.sidebar.success(f"✅ Grafo real: {len(g):,} triples")
        except Exception as e:
            st.sidebar.warning(f"⚠️ Error: {e}")
            from notebooks import create_test_graph
            g = create_test_graph()
            st.sidebar.info("📊 Grafo de prueba (70 modelos)")
    else:
        from notebooks import create_test_graph
        g = create_test_graph()
        st.sidebar.info("📊 Grafo de prueba (70 modelos)")
        st.sidebar.warning("💡 Descarga modelos reales en 'Gestión de Datos'")
    
    return create_api(graph=g)


def main():
    st.title("📊 Dashboard del Catálogo")
    st.markdown("Estadísticas y visualizaciones del grafo RDF de modelos de IA")
    
    # Cargar datos
    try:
        api = load_api()
        stats = api.get_statistics()
    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
        return
    
    # Métricas principales
    st.markdown("### 📈 Métricas Generales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🤖 Total Modelos",
            f"{stats['total_models']:,}",
            help="Número total de modelos en el catálogo"
        )
    
    with col2:
        st.metric(
            "📊 Total Triples",
            f"{stats['total_triples']:,}",
            help="Número de triples en el grafo RDF"
        )
    
    with col3:
        st.metric(
            "📦 Repositorios",
            len(stats['repositories']),
            help="Número de repositorios integrados"
        )
    
    with col4:
        st.metric(
            "🎯 Tareas Únicas",
            len(stats['tasks']),
            help="Tipos de tareas diferentes"
        )
    
    st.markdown("---")
    
    # Distribución por repositorio
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 Distribución por Repositorio")
        
        repo_df = pd.DataFrame([
            {"Repositorio": repo, "Modelos": count}
            for repo, count in stats['repositories'].items()
        ]).sort_values("Modelos", ascending=False)
        
        fig = px.bar(
            repo_df,
            x="Repositorio",
            y="Modelos",
            color="Modelos",
            color_continuous_scale="Blues",
            title="Modelos por Repositorio"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📚 Distribución por Biblioteca")
        
        lib_df = pd.DataFrame([
            {"Biblioteca": lib, "Modelos": count}
            for lib, count in stats['libraries'].items()
        ]).sort_values("Modelos", ascending=False)
        
        fig = px.pie(
            lib_df,
            values="Modelos",
            names="Biblioteca",
            title="Distribución de Bibliotecas",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Top tareas
    st.markdown("### 🎯 Top 10 Tareas Más Comunes")
    
    tasks_df = pd.DataFrame([
        {"Tarea": task, "Modelos": count}
        for task, count in sorted(
            stats['tasks'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    ])
    
    fig = px.bar(
        tasks_df,
        x="Modelos",
        y="Tarea",
        orientation="h",
        color="Modelos",
        color_continuous_scale="Viridis",
        title="Tareas con más modelos"
    )
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Distribución por nivel de acceso
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔐 Distribución por Nivel de Acceso")
        
        if stats['access_levels']:
            access_df = pd.DataFrame([
                {"Nivel de Acceso": level, "Modelos": count}
                for level, count in stats['access_levels'].items()
            ])
            
            if not access_df.empty:
                access_df = access_df.sort_values("Modelos", ascending=False)
                
                fig = px.pie(
                    access_df,
                    values="Modelos",
                    names="Nivel de Acceso",
                    title="Niveles de Acceso en el Catálogo",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de niveles de acceso disponibles")
        else:
            st.info("No hay datos de niveles de acceso disponibles")
    
    with col2:
        st.markdown("### 📋 Tabla de Niveles de Acceso")
        if stats['access_levels'] and stats['access_levels']:
            access_table_df = pd.DataFrame([
                {"Nivel de Acceso": level, "Modelos": count}
                for level, count in stats['access_levels'].items()
            ])
            if not access_table_df.empty:
                access_table_df = access_table_df.sort_values("Modelos", ascending=False)
                st.dataframe(
                    access_table_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No hay datos disponibles")
        else:
            st.info("No hay datos disponibles")
    
    st.markdown("---")
    
    # Tablas detalladas
    st.markdown("### 📊 Datos Detallados")
    
    tab1, tab2, tab3 = st.tabs(["📦 Repositorios", "🎯 Tareas", "📚 Bibliotecas"])
    
    with tab1:
        st.dataframe(
            repo_df,
            use_container_width=True,
            hide_index=True
        )
    
    with tab2:
        all_tasks_df = pd.DataFrame([
            {"Tarea": task, "Modelos": count}
            for task, count in sorted(
                stats['tasks'].items(),
                key=lambda x: x[1],
                reverse=True
            )
        ])
        st.dataframe(
            all_tasks_df,
            use_container_width=True,
            hide_index=True
        )
    
    with tab3:
        st.dataframe(
            lib_df,
            use_container_width=True,
            hide_index=True
        )


if __name__ == "__main__":
    main()
