"""
Script rápido de validación del grafo RDF.

Ejecuta consultas SPARQL básicas para verificar que el grafo se construyó correctamente.
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from knowledge_graph.build_graph import DAIMOGraphBuilder

def main():
    print("=" * 60)
    print("VALIDACIÓN DEL GRAFO RDF")
    print("=" * 60)
    print()
    
    # Cargar grafo desde archivo
    graph_file = "data/ai_models_multi_repo.ttl"
    print(f"📚 Cargando grafo desde: {graph_file}")
    
    builder = DAIMOGraphBuilder()
    builder.graph.parse(graph_file, format="turtle")
    
    print(f"✅ Grafo cargado: {len(builder.graph)} triples")
    print()
    
    # Consulta 1: Contar modelos
    print("1️⃣  Contando modelos totales...")
    query1 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    SELECT (COUNT(?model) as ?count)
    WHERE { ?model a daimo:Model }
    """
    result = list(builder.query(query1))
    print(f"   Total de modelos: {result[0][0]}")
    print()
    
    # Consulta 2: Primeros 5 modelos
    print("2️⃣  Primeros 5 modelos:")
    query2 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?title
    WHERE {
      ?model a daimo:Model .
      ?model dcterms:title ?title .
    }
    LIMIT 5
    """
    results = builder.query(query2)
    for i, row in enumerate(results, 1):
        print(f"   {i}. {row.title}")
    print()
    
    # Consulta 3: Modelos por tarea
    print("3️⃣  Distribución por tipo de tarea:")
    query3 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?task (COUNT(?model) as ?count)
    WHERE {
      ?model a daimo:Model .
      OPTIONAL { ?model dcterms:subject ?task }
    }
    GROUP BY ?task
    ORDER BY DESC(?count)
    LIMIT 5
    """
    results = builder.query(query3)
    for row in results:
        task = str(row.task) if row.task else "sin clasificar"
        count = int(row['count']) if row['count'] else 0
        print(f"   {task}: {count} modelos")
    print()
    
    # Consulta 4: Modelos más populares
    print("4️⃣  Top 5 modelos por descargas:")
    query4 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?title ?downloads
    WHERE {
      ?model a daimo:Model .
      ?model dcterms:title ?title .
      OPTIONAL { ?model daimo:downloads ?downloads }
    }
    ORDER BY DESC(?downloads)
    LIMIT 5
    """
    results = builder.query(query4)
    for i, row in enumerate(results, 1):
        downloads = int(row.downloads) if row.downloads else 0
        print(f"   {i}. {row.title} - {downloads:,} descargas")
    print()
    
    # Consulta 5: Autores
    print("5️⃣  Top 5 autores/organizaciones:")
    query5 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?author (COUNT(?model) as ?count)
    WHERE {
      ?model a daimo:Model .
      ?model dcterms:creator ?authorObj .
      ?authorObj foaf:name ?author .
    }
    GROUP BY ?author
    ORDER BY DESC(?count)
    LIMIT 5
    """
    results = builder.query(query5)
    for i, row in enumerate(results, 1):
        count = int(row['count']) if row['count'] else 0
        print(f"   {i}. {row.author}: {count} modelos")
    print()
    
    print("=" * 60)
    print("✅ VALIDACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("El grafo RDF está funcionando correctamente.")
    print("Puedes explorar más en el notebook: notebooks/01_validation.ipynb")

if __name__ == "__main__":
    main()
