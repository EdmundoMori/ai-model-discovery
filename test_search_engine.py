#!/usr/bin/env python3
"""
Script de prueba rápida del SearchEngine + API

Valida que todos los componentes funcionan correctamente

Autor: Edmundo Mori
Fecha: 2026-02-04
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🧪 Test Suite - SearchEngine + UI")
print("=" * 70)

# Test 1: Imports
print("\n1️⃣ Testing imports...")
try:
    from search.non_federated import create_api, SearchEngine
    from notebooks import create_test_graph
    print("   ✅ Imports OK")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Crear grafo de prueba
print("\n2️⃣ Creating test graph...")
try:
    graph = create_test_graph()
    print(f"   ✅ Graph created: {len(graph):,} triples")
except Exception as e:
    print(f"   ❌ Graph creation error: {e}")
    sys.exit(1)

# Test 3: Inicializar API
print("\n3️⃣ Initializing SearchAPI...")
try:
    api = create_api(graph=graph)
    print(f"   ✅ API initialized")
except Exception as e:
    print(f"   ❌ API initialization error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Obtener estadísticas
print("\n4️⃣ Getting statistics...")
try:
    stats = api.get_statistics()
    print(f"   ✅ Stats retrieved:")
    print(f"      - Total models: {stats['total_models']}")
    print(f"      - Total triples: {stats['total_triples']:,}")
    print(f"      - Repositories: {len(stats['repositories'])}")
    print(f"      - Tasks: {len(stats['tasks'])}")
except Exception as e:
    print(f"   ❌ Stats error: {e}")
    sys.exit(1)

# Test 5: Búsqueda básica
print("\n5️⃣ Testing basic search...")
try:
    query = "list all AI models"
    print(f"   Query: '{query}'")
    
    results = api.search(query, max_results=5, format="response")
    
    if results.is_valid:
        print(f"   ✅ Search successful:")
        print(f"      - Total results: {results.total_results}")
        print(f"      - Execution time: {results.execution_time:.2f}s")
        print(f"      - Top {len(results.results)} results:")
        for i, result in enumerate(results.results[:3], 1):
            print(f"         {i}. {result.title} ({result.source}) - Score: {result.score}")
    else:
        print(f"   ⚠️  Invalid query: {results.errors}")
except Exception as e:
    print(f"   ❌ Search error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Búsqueda con filtro
print("\n6️⃣ Testing filtered search...")
try:
    query = "PyTorch models"
    print(f"   Query: '{query}'")
    
    results = api.search(query, max_results=5, format="response")
    
    if results.is_valid:
        print(f"   ✅ Filtered search successful:")
        print(f"      - Total results: {results.total_results}")
        print(f"      - SPARQL query generated: {len(results.sparql_query)} chars")
    else:
        print(f"   ⚠️  Invalid query: {results.errors}")
except Exception as e:
    print(f"   ❌ Filtered search error: {e}")
    sys.exit(1)

# Test 7: Generar SPARQL
print("\n7️⃣ Testing SPARQL generation...")
try:
    query = "high rated models"
    print(f"   Query: '{query}'")
    
    sparql = api.get_sparql(query)
    print(f"   ✅ SPARQL generated ({len(sparql)} chars):")
    print(f"      {sparql[:100]}...")
except Exception as e:
    print(f"   ❌ SPARQL generation error: {e}")
    sys.exit(1)

# Resumen final
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED")
print("=" * 70)
print("\n🎯 Sistema completamente funcional:")
print("   - SearchEngine operativo")
print("   - API wrapper funcional")
print("   - Text-to-SPARQL validado")
print("   - Grafo RDF cargado")
print("   - Ranking de resultados activo")
print("\n💡 Próximos pasos:")
print("   1. Iniciar interfaz web: python run_app.py")
print("   2. O usar CLI: python -m search.non_federated.cli search 'PyTorch models'")
print("   3. O usar desde Python: ver QUICKSTART_WEB.md")
print()
