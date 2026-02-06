"""
Página de Gestión de Datos - Descarga y construcción del grafo RDF

Permite descargar modelos de múltiples repositorios y construir el grafo de conocimiento

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import json

# Configurar path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rdflib import Graph

st.set_page_config(
    page_title="Gestión de Datos - AI Model Discovery",
    page_icon="📥",
    layout="wide"
)


def get_repository_collectors():
    """Obtener instancias de todos los repositorios"""
    try:
        from utils.huggingface_repository import HuggingFaceRepository
        from utils.kaggle_repository import KaggleRepository
        from utils.civitai_repository import CivitaiRepository
        from utils.replicate_repository import ReplicateRepository
        from utils.tensorflow_hub_repository import TensorFlowHubRepository
        from utils.pytorch_hub_repository import PyTorchHubRepository
        from utils.paperswithcode_repository import PapersWithCodeRepository
        
        return {
            'HuggingFace': HuggingFaceRepository(),
            'Kaggle': KaggleRepository(),
            'Civitai': CivitaiRepository(),
            'Replicate': ReplicateRepository(),
            'TensorFlow Hub': TensorFlowHubRepository(),
            'PyTorch Hub': PyTorchHubRepository(),
            'PapersWithCode': PapersWithCodeRepository()
        }
    except ImportError as e:
        st.error(f"❌ Error importando repositorios: {e}")
        return {}


def save_graph(graph: Graph, filename: str = "ai_models_multi_repo.ttl"):
    """Guardar grafo RDF a disco"""
    output_dir = project_root / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / filename
    graph.serialize(destination=str(output_path), format="turtle")
    
    return output_path


def load_existing_graph():
    """Cargar grafo existente si existe"""
    graph_path = project_root / "data" / "ai_models_multi_repo.ttl"
    
    if graph_path.exists():
        try:
            g = Graph()
            g.parse(str(graph_path), format="turtle")
            return g, graph_path
        except Exception as e:
            # Si el grafo está corrupto, mejor ignorarlo
            st.sidebar.error(f"⚠️ Grafo corrupto detectado: {str(e)[:100]}")
            st.sidebar.info("💡 Se creará un nuevo grafo al descargar modelos")
            return None, graph_path
    
    return None, None


def main():
    st.title("📥 Gestión de Datos")
    st.markdown("Descarga modelos de múltiples repositorios y construye el grafo de conocimiento RDF")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["📥 Descargar Modelos", "📊 Grafo Actual", "⚙️ Configuración"])
    
    # ==================== TAB 1: DESCARGAR MODELOS ====================
    with tab1:
        st.markdown("### 🔄 Descarga de Modelos")
        
        # Información del estado actual
        existing_graph, graph_path = load_existing_graph()
        
        if existing_graph:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Grafo Existente", "✅ Cargado")
            with col2:
                st.metric("🔢 Triples", f"{len(existing_graph):,}")
            with col3:
                st.metric("📁 Ubicación", graph_path.name)
            
            st.warning(f"⚠️ Al descargar nuevos modelos, el grafo actual será **reemplazado completamente**")
            st.info(f"📂 Ubicación actual: `{graph_path}`")
        else:
            st.info("ℹ️ No hay grafo existente. Se creará uno nuevo con los modelos descargados.")
        
        st.markdown("---")
        
        # Configuración de descarga
        st.markdown("### ⚙️ Configuración de Descarga")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Repositorios a descargar")
            
            repos_config = {
                'HuggingFace': st.checkbox("🤗 HuggingFace", value=True, help="Modelos NLP, CV, Audio"),
                'Kaggle': st.checkbox("🏅 Kaggle", value=True, help="Datasets y modelos de competencias"),
                'Civitai': st.checkbox("🎨 Civitai", value=False, help="Modelos generativos (NSFW posible)"),
                'Replicate': st.checkbox("🔁 Replicate", value=True, help="Modelos cloud-deployed"),
                'TensorFlow Hub': st.checkbox("🔌 TensorFlow Hub", value=True, help="Modelos TensorFlow"),
                'PyTorch Hub': st.checkbox("🔥 PyTorch Hub", value=True, help="Modelos PyTorch"),
                'PapersWithCode': st.checkbox("📚 PapersWithCode", value=True, help="Modelos académicos")
            }
            
            selected_repos = [repo for repo, selected in repos_config.items() if selected]
            st.info(f"✅ {len(selected_repos)} repositorios seleccionados")
        
        with col2:
            st.markdown("#### Parámetros de descarga")
            
            models_per_repo = st.slider(
                "Modelos por repositorio",
                min_value=5,
                max_value=100,
                value=20,
                step=5,
                help="Número de modelos a descargar de cada repositorio"
            )
            
            total_expected = models_per_repo * len(selected_repos)
            st.metric("📊 Total esperado", f"{total_expected} modelos")
            
            st.info("💡 Al descargar, el sistema siempre reemplaza el grafo existente con los nuevos datos")
            
            graph_filename = st.text_input(
                "Nombre del archivo",
                value="ai_models_multi_repo.ttl",
                help="Nombre del archivo RDF a guardar (ubicación: data/)"
            )
        
        st.markdown("---")
        
        # Botón de descarga
        col1, col2, col3 = st.columns([1, 1, 2])
        
        # Verificar si hay grafo existente para mostrar advertencia
        existing_graph_check, _ = load_existing_graph()
        
        with col1:
            download_button = st.button(
                "🚀 Iniciar Descarga",
                type="primary",
                use_container_width=True,
                disabled=len(selected_repos) == 0
            )
        
        with col2:
            if st.button("🗑️ Limpiar Caché", use_container_width=True):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("✅ Caché limpiado")
                st.rerun()
        
        # Mostrar confirmación si existe grafo
        confirm_download = True
        if download_button and existing_graph_check:
            st.warning("⚠️ **ADVERTENCIA**: Ya existe un grafo con datos. Al continuar, será **eliminado y reemplazado**.")
            confirm_download = st.checkbox(
                "✅ Confirmo que quiero eliminar el grafo existente y crear uno nuevo",
                value=False
            )
            if not confirm_download:
                st.info("💡 Marca la casilla para confirmar y continuar con la descarga")
        
        # Proceso de descarga
        if download_button and confirm_download:
            st.markdown("---")
            st.markdown("### 🔄 Descargando Modelos...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Inicializar resultados
            all_models = {}
            errors = []
            
            # Obtener repositorios
            repositories = get_repository_collectors()
            
            if not repositories:
                st.error("❌ No se pudieron cargar los repositorios")
                return
            
            # Descargar de cada repositorio
            for idx, repo_name in enumerate(selected_repos):
                progress = (idx + 1) / len(selected_repos)
                progress_bar.progress(progress)
                status_text.markdown(f"**Descargando de {repo_name}...** ({idx + 1}/{len(selected_repos)})")
                
                try:
                    repo = repositories[repo_name]
                    
                    # Descargar modelos
                    if repo_name == 'HuggingFace':
                        models = repo.fetch_models(limit=models_per_repo, sort='downloads')
                    elif repo_name == 'Kaggle':
                        models = repo.fetch_models(limit=models_per_repo)
                    elif repo_name == 'Civitai':
                        models = repo.fetch_models(limit=models_per_repo, sort='Highest Rated')
                    elif repo_name == 'Replicate':
                        models = repo.fetch_models(limit=models_per_repo, sort_by='latest_version_created_at')
                    elif repo_name == 'TensorFlow Hub':
                        models = repo.fetch_models(limit=models_per_repo)
                    elif repo_name == 'PyTorch Hub':
                        models = repo.fetch_models(limit=models_per_repo)
                    elif repo_name == 'PapersWithCode':
                        models = repo.fetch_models(limit=models_per_repo, min_papers=1)
                    
                    all_models[repo_name] = (repo, models)
                    st.success(f"✅ {repo_name}: {len(models)} modelos")
                    
                except Exception as e:
                    error_msg = f"{repo_name}: {str(e)[:100]}"
                    errors.append(error_msg)
                    st.error(f"❌ {error_msg}")
                    all_models[repo_name] = (repo, [])
            
            progress_bar.progress(1.0)
            status_text.markdown("**✅ Descarga completada**")
            
            # Construir grafo RDF
            st.markdown("---")
            st.markdown("### 🔨 Construyendo Grafo RDF...")
            
            try:
                from knowledge_graph.multi_repository_builder import MultiRepositoryGraphBuilder
                
                # Verificar si existe grafo previo
                graph_path_check = project_root / "data" / graph_filename
                if graph_path_check.exists():
                    st.warning(f"⚠️ Grafo existente encontrado: `{graph_filename}`")
                    st.info("🗑️ Eliminando grafo anterior...")
                    graph_path_check.unlink()
                    st.success("✅ Grafo anterior eliminado")
                
                # Crear nuevo grafo desde cero
                builder = MultiRepositoryGraphBuilder()
                st.info("📝 Creando nuevo grafo desde cero")
                
                # Agregar modelos al grafo
                total_added = 0
                for repo_name, (repo, models) in all_models.items():
                    if models:
                        builder.add_repository(repo)
                        for model in models:
                            builder.add_standardized_model(model, repository=repo)
                        total_added += len(models)
                
                # Obtener grafo final
                final_graph = builder.graph
                
                # Guardar grafo
                st.info("💾 Guardando nuevo grafo...")
                saved_path = save_graph(final_graph, graph_filename)
                
                # Limpiar caché para forzar recarga en otras páginas
                st.cache_resource.clear()
                st.success("🔄 Caché limpiado - otras páginas usarán el nuevo grafo")
                
                # Resultados finales
                st.markdown("---")
                st.markdown("### 🎉 Grafo Construido Exitosamente")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Total Modelos", total_added)
                with col2:
                    st.metric("🔢 Total Triples", f"{len(final_graph):,}")
                with col3:
                    st.metric("📦 Repositorios", len([m for m in all_models.values() if m[1]]))
                with col4:
                    st.metric("💾 Archivo", saved_path.name)
                
                st.success(f"✅ Grafo guardado en: `{saved_path}`")
                
                # Mostrar errores si los hay
                if errors:
                    with st.expander("⚠️ Errores durante la descarga"):
                        for error in errors:
                            st.warning(error)
                
                # Botón para ir a búsqueda
                if st.button("🔍 Ir a Búsqueda", type="primary"):
                    st.switch_page("pages/1_🔍_Búsqueda.py")
                
            except Exception as e:
                st.error(f"❌ Error construyendo grafo: {e}")
                import traceback
                with st.expander("Ver traceback completo"):
                    st.code(traceback.format_exc())
    
    # ==================== TAB 2: GRAFO ACTUAL ====================
    with tab2:
        st.markdown("### 📊 Grafo RDF Actual")
        
        existing_graph, graph_path = load_existing_graph()
        
        if not existing_graph:
            st.warning("⚠️ No hay grafo cargado. Ve a la pestaña 'Descargar Modelos' para crear uno.")
            return
        
        # Estadísticas del grafo
        st.markdown("#### 📈 Estadísticas Generales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Contar modelos y repositorios
        from rdflib import Namespace
        from rdflib.namespace import RDF
        
        DAIMO = Namespace("http://purl.org/pionera/daimo#")
        
        models = list(existing_graph.subjects(RDF.type, DAIMO.AIModel))
        total_models = len(models)
        
        # Contar repositorios únicos
        repos = set()
        for model in models:
            source = existing_graph.value(model, DAIMO.source)
            if source:
                repos.add(str(source))
        
        with col1:
            st.metric("🤖 Total Modelos", f"{total_models:,}")
        with col2:
            st.metric("🔢 Total Triples", f"{len(existing_graph):,}")
        with col3:
            st.metric("📦 Repositorios", len(repos))
        with col4:
            st.metric("📁 Archivo", graph_path.name if graph_path else "N/A")
        
        st.markdown("---")
        
        # Distribución por repositorio
        st.markdown("#### 📦 Distribución por Repositorio")
        
        repo_counts = {}
        for model in models:
            source = existing_graph.value(model, DAIMO.source)
            if source:
                source_str = str(source)
                repo_counts[source_str] = repo_counts.get(source_str, 0) + 1
        
        if repo_counts:
            repo_df = pd.DataFrame([
                {"Repositorio": repo, "Modelos": count}
                for repo, count in sorted(repo_counts.items(), key=lambda x: x[1], reverse=True)
            ])
            
            st.dataframe(
                repo_df,
                use_container_width=True,
                hide_index=True
            )
        
        st.markdown("---")
        
        # Información del archivo
        st.markdown("#### 📁 Información del Archivo")
        
        if graph_path and graph_path.exists():
            file_size = graph_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            modified_time = datetime.fromtimestamp(graph_path.stat().st_mtime)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💾 Tamaño", f"{file_size_mb:.2f} MB")
            with col2:
                st.metric("📅 Modificado", modified_time.strftime("%Y-%m-%d"))
            with col3:
                st.metric("🕐 Hora", modified_time.strftime("%H:%M:%S"))
            
            st.info(f"📂 Ruta completa: `{graph_path}`")
        
        # Acciones
        st.markdown("---")
        st.markdown("#### 🔧 Acciones")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Recargar Grafo", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Grafo recargado")
                st.rerun()
        
        with col2:
            if st.button("📥 Descargar Grafo", use_container_width=True):
                if graph_path and graph_path.exists():
                    with open(graph_path, 'rb') as f:
                        st.download_button(
                            "⬇️ Descargar TTL",
                            f,
                            file_name=graph_path.name,
                            mime="text/turtle"
                        )
        
        with col3:
            if st.button("🗑️ Eliminar Grafo", use_container_width=True, type="secondary"):
                if graph_path and graph_path.exists():
                    if st.checkbox("⚠️ Confirmar eliminación"):
                        graph_path.unlink()
                        st.success("✅ Grafo eliminado")
                        st.rerun()
    
    # ==================== TAB 3: CONFIGURACIÓN ====================
    with tab3:
        st.markdown("### ⚙️ Configuración Avanzada")
        
        st.markdown("#### 📋 Repositorios Disponibles")
        
        repos_info = {
            'HuggingFace': {
                'icon': '🤗',
                'description': 'Modelos de NLP, Computer Vision, Audio',
                'api': 'huggingface-hub',
                'propiedades': 15
            },
            'Kaggle': {
                'icon': '🏅',
                'description': 'Datasets y modelos de competencias ML',
                'api': 'kaggle',
                'propiedades': 15
            },
            'Civitai': {
                'icon': '🎨',
                'description': 'Modelos generativos (Stable Diffusion, etc.)',
                'api': 'REST API',
                'propiedades': 16
            },
            'Replicate': {
                'icon': '🔁',
                'description': 'Modelos cloud-deployed con API',
                'api': 'replicate',
                'propiedades': 15
            },
            'TensorFlow Hub': {
                'icon': '🔌',
                'description': 'Modelos pre-entrenados TensorFlow',
                'api': 'REST API',
                'propiedades': 15
            },
            'PyTorch Hub': {
                'icon': '🔥',
                'description': 'Modelos pre-entrenados PyTorch',
                'api': 'REST API',
                'propiedades': 14
            },
            'PapersWithCode': {
                'icon': '📚',
                'description': 'Modelos académicos con papers',
                'api': 'REST API',
                'propiedades': 16
            }
        }
        
        for repo_name, info in repos_info.items():
            with st.expander(f"{info['icon']} {repo_name}"):
                st.markdown(f"**Descripción**: {info['description']}")
                st.markdown(f"**API**: `{info['api']}`")
                st.markdown(f"**Propiedades**: {info['propiedades']}")
        
        st.markdown("---")
        
        st.markdown("#### 🔧 Ontología DAIMO Actual")
        
        st.markdown("""
        **Ubicación**: `ontologies/daimo.ttl`
        
        **Propiedades**:
        - **DatatypeProperty**: 42 propiedades
        - **ObjectProperty**: 26 propiedades
        - **Total**: 68 propiedades definidas
        
        **Propiedades universales clave**:
        - `title`, `description`, `source`, `creator`
        - `task`, `accessLevel`, `sourceURL`
        - `downloads`, `likes`, `library`
        - `inferenceEndpoint`, `githubURL`
        
        **Propiedades específicas por repositorio**:
        - HuggingFace: `safetensors`, `cardData`, `isGated`
        - Replicate: `runCount`, `versionId`, `cogVersion`
        - Civitai: `isNSFW`, `isPOI`, `triggerWords`, `baseModel`
        - PapersWithCode: `arxivId`, `paper`, `yearIntroduced`, `isOfficial`
        - PyTorch Hub: `hubRepo`, `entryPoint`
        - TensorFlow Hub: `tfhubHandle`, `fineTunable`, `modelFormat`
        
        **Grafo RDF generado**: `data/ai_models_multi_repo.ttl`
        """)
        
        st.markdown("---")
        
        st.markdown("#### 📚 Documentación Técnica")
        
        st.markdown("""
        - **Ontología**: `ontologies/daimo.ttl` (68 propiedades)
        - **Grafo RDF**: `data/ai_models_multi_repo.ttl` (generado por esta página)
        - **Validación**: Scripts en raíz del proyecto (`validate_*.py`)
        - **RAG Examples**: `llm/rag_sparql_examples.py` (24 ejemplos SPARQL)
        """)


if __name__ == "__main__":
    main()
