# Consultas SPARQL de Ejemplo

Este directorio contiene consultas SPARQL predefinidas para explorar el grafo de conocimiento de modelos de IA.

## Consultas Básicas

### 1. Listar todos los modelos
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?created
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  OPTIONAL { ?model dcterms:created ?created }
}
ORDER BY DESC(?created)
LIMIT 10
```

### 2. Modelos por tarea
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:subject ?task .
  FILTER(CONTAINS(?task, "classification"))
}
LIMIT 20
```

### 3. Modelos con licencia específica
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>

SELECT ?model ?title ?license
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model odrl:hasPolicy ?licenseObj .
  ?licenseObj dcterms:identifier ?license .
  FILTER(CONTAINS(?license, "mit"))
}
```

### 4. Modelos más populares
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
}
ORDER BY DESC(?downloads)
LIMIT 10
```

### 5. Modelos por autor
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?model ?title ?author
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:creator ?authorObj .
  ?authorObj foaf:name ?author .
}
```

### 6. Modelos entrenados con dataset específico
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>

SELECT ?model ?title ?dataset
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model prov:wasDerivedFrom ?datasetObj .
  ?datasetObj dcterms:identifier ?dataset .
}
```

### 7. Modelos por librería/framework
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model daimo:library ?library .
  FILTER(?library = "transformers")
}
```

### 8. Estadísticas por tarea
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?task (COUNT(?model) as ?count)
WHERE {
  ?model a daimo:Model .
  ?model dcterms:subject ?task .
}
GROUP BY ?task
ORDER BY DESC(?count)
```

## Consultas Avanzadas

### 9. Modelos multilingües
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title (COUNT(?lang) as ?numLanguages)
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcterms:language ?lang .
}
GROUP BY ?model ?title
HAVING (COUNT(?lang) > 1)
ORDER BY DESC(?numLanguages)
```

### 10. Modelos con múltiples tags
```sparql
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>

SELECT ?model ?title (GROUP_CONCAT(?keyword; separator=", ") as ?tags)
WHERE {
  ?model a daimo:Model .
  ?model dcterms:title ?title .
  ?model dcat:keyword ?keyword .
}
GROUP BY ?model ?title
LIMIT 10
```

## Uso

Las consultas se pueden ejecutar usando:

1. **Python con RDFLib**:
```python
from knowledge_graph import DAIMOGraphBuilder

builder = DAIMOGraphBuilder()
builder.build_from_json("data/raw/hf_models.json")

query = """
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?model WHERE { ?model a daimo:Model }
"""

results = builder.query(query)
for row in results:
    print(row)
```

2. **Desde el notebook de validación** (notebooks/01_validation.ipynb)

3. **Herramientas externas**:
   - Apache Jena Fuseki
   - GraphDB
   - Protégé
