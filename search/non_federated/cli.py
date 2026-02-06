#!/usr/bin/env python3
"""
CLI para SearchEngine - Interfaz de línea de comandos

Uso:
    python -m search.non_federated.cli search "PyTorch models"
    python -m search.non_federated.cli stats
    python -m search.non_federated.cli sparql "high rated models"

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import json

# Agregar directorio raíz al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from search.non_federated.api import create_api
from rdflib import Graph


def load_default_graph() -> Optional[Graph]:
    """Cargar grafo por defecto desde data/"""
    graph_path = project_root / "data" / "processed" / "knowledge_graph.ttl"
    
    if graph_path.exists():
        g = Graph()
        g.parse(str(graph_path), format="turtle")
        return g
    else:
        print(f"⚠️  Grafo no encontrado en {graph_path}")
        print("   Crea el grafo primero ejecutando: python -m knowledge_graph.build_graph")
        return None


def search_command(args):
    """Ejecutar búsqueda"""
    graph = load_default_graph()
    if graph is None:
        return 1
    
    api = create_api(graph=graph)
    
    print(f"🔍 Buscando: '{args.query}'")
    print("=" * 70)
    
    results = api.search(
        query=args.query,
        max_results=args.max_results,
        format="response"
    )
    
    if not results.is_valid:
        print("❌ Query inválida:")
        for error in results.errors:
            print(f"   - {error}")
        return 1
    
    print(f"✅ {results.total_results} resultados encontrados")
    print(f"⏱️  Tiempo: {results.execution_time:.2f}s")
    
    if args.show_sparql:
        print(f"\n📝 SPARQL generado:")
        print(results.sparql_query)
    
    print(f"\n📊 Top {len(results.results)} resultados:\n")
    
    for i, result in enumerate(results.results, 1):
        print(f"{i}. {result.title}")
        print(f"   📦 Repositorio: {result.source}")
        print(f"   🎯 Tarea: {result.task}")
        print(f"   ⭐ Score: {result.score:.2f}")
        
        if args.verbose:
            print(f"   📚 Biblioteca: {result.metadata.get('library', 'N/A')}")
            print(f"   📥 Downloads: {result.metadata.get('downloads', 'N/A')}")
            print(f"   ⭐ Rating: {result.metadata.get('rating', 'N/A')}")
        
        print()
    
    if args.json:
        print("\n📄 JSON output:")
        print(json.dumps(results.to_dict(), indent=2, ensure_ascii=False))
    
    return 0


def stats_command(args):
    """Mostrar estadísticas"""
    graph = load_default_graph()
    if graph is None:
        return 1
    
    api = create_api(graph=graph)
    
    print("📊 ESTADÍSTICAS DEL GRAFO")
    print("=" * 70)
    
    stats = api.get_statistics()
    
    print(f"\n📈 General:")
    print(f"   Total modelos:  {stats['total_models']:,}")
    print(f"   Total triples:  {stats['total_triples']:,}")
    
    print(f"\n📦 Repositorios:")
    for repo, count in sorted(stats['repositories'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {repo:20} {count:>4} modelos")
    
    print(f"\n🎯 Tareas:")
    for task, count in sorted(stats['tasks'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {task:30} {count:>3} modelos")
    
    print(f"\n📚 Bibliotecas:")
    for lib, count in sorted(stats['libraries'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {lib:20} {count:>4} modelos")
    
    print(f"\n🌐 Dominios:")
    for domain, count in sorted(stats['domains'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {domain:20} {count:>4} modelos")
    
    if args.json:
        print("\n📄 JSON output:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    return 0


def sparql_command(args):
    """Generar SPARQL sin ejecutar"""
    graph = load_default_graph()
    if graph is None:
        return 1
    
    api = create_api(graph=graph)
    
    print(f"🔍 Query: '{args.query}'")
    print("=" * 70)
    
    sparql = api.get_sparql(args.query)
    
    print("\n📝 SPARQL generado:\n")
    print(sparql)
    
    return 0


def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(
        description="SearchEngine CLI - Búsqueda semántica de modelos de IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s search "PyTorch models"
  %(prog)s search "high rated NLP models" --max-results 5
  %(prog)s stats
  %(prog)s sparql "models from HuggingFace"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")
    
    # Comando: search
    search_parser = subparsers.add_parser("search", help="Búsqueda semántica")
    search_parser.add_argument("query", help="Query en lenguaje natural")
    search_parser.add_argument("--max-results", type=int, default=10, help="Máximo de resultados")
    search_parser.add_argument("--show-sparql", action="store_true", help="Mostrar SPARQL generado")
    search_parser.add_argument("--verbose", "-v", action="store_true", help="Salida detallada")
    search_parser.add_argument("--json", action="store_true", help="Output en JSON")
    search_parser.set_defaults(func=search_command)
    
    # Comando: stats
    stats_parser = subparsers.add_parser("stats", help="Estadísticas del grafo")
    stats_parser.add_argument("--json", action="store_true", help="Output en JSON")
    stats_parser.set_defaults(func=stats_command)
    
    # Comando: sparql
    sparql_parser = subparsers.add_parser("sparql", help="Generar SPARQL")
    sparql_parser.add_argument("query", help="Query en lenguaje natural")
    sparql_parser.set_defaults(func=sparql_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
