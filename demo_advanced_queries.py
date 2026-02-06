"""
Demo de Consultas SPARQL Avanzadas con Ontología DAIMO v2.0

Demuestra las capacidades de la ontología mejorada con 32 propiedades
para realizar consultas complejas sobre 4 repositorios de modelos de IA.
"""

import os
os.chdir("/home/edmundo/ai-model-discovery")

from utils.huggingface_repository import HuggingFaceRepository
from utils.kaggle_repository import KaggleRepository
from utils.civitai_repository import CivitaiRepository
from utils.replicate_repository import ReplicateRepository
from knowledge_graph.multi_repository_builder import MultiRepositoryGraphBuilder


def print_section(title):
    """Imprime un título de sección."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_query(graph, query_name, query, description):
    """Ejecuta una consulta SPARQL y muestra resultados."""
    print(f"🔍 {query_name}")
    print(f"   {description}\n")
    
    results = list(graph.query(query))
    
    if not results:
        print("   ⚠️ No se encontraron resultados\n")
        return
    
    print(f"   ✅ {len(results)} resultados:\n")
    return results


def main():
    print_section("🚀 DEMO: Consultas SPARQL Avanzadas con DAIMO v2.0")
    
    # Construir grafo con 10 modelos por repositorio
    print("📦 Construyendo grafo de conocimiento...\n")
    
    builder = MultiRepositoryGraphBuilder()
    
    repos = {
        'HuggingFace': HuggingFaceRepository(),
        'Kaggle': KaggleRepository(),
        'Civitai': CivitaiRepository(),
        'Replicate': ReplicateRepository()
    }
    
    total_models = 0
    for name, repo in repos.items():
        builder.add_repository(repo)
        try:
            models = repo.fetch_models(limit=10)
            for model in models:
                builder.add_standardized_model(model, repository=repo)
            total_models += len(models)
            print(f"   ✅ {name}: {len(models)} modelos")
        except Exception as e:
            print(f"   ⚠️ {name}: {str(e)[:50]}")
    
    g = builder.graph
    print(f"\n   📊 Grafo: {len(g):,} triples | {total_models} modelos")
    
    # ========================================================================
    # QUERY 1: Modelos con API de Inferencia
    # ========================================================================
    print_section("QUERY 1: Modelos con API de Inferencia Disponible")
    
    query1 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT ?title ?source ?endpoint ?downloads WHERE {
        ?model a daimo:Model ;
               dcterms:title ?title ;
               daimo:source ?source ;
               daimo:inferenceEndpoint ?endpoint ;
               daimo:downloads ?downloads .
    }
    ORDER BY DESC(?downloads)
    LIMIT 10
    """
    
    results = run_query(g, "Modelos Production-Ready", query1,
                       "Modelos con endpoint de inferencia para uso inmediato")
    
    if results:
        for i, row in enumerate(results, 1):
            print(f"   {i}. {str(row.title)[:40]:40s} [{str(row.source):12s}]")
            print(f"      Endpoint: {str(row.endpoint)[:60]}")
            print(f"      Descargas: {int(str(row.downloads)):,}\n")
    
    # ========================================================================
    # QUERY 2: Comparación de Métricas de Popularidad
    # ========================================================================
    print_section("QUERY 2: Comparación de Métricas por Repositorio")
    
    query2 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT ?title ?source ?downloads ?likes ?runCount WHERE {
        ?model a daimo:Model ;
               dcterms:title ?title ;
               daimo:source ?source .
        
        OPTIONAL { ?model daimo:downloads ?downloads }
        OPTIONAL { ?model daimo:likes ?likes }
        OPTIONAL { ?model daimo:runCount ?runCount }
        
        FILTER(?downloads > 0 || ?likes > 0 || ?runCount > 0)
    }
    ORDER BY DESC(?downloads) DESC(?runCount) DESC(?likes)
    LIMIT 15
    """
    
    results = run_query(g, "Métricas de Popularidad", query2,
                       "Comparación de downloads, likes y ejecuciones")
    
    if results:
        print(f"   {'Modelo':<35} {'Repo':<12} {'Downloads':>12} {'Likes':>8} {'Runs':>12}")
        print(f"   {'-'*35} {'-'*12} {'-'*12} {'-'*8} {'-'*12}")
        
        for row in results:
            title = str(row.title)[:33]
            source = str(row.source)
            downloads = int(str(row.downloads)) if row.downloads else 0
            likes = int(str(row.likes)) if row.likes else 0
            runs = int(str(row.runCount)) if row.runCount else 0
            
            print(f"   {title:<35} {source:<12} {downloads:>12,} {likes:>8,} {runs:>12,}")
        print()
    
    # ========================================================================
    # QUERY 3: Modelos por Pipeline/Tarea
    # ========================================================================
    print_section("QUERY 3: Distribución por Tipo de Tarea (Pipeline)")
    
    query3 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT ?pipeline (COUNT(?model) as ?modelCount) WHERE {
        ?model a daimo:Model ;
               daimo:pipelineTag ?pipeline .
    }
    GROUP BY ?pipeline
    ORDER BY DESC(?modelCount)
    """
    
    results = run_query(g, "Tareas ML más Comunes", query3,
                       "Agrupación de modelos por pipeline_tag")
    
    if results:
        print(f"   {'Pipeline':<30} {'Modelos':>10}")
        print(f"   {'-'*30} {'-'*10}")
        for row in results:
            print(f"   {str(row.pipeline):<30} {int(str(row.modelCount)):>10}")
        print()
    
    # ========================================================================
    # QUERY 4: Modelos con Recursos Educativos
    # ========================================================================
    print_section("QUERY 4: Modelos con Documentación Completa")
    
    query4 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT ?title ?source ?github ?paper WHERE {
        ?model a daimo:Model ;
               dcterms:title ?title ;
               daimo:source ?source .
        
        OPTIONAL { ?model daimo:githubURL ?github }
        OPTIONAL { ?model daimo:paperURL ?paper }
        
        FILTER(BOUND(?github) || BOUND(?paper))
    }
    ORDER BY ?source
    LIMIT 10
    """
    
    results = run_query(g, "Modelos Bien Documentados", query4,
                       "Modelos con GitHub y/o paper académico")
    
    if results:
        for row in results:
            print(f"   📚 {str(row.title)[:45]} [{str(row.source)}]")
            if row.github:
                print(f"      GitHub: {str(row.github)}")
            if row.paper:
                print(f"      Paper: {str(row.paper)}")
            print()
    
    # ========================================================================
    # QUERY 5: Control de Acceso y Seguridad
    # ========================================================================
    print_section("QUERY 5: Análisis de Control de Acceso")
    
    query5 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT ?title ?source ?private ?gated ?nsfw WHERE {
        ?model a daimo:Model ;
               dcterms:title ?title ;
               daimo:source ?source .
        
        OPTIONAL { ?model daimo:isPrivate ?private }
        OPTIONAL { ?model daimo:isGated ?gated }
        OPTIONAL { ?model daimo:isNSFW ?nsfw }
    }
    LIMIT 20
    """
    
    results = run_query(g, "Restricciones de Acceso", query5,
                       "Modelos con controles de privacidad o contenido")
    
    if results:
        public_count = sum(1 for r in results if not (r.private and str(r.private).lower() == 'true'))
        gated_count = sum(1 for r in results if r.gated and str(r.gated).lower() == 'true')
        nsfw_count = sum(1 for r in results if r.nsfw and str(r.nsfw).lower() == 'true')
        
        print(f"   📊 Estadísticas de Acceso:")
        print(f"      • Públicos: {public_count}/{len(results)}")
        print(f"      • Con aprobación requerida: {gated_count}/{len(results)}")
        print(f"      • Contenido sensible (NSFW): {nsfw_count}/{len(results)}")
        print()
    
    # ========================================================================
    # QUERY 6: Modelos con Safetensors
    # ========================================================================
    print_section("QUERY 6: Modelos con Formato Safetensors")
    
    query6 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT ?title ?source ?safetensors WHERE {
        ?model a daimo:Model ;
               dcterms:title ?title ;
               daimo:source ?source ;
               daimo:safetensors ?safetensors .
        
        FILTER(?safetensors = true)
    }
    LIMIT 10
    """
    
    results = run_query(g, "Modelos con Safetensors", query6,
                       "Formato seguro para cargar pesos del modelo")
    
    if results:
        print(f"   ✅ {len(results)} modelos usan Safetensors (formato seguro)\n")
        for i, row in enumerate(results, 1):
            print(f"   {i}. {str(row.title)[:50]} [{str(row.source)}]")
    
    # ========================================================================
    # QUERY 7: Versionado y Tracking
    # ========================================================================
    print_section("QUERY 7: Modelos con Control de Versiones")
    
    query7 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT ?title ?source ?versionId ?cogVersion WHERE {
        ?model a daimo:Model ;
               dcterms:title ?title ;
               daimo:source ?source .
        
        OPTIONAL { ?model daimo:versionId ?versionId }
        OPTIONAL { ?model daimo:cogVersion ?cogVersion }
        
        FILTER(BOUND(?versionId) || BOUND(?cogVersion))
    }
    LIMIT 10
    """
    
    results = run_query(g, "Control de Versiones", query7,
                       "Modelos con versionado explícito (Replicate)")
    
    if results:
        for row in results:
            print(f"   📦 {str(row.title)[:40]}")
            if row.versionId:
                print(f"      Version ID: {str(row.versionId)[:40]}...")
            if row.cogVersion:
                print(f"      Cog Version: {str(row.cogVersion)}")
            print()
    
    # ========================================================================
    # QUERY 8: Análisis Cross-Repository
    # ========================================================================
    print_section("QUERY 8: Comparación Cross-Repository")
    
    query8 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    
    SELECT ?source 
           (COUNT(?model) as ?totalModels)
           (AVG(?downloads) as ?avgDownloads)
           (MAX(?downloads) as ?maxDownloads)
    WHERE {
        ?model a daimo:Model ;
               daimo:source ?source ;
               daimo:downloads ?downloads .
    }
    GROUP BY ?source
    ORDER BY DESC(?avgDownloads)
    """
    
    results = run_query(g, "Estadísticas por Repositorio", query8,
                       "Métricas agregadas por fuente")
    
    if results:
        print(f"   {'Repositorio':<15} {'Modelos':>10} {'Avg Downloads':>15} {'Max Downloads':>15}")
        print(f"   {'-'*15} {'-'*10} {'-'*15} {'-'*15}")
        for row in results:
            source = str(row.source)
            total = int(str(row.totalModels))
            avg = int(float(str(row.avgDownloads))) if row.avgDownloads else 0
            max_dl = int(str(row.maxDownloads)) if row.maxDownloads else 0
            print(f"   {source:<15} {total:>10} {avg:>15,} {max_dl:>15,}")
        print()
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print_section("📊 RESUMEN DE CAPACIDADES")
    
    print("   ✅ Ontología DAIMO v2.0:")
    print("      • 32 propiedades (vs 7 en v1.0) = +357%")
    print("      • 4 repositorios integrados")
    print("      • 8 consultas avanzadas demostradas")
    print()
    
    print("   🎯 Casos de Uso Habilitados:")
    print("      1. Búsqueda de modelos production-ready (con API)")
    print("      2. Comparación de popularidad cross-repository")
    print("      3. Filtrado por tipo de tarea (pipeline_tag)")
    print("      4. Descubrimiento de recursos educativos")
    print("      5. Análisis de restricciones de acceso")
    print("      6. Validación de formato seguro (safetensors)")
    print("      7. Tracking de versiones de modelos")
    print("      8. Análisis estadístico agregado")
    print()
    
    print("   🚀 Mejoras vs v1.0:")
    print("      • +25 propiedades nuevas activas")
    print("      • Soporte multi-repositorio nativo")
    print("      • Metadatos técnicos enriquecidos")
    print("      • Consultas complejas habilitadas")
    print()
    
    print("=" * 80)
    print("\n✅ Demo completada. Sistema listo para uso en investigación.\n")


if __name__ == "__main__":
    main()
