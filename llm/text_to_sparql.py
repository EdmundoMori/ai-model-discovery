"""
Text to SPARQL Converter using LangChain + RAG
================================================

Este módulo implementa la conversión de lenguaje natural a SPARQL usando:
1. **LangChain**: Framework para orquestación de LLMs
2. **RAG (Retrieval Augmented Generation)**: Recuperación de ejemplos relevantes  
3. **Few-Shot Learning**: Ejemplos dinámicos según la query del usuario

Arquitectura RAG:
-----------------
User Query → Embedding → Vector Search → Top-K Examples → LLM Prompt → SPARQL Query

Componentes:
- ChromaDB: Vector store para embeddings de ejemplos
- LangChain: Chains, prompts, retrievers
- Claude 3.5 Sonnet: LLM backend
"""

import os
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

# LangChain imports
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ChromaDB for RAG
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB no disponible. Instalar con: pip install chromadb")

# Internal imports
from .prompts import DAIMO_ONTOLOGY_CONTEXT, TEXT_TO_SPARQL_PROMPT
from .query_validator import validate_sparql
from .rag_sparql_examples import get_all_examples, SPARQLExample
from .ontology_dictionary import (
    get_top_properties,
    get_all_properties,
    get_property_context_compact,
    get_property_context_detailed
)


@dataclass
class ConversionResult:
    """Resultado de la conversión con metadata"""
    natural_query: str
    sparql_query: str
    is_valid: bool
    validation_errors: List[str]
    validation_warnings: List[str]
    retrieved_examples: List[str]  # IDs de ejemplos usados en RAG
    confidence: str  # high, medium, low


class TextToSPARQLConverter:
    """
    Conversor de texto a SPARQL con LangChain + RAG
    
    Workflow:
    1. Usuario envía query en lenguaje natural
    2. RAG retriever busca ejemplos similares en vector store
    3. LangChain construye prompt con ejemplos dinámicos
    4. Claude genera SPARQL query
    5. Validator verifica sintaxis y seguridad
    """
    
    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        model: str = "deepseek-r1:7b",
        use_rag: bool = True,
        top_k_examples: int = 3,
        temperature: float = 0.0,
        llm_provider: str = "ollama",  # "anthropic" or "ollama"
        validation_graph: Optional[any] = None  # RDFlib Graph para validación
    ):
        """
        Inicializa el conversor
        
        Args:
            anthropic_api_key: API key de Anthropic (default: $ANTHROPIC_API_KEY)
            model: Modelo a usar (DeepSeek R1 7B por defecto con Ollama)
            use_rag: Si True, usa RAG para seleccionar ejemplos dinámicamente
            top_k_examples: Número de ejemplos a recuperar con RAG
            temperature: Temperatura del LLM (0.0 = determinístico)
            llm_provider: "anthropic" o "ollama" (por defecto: ollama)
            validation_graph: Grafo RDF para validar ejecución de queries
        """
        self.llm_provider = llm_provider
        self.model = model
        self.use_rag = use_rag and CHROMADB_AVAILABLE
        self.top_k_examples = top_k_examples
        self.temperature = temperature
        self.validation_graph = validation_graph
        
        # Inicializar LLM según el provider
        if llm_provider == "ollama":
            if not OLLAMA_AVAILABLE:
                raise ValueError("Ollama no está disponible. Instalar con: pip install langchain-community")
            
            self.llm = Ollama(
                model=model,
                temperature=temperature,
                num_predict=2048
            )
            print(f"🦙 Usando Ollama con modelo: {model}")
            
        elif llm_provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ValueError("Anthropic no está disponible. Instalar con: pip install langchain-anthropic")
            
            self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY no configurada")
            
            self.llm = ChatAnthropic(
                anthropic_api_key=self.api_key,
                model_name=self.model,
                temperature=self.temperature,
                max_tokens=2048
            )
            print(f"🤖 Usando Anthropic Claude: {model}")
        else:
            raise ValueError(f"Provider no soportado: {llm_provider}. Use 'anthropic' u 'ollama'")
        
        # Inicializar RAG si está habilitado
        if self.use_rag:
            self._initialize_rag()
        
        # Construir chain de LangChain
        self._build_chain()
        
        print(f"✅ TextToSPARQLConverter inicializado")
        print(f"   - Modelo: {self.model}")
        print(f"   - RAG: {'✓ Habilitado' if self.use_rag else '✗ Deshabilitado'}")
        print(f"   - Top-K ejemplos: {self.top_k_examples}")
    
    def _initialize_rag(self):
        """
        Inicializa el sistema RAG con ChromaDB
        
        Pasos:
        1. Crear ChromaDB client (persistente)
        2. Crear colección con embeddings
        3. Indexar todos los ejemplos SPARQL
        """
        print("🔧 Inicializando RAG con ChromaDB...")
        
        # ChromaDB client (persistente para evitar errores de colección no encontrada)
        from pathlib import Path
        chroma_dir = Path.home() / ".cache" / "ai_model_discovery" / "chroma"
        chroma_dir.mkdir(parents=True, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(path=str(chroma_dir))
        
        # Embedding function (default de ChromaDB)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Intentar obtener colección existente o crear nueva
        try:
            self.collection = self.chroma_client.get_collection(
                name="sparql_examples",
                embedding_function=self.embedding_function
            )
            print(f"   ✓ Colección existente cargada ({self.collection.count()} ejemplos)")
            return  # Ya existe, no necesitamos reindexar
        except:
            # Colección no existe, crearla
            pass
        
        self.collection = self.chroma_client.create_collection(
            name="sparql_examples",
            embedding_function=self.embedding_function,
            metadata={"description": "DAIMO SPARQL query examples for RAG"}
        )
        
        # Indexar ejemplos
        examples = get_all_examples()
        
        documents = []
        metadatas = []
        ids = []
        
        for ex in examples:
            # Documento = query natural + keywords para mejor matching
            doc = f"{ex.natural_query}. Keywords: {', '.join(ex.keywords)}"
            documents.append(doc)
            
            metadatas.append({
                "id": ex.id,
                "complexity": ex.complexity,
                "category": ex.category,
                "explanation": ex.explanation
            })
            
            ids.append(ex.id)
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"   ✓ {len(examples)} ejemplos indexados en ChromaDB")
    
    def _retrieve_examples(self, user_query: str) -> Tuple[List[SPARQLExample], float]:
        """
        Recupera ejemplos relevantes usando RAG
        
        Args:
            user_query: Query del usuario en lenguaje natural
            
        Returns:
            Tupla de (ejemplos relevantes, RAG score promedio)
        """
        if not self.use_rag:
            # Sin RAG: retornar ejemplos básicos fijos
            all_examples = get_all_examples()
            return all_examples[:self.top_k_examples], 0.5
        
        # Query a ChromaDB
        results = self.collection.query(
            query_texts=[user_query],
            n_results=self.top_k_examples
        )
        
        # Calcular RAG score promedio (distancia → similaridad)
        # ChromaDB retorna distancias (menor = más similar)
        # Convertir a score de similaridad (0-1, mayor = más similar)
        distances = results['distances'][0]
        similarities = [1 / (1 + d) for d in distances]  # Convertir distancia a similaridad
        avg_score = sum(similarities) / len(similarities) if similarities else 0.0
        
        # Reconstruir SPARQLExample objects
        all_examples = get_all_examples()
        examples_dict = {ex.id: ex for ex in all_examples}
        
        retrieved = []
        for example_id in results['ids'][0]:
            if example_id in examples_dict:
                retrieved.append(examples_dict[example_id])
        
        return retrieved, avg_score
    
    def _build_chain(self):
        """
        Construye el LangChain chain para conversión
        
        Chain structure:
        1. RunnablePassthrough: Pasar user_query
        2. Retrieve examples (RAG)
        3. Build prompt con few-shot examples
        4. LLM call (Ollama/Anthropic)
        5. Output parser (extract SPARQL)
        """
        # Usar el nuevo prompt simplificado
        self.prompt = ChatPromptTemplate.from_template(TEXT_TO_SPARQL_PROMPT)
        
        # Output parser: extraer query limpia
        self.output_parser = StrOutputParser()
        
        print("   ✓ LangChain chain configurado")
    
    def _format_examples(self, examples: List[SPARQLExample]) -> str:
        """Formatea ejemplos para el prompt"""
        formatted = []
        for i, ex in enumerate(examples, 1):
            formatted.append(f"Ejemplo {i}:")
            formatted.append(f"Consulta: {ex.natural_query}")
            formatted.append(f"SPARQL:\n{ex.sparql_query}\n")
        
        return "\n".join(formatted)
    
    def _get_property_context(self, rag_score: float, user_query: str) -> str:
        """
        INYECCIÓN INTELIGENTE: Decide qué contexto de propiedades inyectar
        
        Estrategia basada en RAG score:
        - Score > 0.8: Sin diccionario (ejemplos suficientes)
        - Score 0.5-0.8: Diccionario reducido (top 10 propiedades)
        - Score < 0.5: Diccionario completo (~30 propiedades)
        
        Args:
            rag_score: Score promedio de similitud del RAG (0-1)
            user_query: Query del usuario (para sugerencias contextuales)
            
        Returns:
            String con contexto de propiedades o vacío
        """
        # Score MUY ALTO: Los ejemplos RAG son suficientes
        if rag_score > 0.8:
            return ""
        
        # Score MEDIO: Agregar top 10 propiedades (compacto)
        elif rag_score >= 0.5:
            top_props = get_top_properties(n=10)
            return "\n\n" + get_property_context_compact(top_props)
        
        # Score BAJO: Agregar diccionario completo por categorías
        else:
            all_props = get_all_properties()
            return "\n\n" + get_property_context_detailed(all_props)
    
    def _post_process_sparql(self, sparql: str) -> str:
        """
        Post-procesa el SPARQL generado para corregir patrones incorrectos comunes.
        
        Args:
            sparql: Query SPARQL generada por el LLM
            
        Returns:
            Query SPARQL corregida
        """
        import re
        
        corrected = sparql
        corrections_made = []
        
        # 0. NUEVA: Limpiar texto explicativo ANTES de la query
        # Eliminar líneas que empiezan con texto explicativo (no SPARQL)
        lines = corrected.split('\n')
        cleaned_lines = []
        found_sparql_start = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detectar inicio de SPARQL (PREFIX o SELECT)
            if stripped.startswith('PREFIX') or stripped.startswith('SELECT') or stripped.startswith('CONSTRUCT') or stripped.startswith('DESCRIBE') or stripped.startswith('ASK'):
                found_sparql_start = True
            
            # Una vez encontrado SPARQL, mantener todas las líneas hasta encontrar explicación
            if found_sparql_start:
                # Detener si encontramos texto explicativo DESPUÉS del SPARQL
                if any(stripped.lower().startswith(x) for x in ['explanation:', 'note:', 'this query', 'the query', 'here', 'above', 'below']):
                    break
                cleaned_lines.append(line)
            elif stripped.startswith('PREFIX'):
                # Forzar inicio si encuentra PREFIX
                found_sparql_start = True
                cleaned_lines.append(line)
        
        if len(cleaned_lines) < len(lines):
            corrected = '\n'.join(cleaned_lines)
            corrections_made.append(f"Eliminado texto explicativo ({len(lines) - len(cleaned_lines)} líneas)")
        
        # 0b. NUEVA: Balancear llaves { }
        open_braces = corrected.count('{')
        close_braces = corrected.count('}')
        
        if open_braces != close_braces:
            corrections_made.append(f"⚠️ Llaves desbalanceadas: {open_braces} abre, {close_braces} cierra")
            
            # Intentar corregir automáticamente
            if open_braces > close_braces:
                # Faltan llaves de cierre - agregar al final antes de LIMIT/ORDER
                missing = open_braces - close_braces
                
                # Buscar dónde insertar (antes de LIMIT, ORDER, o al final)
                insert_pos = len(corrected)
                for keyword in ['LIMIT', 'ORDER BY', 'GROUP BY']:
                    pos = corrected.upper().rfind(keyword)
                    if pos > 0:
                        insert_pos = min(insert_pos, pos)
                
                # Insertar llaves faltantes
                closing_braces = '\n' + '  ' * (missing - 1) + '}\n' * missing
                corrected = corrected[:insert_pos].rstrip() + closing_braces + corrected[insert_pos:]
                corrections_made.append(f"Agregadas {missing} llaves de cierre")
                
            elif close_braces > open_braces:
                # Sobran llaves de cierre - eliminar las últimas
                missing = close_braces - open_braces
                for _ in range(missing):
                    # Eliminar última llave de cierre
                    last_brace = corrected.rfind('}')
                    if last_brace > 0:
                        corrected = corrected[:last_brace] + corrected[last_brace+1:]
                corrections_made.append(f"Eliminadas {missing} llaves de cierre sobrantes")
        
        # 0c. NUEVA: Limpiar punto y coma incorrectos
        # En SPARQL, los ; separan propiedades del mismo sujeto
        # Error común: poner ; al final de un bloque OPTIONAL o antes de FILTER
        
        # Eliminar ; antes de FILTER
        if re.search(r';\s*FILTER', corrected):
            corrected = re.sub(r';\s*FILTER', ' .\n  FILTER', corrected)
            corrections_made.append("Eliminado ; incorrecto antes de FILTER")
        
        # Eliminar ; antes de OPTIONAL
        if re.search(r';\s*OPTIONAL', corrected):
            corrected = re.sub(r';\s*OPTIONAL', ' .\n  OPTIONAL', corrected)
            corrections_made.append("Eliminado ; incorrecto antes de OPTIONAL")
        
        # Eliminar ; antes de }
        if re.search(r';\s*}', corrected):
            corrected = re.sub(r';\s*}', '\n  }', corrected)
            corrections_made.append("Eliminado ; incorrecto antes de }")
        
        # 0d. NUEVA: Asegurar que la query empieza correctamente
        # Error: query que empieza con minúsculas o caracteres extraños
        first_line = corrected.lstrip().split('\n')[0].strip()
        
        if not any(first_line.startswith(kw) for kw in ['PREFIX', 'SELECT', 'CONSTRUCT', 'DESCRIBE', 'ASK']):
            # Buscar la primera línea válida
            for i, line in enumerate(corrected.split('\n')):
                if any(line.strip().startswith(kw) for kw in ['PREFIX', 'SELECT', 'CONSTRUCT', 'DESCRIBE', 'ASK']):
                    corrected = '\n'.join(corrected.split('\n')[i:])
                    corrections_made.append("Eliminadas líneas inválidas al inicio")
                    break
        
        # 1. Corregir PREFIX dcterms incorrecto
        # Patrones incorrectos comunes del LLM
        wrong_dcterms_patterns = [
            r'PREFIX dcterms: <http://www\.w3\.org/2001/XMLSchema[^>]*>',
            r'PREFIX dcterms: <http://xmlns\.com/[^>]*>',
            r'PREFIX dcterms: <http://purl\.org/dc/[^>]*elements[^>]*>',
        ]
        correct_dcterms = 'PREFIX dcterms: <http://purl.org/dc/terms/>'
        
        for pattern in wrong_dcterms_patterns:
            if re.search(pattern, corrected):
                corrected = re.sub(pattern, correct_dcterms, corrected)
                corrections_made.append("PREFIX dcterms corregido")
                break
        
        # 2. Corregir daimo:AIModel → daimo:Model
        if 'daimo:AIModel' in corrected:
            corrected = corrected.replace('daimo:AIModel', 'daimo:Model')
            corrections_made.append("Clase: AIModel → Model")
        
        # 3. Convertir daimo:task obligatorio → OPTIONAL
        # Patrón: daimo:task ?task . (binding obligatorio)
        # Cambiar a: OPTIONAL { ?model daimo:task ?task }
        task_pattern = r'daimo:task\s+\?task\s*[;\.]'
        if re.search(task_pattern, corrected):
            # Verificar si NO está ya en OPTIONAL
            if 'OPTIONAL' not in corrected or 'OPTIONAL { ?model daimo:task ?task }' not in corrected:
                corrected = re.sub(
                    r'daimo:task\s+\?task\s*([;\.])',
                    r'.\n  OPTIONAL { ?model daimo:task ?task }',
                    corrected,
                    count=1
                )
                corrections_made.append("daimo:task convertido a OPTIONAL")
        
        # 4. Corregir OPTIONAL con literal: OPTIONAL { ?model daimo:prop 'value' }
        optional_literal_pattern = r'OPTIONAL\s*{\s*\?model\s+([\w:]+)\s+(["\'][^"\']+["\'])\s*}'
        matches = list(re.finditer(optional_literal_pattern, corrected))
        for match in reversed(matches):
            prop = match.group(1)
            value = match.group(2)
            prop_name = prop.split(':')[-1] if ':' in prop else prop
            var_name = f"?{prop_name}"
            
            old_pattern = match.group(0)
            new_pattern = f"?model {prop} {var_name} .\n  FILTER({var_name} = {value})"
            corrected = corrected[:match.start()] + new_pattern + corrected[match.end():]
            corrections_made.append(f"OPTIONAL literal: {prop}")
        
        # 5. Asegurar que dcterms:title/source/description usen dcterms (no daimo)
        if re.search(r'\bdaimo:title\b', corrected):
            corrected = re.sub(r'\bdaimo:title\b', 'dcterms:title', corrected)
            corrections_made.append("Namespace: daimo:title → dcterms:title")
        if re.search(r'\bdaimo:source\b', corrected):
            corrected = re.sub(r'\bdaimo:source\b', 'dcterms:source', corrected)
            corrections_made.append("Namespace: daimo:source → dcterms:source")
        if re.search(r'\bdaimo:description\b', corrected):
            corrected = re.sub(r'\bdaimo:description\b', 'dcterms:description', corrected)
            corrections_made.append("Namespace: daimo:description → dcterms:description")
        
        # 6. Eliminar filtros restrictivos con downloads en OPTIONAL
        # Patrón problemático: ?downloads > N en FILTER cuando downloads es OPTIONAL
        if 'OPTIONAL { ?model daimo:downloads ?downloads }' in corrected or 'OPTIONAL {?model daimo:downloads ?downloads}' in corrected:
            # Buscar FILTER con ?downloads > N sin !BOUND
            filter_downloads_pattern = r'FILTER\s*\([^)]*?(?<!\!BOUND\(\?downloads\)\s\|\|\s)\?downloads\s*>\s*\d+'
            if re.search(filter_downloads_pattern, corrected):
                # Agregar !BOUND al FILTER
                corrected = re.sub(
                    r'(\?downloads\s*>\s*\d+)',
                    r'(!BOUND(?downloads) || \1)',
                    corrected
                )
                corrections_made.append("Agregado !BOUND(?downloads) al FILTER")
        
        # 7. Asegurar que existan PREFIXes necesarios
        required_prefixes = {
            'daimo': 'PREFIX daimo: <http://purl.org/pionera/daimo#>',
            'dcterms': 'PREFIX dcterms: <http://purl.org/dc/terms/>'
        }
        
        for prefix_name, prefix_declaration in required_prefixes.items():
            # Verificar si el prefijo se usa pero no está declarado
            if f'{prefix_name}:' in corrected and f'PREFIX {prefix_name}:' not in corrected:
                # Agregar al inicio
                corrected = prefix_declaration + '\n' + corrected
                corrections_made.append(f"PREFIX {prefix_name} agregado")
        
        # 8. Agregar LIMIT si falta
        if 'LIMIT' not in corrected.upper():
            # Agregar antes del último salto de línea o al final
            corrected = corrected.rstrip() + '\nLIMIT 15'
            corrections_made.append("LIMIT 15 agregado")
        
        # 9. Verificar LIMIT excesivo (>50 es muy grande)
        limit_match = re.search(r'LIMIT\s+(\d+)', corrected, re.IGNORECASE)
        if limit_match:
            limit_value = int(limit_match.group(1))
            if limit_value > 50:
                corrected = re.sub(r'LIMIT\s+\d+', 'LIMIT 50', corrected, flags=re.IGNORECASE)
                corrections_made.append(f"LIMIT reducido de {limit_value} a 50")
            elif limit_value < 5:
                corrected = re.sub(r'LIMIT\s+\d+', 'LIMIT 10', corrected, flags=re.IGNORECASE)
                corrections_made.append(f"LIMIT aumentado de {limit_value} a 10")
        
        # 10. Normalizar comillas: preferir comillas dobles en literales
        # Convertir comillas simples a dobles en literales (pero no en URLs)
        corrected = re.sub(r"'([^']+)'(?!\s*\^)", r'"\1"', corrected)
        if "'" in sparql and "'" not in corrected:
            corrections_made.append("Comillas simples → dobles en literales")
        
        # 11. Asegurar que ?model esté en SELECT si no es agregación
        if 'SELECT' in corrected and 'GROUP BY' not in corrected:
            select_match = re.search(r'SELECT\s+(.*?)\s+WHERE', corrected, re.DOTALL)
            if select_match:
                select_vars = select_match.group(1)
                if '?model' not in select_vars and 'COUNT' not in select_vars:
                    # Agregar ?model al inicio del SELECT
                    corrected = re.sub(
                        r'(SELECT\s+)',
                        r'\1?model ',
                        corrected,
                        count=1
                    )
                    corrections_made.append("?model agregado al SELECT")
        
        # 12. Limpiar espacios y formato
        # Asegurar saltos de línea después de PREFIXes
        corrected = re.sub(r'(PREFIX[^\n]+)(?!\n\n)', r'\1\n', corrected)
        # Limpiar múltiples espacios
        corrected = re.sub(r' {2,}', ' ', corrected)
        
        # Log correcciones
        if corrections_made:
            print(f"   🔧 Post-procesamiento aplicado ({len(corrections_made)} correcciones):")
            for correction in corrections_made:
                print(f"      • {correction}")
        else:
            print(f"   ✅ Query correcta, sin correcciones necesarias")
        
        return corrected
    
    def _clean_sparql_output(self, raw_output: str) -> str:
        """
        Limpia la salida del LLM para extraer solo SPARQL
        
        LLMs a veces agregan texto extra, markdown, etc.
        Esta función extrae la query limpia.
        """
        # Eliminar markdown code blocks
        if "```sparql" in raw_output:
            raw_output = raw_output.split("```sparql")[1].split("```")[0]
        elif "```" in raw_output:
            raw_output = raw_output.split("```")[1].split("```")[0]
        
        # Eliminar líneas de explicación
        lines = raw_output.strip().split("\n")
        query_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Skip empty lines and explanations
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue
            # Keep SPARQL lines
            if any(keyword in stripped.upper() for keyword in ["PREFIX", "SELECT", "WHERE", "FILTER", "ORDER", "LIMIT", "GROUP", "OPTIONAL"]):
                query_lines.append(line)
            elif query_lines:  # Inside query
                query_lines.append(line)
        
        return "\n".join(query_lines).strip()
    
    def convert(self, user_query: str, validate: bool = True, use_fallback: bool = True) -> ConversionResult:
        """
        Convierte lenguaje natural a SPARQL
        
        Args:
            user_query: Query del usuario en lenguaje natural
            validate: Si True, valida la query generada
            use_fallback: Si True, usa el mejor ejemplo RAG como fallback cuando LLM falla
            
        Returns:
            ConversionResult con query, validación y metadata
        """
        print(f"\n🔍 Procesando: '{user_query}'")
        
        # 1. Recuperar ejemplos relevantes (RAG) + score
        retrieved_examples, rag_score = self._retrieve_examples(user_query)
        example_ids = [ex.id for ex in retrieved_examples]
        
        if self.use_rag:
            print(f"   📚 Ejemplos recuperados (RAG): {', '.join(example_ids)}")
            print(f"   📊 RAG Score: {rag_score:.3f}")
        
        # FALLBACK DIRECTO: Si RAG score es alto (>0.5), usar ejemplo directamente
        # Esto garantiza queries correctos en lugar de confiar en LLM que puede generar sintaxis incorrecta
        if use_fallback and rag_score > 0.50 and len(retrieved_examples) > 0:
            best_example = retrieved_examples[0]
            print(f"   🎯 RAG score suficiente ({rag_score:.3f}) - Usando ejemplo {best_example.id} directamente")
            
            return ConversionResult(
                natural_query=user_query,
                sparql_query=best_example.sparql_query,
                is_valid=True,
                validation_errors=[],
                validation_warnings=[],
                retrieved_examples=[best_example.id],
                confidence="high"
            )
        
        # 2. Formatear ejemplos para prompt
        examples_text = self._format_examples(retrieved_examples)
        
        # 3. INYECCIÓN INTELIGENTE: Agregar diccionario de propiedades según RAG score
        property_context = self._get_property_context(rag_score, user_query)
        
        if property_context:
            print(f"   📖 Contexto de propiedades inyectado")
        
        # 4. Construir chain dinámico con ejemplos
        chain = self.prompt | self.llm | self.output_parser
        
        # 5. Ejecutar LLM
        try:
            raw_output = chain.invoke({
                "examples": examples_text,
                "property_context": property_context,
                "user_query": user_query
            })
            
            # 6. Limpiar output
            sparql_query = self._clean_sparql_output(raw_output)
            
            # 7. POST-PROCESAMIENTO: Corregir patrones incorrectos
            sparql_query = self._post_process_sparql(sparql_query)
            
            print(f"   ✓ SPARQL generado ({len(sparql_query)} chars)")
            
        except Exception as e:
            print(f"   ✗ Error en LLM: {e}")
            return ConversionResult(
                natural_query=user_query,
                sparql_query="",
                is_valid=False,
                validation_errors=[f"LLM error: {str(e)}"],
                validation_warnings=[],
                retrieved_examples=example_ids,
                confidence="low"
            )
        
        # 7. Validar query
        is_valid = True
        errors = []
        warnings = []
        
        if validate:
            # Crear validador con grafo si está disponible
            from llm.query_validator import SPARQLValidator
            validator = SPARQLValidator(test_graph=self.validation_graph)
            validation_result = validator.validate(sparql_query)
            is_valid = validation_result.get('valid', False)
            errors = validation_result.get('errors', [])
            warnings = validation_result.get('warnings', [])
            
            if is_valid:
                print(f"   ✅ Query válida")
            else:
                print(f"   ⚠️  Query inválida: {len(errors)} errores")
        
        # 8. Estimar confianza
        confidence = self._estimate_confidence(sparql_query, errors, warnings)
        
        return ConversionResult(
            natural_query=user_query,
            sparql_query=sparql_query,
            is_valid=is_valid,
            validation_errors=errors,
            validation_warnings=warnings,
            retrieved_examples=example_ids,
            confidence=confidence
        )
    
    def _estimate_confidence(self, sparql: str, errors: List[str], warnings: List[str]) -> str:
        """Estima la confianza en la conversión"""
        if errors:
            return "low"
        
        # Check query completeness
        required_keywords = ["PREFIX", "SELECT", "WHERE"]
        has_all = all(kw in sparql for kw in required_keywords)
        
        if not has_all:
            return "low"
        
        if warnings:
            return "medium"
        
        return "high"
    
    def batch_convert(self, queries: List[str], validate: bool = True) -> List[ConversionResult]:
        """
        Convierte múltiples queries en batch
        
        Útil para evaluación y testing
        """
        results = []
        
        print(f"\n🚀 Procesando {len(queries)} queries en batch...")
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}]", end=" ")
            result = self.convert(query, validate=validate)
            results.append(result)
        
        # Estadísticas
        valid_count = sum(1 for r in results if r.is_valid)
        success_rate = (valid_count / len(results)) * 100
        
        print(f"\n\n📊 Resultados:")
        print(f"   - Válidas: {valid_count}/{len(results)} ({success_rate:.1f}%)")
        print(f"   - Confianza alta: {sum(1 for r in results if r.confidence == 'high')}")
        print(f"   - Confianza media: {sum(1 for r in results if r.confidence == 'medium')}")
        print(f"   - Confianza baja: {sum(1 for r in results if r.confidence == 'low')}")
        
        return results


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

def convert_text_to_sparql(
    user_query: str,
    api_key: Optional[str] = None,
    use_rag: bool = True
) -> Tuple[str, bool]:
    """
    Función simple para conversión rápida
    
    Returns:
        (sparql_query, is_valid)
    """
    converter = TextToSPARQLConverter(
        anthropic_api_key=api_key,
        use_rag=use_rag
    )
    
    result = converter.convert(user_query)
    return result.sparql_query, result.is_valid


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Test básico
    converter = TextToSPARQLConverter(use_rag=True)
    
    test_queries = [
        "show me the most popular models",
        "computer vision models from HuggingFace",
        "compare PyTorch vs TensorFlow by average downloads"
    ]
    
    for query in test_queries:
        result = converter.convert(query)
        
        print(f"\n{'='*60}")
        print(f"Query: {result.natural_query}")
        print(f"Valid: {result.is_valid}")
        print(f"Confidence: {result.confidence}")
        print(f"Examples used: {', '.join(result.retrieved_examples)}")
        print(f"\nSPARQL:\n{result.sparql_query}")
        
        if result.validation_errors:
            print(f"\nErrors: {result.validation_errors}")
