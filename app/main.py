"""
AI Model Discovery - Streamlit Web Interface

Interfaz web para demostrar el sistema de búsqueda semántica de modelos de IA

Características:
- 🔍 Búsqueda semántica con Text-to-SPARQL
- 📊 Dashboard de estadísticas
- 📈 Visualización del grafo RDF
- ⚙️ Configuración del sistema

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

import streamlit as st
import sys
from pathlib import Path

# Configurar path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuración de la página
st.set_page_config(
    page_title="AI Model Discovery",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .result-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Página principal"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Model Discovery</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Sistema de búsqueda semántica de modelos de IA con Text-to-SPARQL</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1E88E5/FFFFFF?text=AI+Discovery", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### 📚 Navegación")
        st.markdown("""
        - 📥 **Gestión de Datos**: Descargar modelos reales
        - 🔍 **Búsqueda**: Consultas en lenguaje natural
        - 📊 **Dashboard**: Estadísticas del catálogo
        - 📈 **Grafo RDF**: Visualización del conocimiento
        - ⚙️ **Configuración**: Ajustes del sistema
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 Sistema")
        st.markdown("""
        **Componentes validados:**
        - ✅ Text-to-SPARQL (80% success)
        - ✅ RAG con 14 ejemplos
        - ✅ Validación con RDF
        - ✅ GPU acceleration (RTX 4050)
        """)
        
        st.markdown("---")
        st.markdown("### 📖 Repositorios")
        st.markdown("""
        1. HuggingFace
        2. TensorFlow Hub
        3. PyTorch Hub
        4. Replicate
        5. Kaggle
        6. PapersWithCode
        7. GitHub
        """)
        
        st.markdown("---")
        st.markdown("### 👨‍💻 Autor")
        st.markdown("**Edmundo Mori**")
        st.markdown("Tesis de Grado - 2026")
    
    # Contenido principal
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>🔍</h2>
            <h3>Búsqueda Semántica</h3>
            <p>Consultas en lenguaje natural convertidas automáticamente a SPARQL</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>🤖</h2>
            <h3>7 Repositorios</h3>
            <p>Integración con HuggingFace, PyTorch Hub, Kaggle y más</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>📊</h2>
            <h3>Ontología DAIMO</h3>
            <p>Grafo RDF con metadatos semánticos enriquecidos</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sección de inicio rápido
    st.markdown("## 🚀 Inicio Rápido")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📖 Cómo usar")
        st.markdown("""
        1. **Descargar modelos**: Ve a "📥 Gestión de Datos"
        2. **Seleccionar repositorios**: Elige de 7 fuentes disponibles
        3. **Construir grafo**: Genera el grafo RDF con metadatos reales
        4. **Buscar modelos**: Usa lenguaje natural en "🔍 Búsqueda"
        5. **Explorar**: Analiza estadísticas y visualiza el grafo
        """)
    
    with col2:
        st.markdown("### 💡 Ejemplos de búsqueda")
        st.code("""
# Búsquedas básicas
"list all AI models"
"PyTorch models"
"models from HuggingFace"

# Búsquedas avanzadas
"high rated NLP models"
"most popular computer vision models"
"models with rating above 4.5"

# Agregaciones
"count models by repository"
"average rating per task"
        """)
    
    st.markdown("---")
    
    # Arquitectura del sistema
    st.markdown("## 🏗️ Arquitectura del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 1️⃣ Recolección")
        st.markdown("""
        - Multi-repository collectors
        - 7 fuentes de datos
        - Metadata enriquecida
        - Normalización de datos
        """)
    
    with col2:
        st.markdown("### 2️⃣ Procesamiento")
        st.markdown("""
        - Construcción de grafo RDF
        - Ontología DAIMO
        - Text-to-SPARQL con LLM
        - RAG con ChromaDB
        """)
    
    with col3:
        st.markdown("### 3️⃣ Búsqueda")
        st.markdown("""
        - SearchEngine semántico
        - Ranking de resultados
        - Validación automática
        - API REST
        """)
    
    st.markdown("---")
    
    # Estado del proyecto
    st.markdown("## 📈 Estado del Proyecto")
    
    progress_col1, progress_col2 = st.columns([2, 1])
    
    with progress_col1:
        st.markdown("### Fases completadas")
        
        phases = [
            ("Fase 0: Inicialización", 100),
            ("Fase 1: Fundamentos", 100),
            ("Fase 2: SearchEngine", 75),
            ("Fase 3: Búsqueda federada", 0),
            ("Fase 4: Cross-repository", 0),
        ]
        
        for phase, completion in phases:
            st.progress(completion / 100)
            st.markdown(f"**{phase}**: {completion}%")
    
    with progress_col2:
        st.markdown("### Métricas clave")
        st.metric("Success Rate", "80%", "10%")
        st.metric("Modelos validados", "70", "70")
        st.metric("Repositorios", "7", "7")
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>🎓 Proyecto de Tesis - Sistema de Descubrimiento y Búsqueda de Modelos de IA</p>
        <p>Edmundo Mori - 2026</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
