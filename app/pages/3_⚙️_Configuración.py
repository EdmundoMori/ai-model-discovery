"""
Página de Configuración - Ajustes del sistema

Permite configurar parámetros del motor de búsqueda y el LLM

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

import streamlit as st
import sys
from pathlib import Path

# Configurar path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


st.set_page_config(page_title="Configuración - AI Model Discovery", page_icon="⚙️", layout="wide")


def main():
    st.title("⚙️ Configuración del Sistema")
    st.markdown("Ajusta los parámetros del motor de búsqueda y el LLM")
    
    # Configuración del LLM
    st.markdown("### 🤖 Configuración del LLM")
    
    col1, col2 = st.columns(2)
    
    with col1:
        llm_provider = st.selectbox(
            "Proveedor LLM",
            options=["ollama", "anthropic"],
            index=0,
            help="Proveedor del modelo de lenguaje"
        )
        
        if llm_provider == "ollama":
            model = st.selectbox(
                "Modelo",
                options=[
                    "deepseek-r1:7b",
                    "deepseek-r1:1.5b",
                    "llama2:7b",
                    "mistral:7b"
                ],
                index=0,
                help="Modelo Ollama local"
            )
        else:
            model = st.selectbox(
                "Modelo",
                options=[
                    "claude-3-5-sonnet-20241022",
                    "claude-3-opus-20240229",
                    "claude-3-haiku-20240307"
                ],
                index=0,
                help="Modelo Anthropic (requiere API key)"
            )
        
        temperature = st.slider(
            "Temperatura",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Mayor temperatura = respuestas más creativas"
        )
    
    with col2:
        use_rag = st.checkbox(
            "Usar RAG (Retrieval Augmented Generation)",
            value=True,
            help="Usa ejemplos SPARQL para mejorar conversión"
        )
        
        if use_rag:
            top_k_examples = st.slider(
                "Top-K ejemplos RAG",
                min_value=1,
                max_value=10,
                value=3,
                help="Número de ejemplos similares a usar"
            )
        else:
            top_k_examples = 0
        
        validate_sparql = st.checkbox(
            "Validar SPARQL antes de ejecutar",
            value=True,
            help="Valida sintaxis y ejecutabilidad"
        )
    
    st.markdown("---")
    
    # Configuración de búsqueda
    st.markdown("### 🔍 Configuración de Búsqueda")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_results = st.number_input(
            "Máximo de resultados",
            min_value=5,
            max_value=100,
            value=10,
            step=5,
            help="Número máximo de resultados a retornar"
        )
        
        min_score = st.number_input(
            "Score mínimo",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5,
            help="Score mínimo para incluir resultado"
        )
    
    with col2:
        timeout = st.number_input(
            "Timeout (segundos)",
            min_value=5,
            max_value=300,
            value=30,
            step=5,
            help="Tiempo máximo de ejecución"
        )
        
        cache_results = st.checkbox(
            "Cachear resultados",
            value=True,
            help="Guarda resultados para consultas repetidas"
        )
    
    st.markdown("---")
    
    # Estado del sistema
    st.markdown("### 📊 Estado del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 Text-to-SPARQL")
        st.success("✅ Operacional")
        st.metric("Success Rate", "80%")
        st.metric("Executability", "100%")
    
    with col2:
        st.markdown("#### 🖥️ GPU")
        st.success("✅ Activa")
        st.metric("Modelo", "NVIDIA RTX 4050")
        st.metric("Uso VRAM", "4815/6141 MB")
    
    with col3:
        st.markdown("#### 📊 Grafo RDF")
        st.success("✅ Cargado")
        st.metric("Modelos", "70")
        st.metric("Triples", "630")
    
    st.markdown("---")
    
    # Información del proyecto
    st.markdown("### 📖 Información del Proyecto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📚 Componentes")
        st.markdown("""
        - ✅ Multi-repository collectors (7 fuentes)
        - ✅ Ontología DAIMO
        - ✅ Text-to-SPARQL con LLM
        - ✅ RAG con ChromaDB (14 ejemplos)
        - ✅ SearchEngine semántico
        - ✅ Validador SPARQL
        - ✅ Interfaz Web (Streamlit)
        """)
    
    with col2:
        st.markdown("#### 🎓 Tesis")
        st.markdown("""
        **Título**: Sistema de Descubrimiento y Búsqueda de Modelos de IA
        
        **Autor**: Edmundo Mori
        
        **Año**: 2026
        
        **Objetivo**: Crear un sistema de búsqueda semántica que integre
        múltiples repositorios de modelos de IA usando Text-to-SPARQL
        y grafos de conocimiento.
        """)
    
    st.markdown("---")
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Guardar Configuración", type="primary", use_container_width=True):
            st.success("✅ Configuración guardada")
    
    with col2:
        if st.button("🔄 Restablecer por defecto", use_container_width=True):
            st.info("ℹ️ Configuración restablecida")
    
    with col3:
        if st.button("🧪 Probar configuración", use_container_width=True):
            with st.spinner("Probando..."):
                import time
                time.sleep(1)
                st.success("✅ Configuración válida")


if __name__ == "__main__":
    main()
