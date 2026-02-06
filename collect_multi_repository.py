#!/usr/bin/env python3
"""
Script de recolección multi-repositorio para AI Model Discovery.

Este script orquesta la recolección de modelos de múltiples fuentes:
- HuggingFace Hub
- Kaggle Models
- Civitai
- Papers With Code
- Azure AI Model Catalog

Todos los modelos se normalizan a StandardizedModel y se mapean
a la ontología DAIMO en un único grafo RDF.

Uso:
    python collect_multi_repository.py --limit 50 --output kg_multi_repo.ttl
    
    # Solo HuggingFace y Kaggle
    python collect_multi_repository.py --repos huggingface kaggle --limit 25

Autor: Edmundo Mori
Fecha: Enero 2026
"""

import argparse
import sys
from pathlib import Path

# Añadir directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.huggingface_repository import HuggingFaceRepository
from utils.kaggle_repository import KaggleRepository
from utils.civitai_repository import CivitaiRepository
from utils.pwc_repository import PWCRepository
from utils.azure_repository import AzureRepository
from knowledge_graph.multi_repository_builder import MultiRepositoryGraphBuilder


def main():
    parser = argparse.ArgumentParser(
        description="Collect AI models from multiple repositories and build RDF graph"
    )
    parser.add_argument(
        "--repos",
        nargs="+",
        choices=["huggingface", "kaggle", "civitai", "paperswithcode", "azure", "all"],
        default=["all"],
        help="Repositories to fetch from (default: all)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum models per repository (default: 50)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/ai_models_multi_repo.ttl",
        help="Output TTL file path (default: data/ai_models_multi_repo.ttl)"
    )
    parser.add_argument(
        "--ontology",
        type=str,
        default="ontologies/daimo.ttl",
        help="Path to DAIMO ontology (default: ontologies/daimo.ttl)"
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue if a repository fails (default behavior)"
    )
    
    args = parser.parse_args()
    
    # Banner
    print("=" * 80)
    print("🤖 AI Model Discovery - Multi-Repository Collector")
    print("=" * 80)
    print(f"📦 Target repositories: {', '.join(args.repos)}")
    print(f"📊 Limit per repository: {args.limit}")
    print(f"💾 Output file: {args.output}")
    print("=" * 80)
    
    # Inicializar builder
    builder = MultiRepositoryGraphBuilder(ontology_path=args.ontology)
    
    # Determinar qué repositorios activar
    repo_list = args.repos
    if "all" in repo_list:
        repo_list = ["huggingface", "kaggle", "civitai", "paperswithcode", "azure"]
    
    # Instanciar repositorios
    repositories = []
    
    if "huggingface" in repo_list:
        print("\n✅ Activating HuggingFace repository...")
        repositories.append(HuggingFaceRepository())
    
    if "kaggle" in repo_list:
        print("✅ Activating Kaggle repository...")
        print("   ⚠️  Note: Requires Kaggle API credentials")
        repositories.append(KaggleRepository())
    
    if "civitai" in repo_list:
        print("✅ Activating Civitai repository...")
        repositories.append(CivitaiRepository())
    
    if "paperswithcode" in repo_list:
        print("✅ Activating Papers With Code repository...")
        repositories.append(PWCRepository())
    
    if "azure" in repo_list:
        print("✅ Activating Azure AI repository...")
        print("   ⚠️  Note: Requires Azure credentials (az login)")
        repositories.append(AzureRepository())
    
    if not repositories:
        print("❌ No repositories activated. Exiting.")
        sys.exit(1)
    
    try:
        # Construir grafo desde todos los repositorios
        models_added = builder.build_from_repositories(
            repositories=repositories,
            limit_per_repo=args.limit
        )
        
        # Guardar grafo
        print(f"\n💾 Saving RDF graph to {args.output}...")
        builder.save(args.output)
        
        # Mostrar estadísticas
        print("\n" + "=" * 80)
        print("📊 STATISTICS")
        print("=" * 80)
        
        stats = builder.get_statistics()
        print(f"Total triples: {stats['total_triples']}")
        print(f"Total models: {models_added}")
        print(f"Repositories used: {stats['repositories']}")
        
        print("\n📦 Models by source:")
        for source, count in stats['models_by_source'].items():
            print(f"   - {source}: {count} models")
        
        print("\n🔍 Repository details:")
        for repo_stat in stats['repository_stats']:
            status = "✅" if repo_stat['success'] else "❌"
            print(f"   {status} {repo_stat['name']}: {repo_stat['models_fetched']} models")
            if repo_stat['errors']:
                for error in repo_stat['errors']:
                    print(f"      ⚠️  {error}")
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS: Multi-repository graph generation complete!")
        print(f"📄 Output: {args.output}")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
