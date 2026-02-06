"""
Prompts para LLM Text-to-SPARQL
Reutiliza la ontología DAIMO v2.2 que ya existe
"""

DAIMO_ONTOLOGY_CONTEXT = """
You are a SPARQL query generator for the DAIMO ontology v2.2.

⚠️ CRITICAL CLASS REQUIREMENT:
- ALWAYS use: daimo:Model (NOT daimo:AIModel)
- Pattern: ?model a daimo:Model ;

DAIMO Ontology Structure:
- Namespace: PREFIX daimo: <http://purl.org/pionera/daimo#>
- Main Class: daimo:Model (⚠️ MANDATORY - use this, never AIModel)
- Universal Properties (10):
  * dcterms:title (model name) - ⚠️ Use dcterms prefix, NOT daimo
  * dcterms:source (repository) - ⚠️ Use dcterms prefix, NOT daimo
  * dcterms:description (model description)
  * daimo:sourceURL (model URL)
  * daimo:creator (author/organization)
  * daimo:task (ML task: Classification, NLP, Computer Vision, etc.)
  * daimo:library (framework: PyTorch, TensorFlow, scikit-learn, etc.)
  * daimo:accessLevel (public, gated, private, community)
  * daimo:downloads (integer - popularity metric)
  * daimo:likes (integer - engagement metric)

- Repository-Specific Properties:
  * HuggingFace: safetensors, cardData, githubURL
  * Kaggle: licenseName, rating
  * Civitai: rating, isNSFW, baseModel, triggerWords
  * Replicate: runCount, versionId, cogVersion
  * TensorFlow Hub: tfhubHandle, fineTunable, frameworkVersion
  * PyTorch Hub: hubRepo, entryPoint
  * PapersWithCode: arxivId, paper, yearIntroduced, citationCount, isOfficial

Available Data Sources:
- HuggingFace (25 models)
- Kaggle (25 models)
- Civitai (25 models)
- Replicate (25 models)
- TensorFlow Hub (25 models)
- PyTorch Hub (25 models)
- PapersWithCode (25 models)
Total: 175 models in the knowledge graph
"""

TEXT_TO_SPARQL_PROMPT = """
Generate a SPARQL query for the DAIMO ontology.

⚠️ CRITICAL REQUIREMENTS - FOLLOW EXACTLY:

1. **CLASS**: ?model a daimo:Model (NEVER daimo:AIModel)
2. **PREFIXES**: 
   - PREFIX daimo: <http://purl.org/pionera/daimo#>
   - PREFIX dcterms: <http://purl.org/dc/terms/>
3. **SELECT**: ALWAYS start with ?model, then other variables
4. **PROPERTY BINDING**: To filter by a property value:
   ✅ CORRECT: ?model daimo:library ?library . FILTER(LCASE(?library) = "pytorch")
   ❌ WRONG: OPTIONAL {{ ?model daimo:library 'pytorch' }}
   ❌ WRONG: ?model daimo:library 'pytorch'
5. **NAMESPACE**: 
   - dcterms:title (NOT daimo:title)
   - dcterms:source (NOT daimo:source)
   - dcterms:description (NOT daimo:description)
6. **OPTIONAL**: Only for truly optional properties (downloads, likes, etc.)
   - Use: OPTIONAL {{ ?model daimo:downloads ?downloads }}
   - NOT for filtering conditions
7. **FILTER PATTERNS**:
   - Exact match: FILTER(LCASE(?var) = "value")
   - Partial match: FILTER(CONTAINS(LCASE(?var), "value"))
   - Numeric: FILTER(?var > 1000)
8. **ALWAYS end with LIMIT** (default: 15)

NAMESPACE RULES:
- dcterms:title - Model title
- dcterms:source - Model repository (HuggingFace, PyTorch Hub, etc.)
- dcterms:description - Model description
- daimo:library - Framework/library name
- daimo:downloads - Download count
- daimo:likes - Number of likes
- daimo:task - Task type (NLP, computer vision, etc.)
- daimo:accessLevel - Access level (public, private)

SIMPLE EXAMPLES:

Input: show me models
Output:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?model ?title ?source
WHERE {{
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
}}
LIMIT 10

Input: popular models
Output:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?model ?title ?downloads
WHERE {{
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:downloads ?downloads .
}}
ORDER BY DESC(?downloads)
LIMIT 10

Input: PyTorch models
Output:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?model ?title ?library
WHERE {{
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(CONTAINS(LCASE(?library), "pytorch"))
}}
LIMIT 10

Input: count by library
Output:
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?library (COUNT(?model) AS ?count)
WHERE {{
  ?model a daimo:Model ;
         daimo:library ?library .
}}
GROUP BY ?library
ORDER BY DESC(?count)

Now generate SPARQL for this query (ONLY the SPARQL, no explanation):

User Query: {user_query}

Retrieved Examples (use as reference):
{examples}

{property_context}

SPARQL Query:

Q: "Computer vision models from any source"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?model ?title ?source ?task ?library ?downloads
WHERE {{
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:task ?task .
  OPTIONAL {{ ?model daimo:library ?library }}
  OPTIONAL {{ ?model daimo:downloads ?downloads }}
  FILTER(CONTAINS(LCASE(?task), "computer vision") || CONTAINS(LCASE(?task), "image") || CONTAINS(LCASE(?task), "vision"))
}}
ORDER BY DESC(?downloads)
LIMIT 15

Q: "Compare TensorFlow vs PyTorch models by popularity"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?library (COUNT(?model) as ?modelCount) (AVG(?downloads) as ?avgDownloads) (MAX(?downloads) as ?maxDownloads)
WHERE {{
  ?model a daimo:Model ;
         daimo:library ?library .
  OPTIONAL {{ ?model daimo:downloads ?downloads }}
  FILTER(CONTAINS(LCASE(?library), "tensorflow") || CONTAINS(LCASE(?library), "pytorch"))
}}
GROUP BY ?library
ORDER BY DESC(?avgDownloads)

Q: "Find models with both high downloads and high likes"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?model ?title ?source ?downloads ?likes ?task
WHERE {{
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:downloads ?downloads ;
         daimo:likes ?likes .
  OPTIONAL {{ ?model daimo:task ?task }}
  FILTER(?downloads > 50000 && ?likes > 100)
}}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 10

Q: "Models from HuggingFace for NLP"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?model ?title ?source ?task ?downloads
WHERE {{
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:task ?task .
  OPTIONAL {{ ?model daimo:downloads ?downloads }}
  FILTER(
    CONTAINS(LCASE(STR(?source)), "huggingface") &&
    (CONTAINS(LCASE(?task), "nlp") || CONTAINS(LCASE(?task), "language") || CONTAINS(LCASE(?task), "text"))
  )
}}
ORDER BY DESC(?downloads)
LIMIT 15

Q: "Statistical analysis: average downloads by repository"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?source (COUNT(?model) as ?totalModels) (AVG(?downloads) as ?avgDownloads) (MAX(?downloads) as ?maxDownloads) (MIN(?downloads) as ?minDownloads)
WHERE {{
  ?model a daimo:AIModel ;
         daimo:source ?source .
  OPTIONAL {{ ?model daimo:downloads ?downloads }}
  FILTER(BOUND(?downloads))
}}
GROUP BY ?source
ORDER BY DESC(?avgDownloads)

Q: "Find similar models: PyTorch + Computer Vision + high popularity"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?title ?source ?library ?task ?downloads ?likes
WHERE {{
  ?model a daimo:AIModel ;
         daimo:title ?title ;
         daimo:source ?source ;
         daimo:library ?library ;
         daimo:task ?task .
  OPTIONAL {{ ?model daimo:downloads ?downloads }}
  OPTIONAL {{ ?model daimo:likes ?likes }}
  FILTER(
    CONTAINS(LCASE(?library), "pytorch") &&
    (CONTAINS(LCASE(?task), "vision") || CONTAINS(LCASE(?task), "image")) &&
    (?downloads > 10000 || ?likes > 100)
  )
}}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 15

Q: "Models NOT from HuggingFace with TensorFlow framework"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?source ?library ?task ?downloads
WHERE {{
  ?model a daimo:AIModel ;
         daimo:source ?source ;
         daimo:title ?title ;
         daimo:library ?library .
  OPTIONAL {{ ?model daimo:task ?task }}
  OPTIONAL {{ ?model daimo:downloads ?downloads }}
  FILTER(
    ?source != "HuggingFace"^^xsd:string &&
    CONTAINS(LCASE(?library), "tensorflow")
  )
}}
ORDER BY DESC(?downloads)
LIMIT 10

Q: "Find generative models (Civitai or Replicate) with version control"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?source ?versionId ?baseModel ?runCount ?task
WHERE {{
  ?model a daimo:AIModel ;
         daimo:source ?source ;
         daimo:title ?title .
  OPTIONAL {{ ?model daimo:versionId ?versionId }}
  OPTIONAL {{ ?model daimo:baseModel ?baseModel }}
  OPTIONAL {{ ?model daimo:runCount ?runCount }}
  OPTIONAL {{ ?model daimo:task ?task }}
  FILTER(
    (?source = "Civitai"^^xsd:string || ?source = "Replicate"^^xsd:string) &&
    (BOUND(?versionId) || BOUND(?baseModel))
  )
}}
ORDER BY DESC(?runCount)
LIMIT 15

Q: "Cross-repository search: models with GitHub links and high engagement"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?title ?source ?githubURL ?likes ?downloads ?task
WHERE {{
  ?model a daimo:AIModel ;
         daimo:title ?title ;
         daimo:source ?source ;
         daimo:githubURL ?githubURL .
  OPTIONAL {{ ?model daimo:likes ?likes }}
  OPTIONAL {{ ?model daimo:downloads ?downloads }}
  OPTIONAL {{ ?model daimo:task ?task }}
  FILTER(BOUND(?githubURL) && (?likes > 50 || ?downloads > 5000))
}}
ORDER BY DESC(?likes) DESC(?downloads)
LIMIT 20

Q: "Distribution analysis: count models by task category"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?task (COUNT(?model) as ?count)
WHERE {{
  ?model a daimo:AIModel ;
         daimo:task ?task .
}}
GROUP BY ?task
ORDER BY DESC(?count)

Q: "Multi-criteria search: NLP + recent papers + official implementation"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?arxivId ?yearIntroduced ?isOfficial ?paper ?task
WHERE {{
  ?model a daimo:AIModel ;
         daimo:source "PapersWithCode"^^xsd:string ;
         daimo:title ?title ;
         daimo:task ?task .
  OPTIONAL {{ ?model daimo:arxivId ?arxivId }}
  OPTIONAL {{ ?model daimo:yearIntroduced ?yearIntroduced }}
  OPTIONAL {{ ?model daimo:isOfficial ?isOfficial }}
  OPTIONAL {{ ?model daimo:paper ?paper }}
  FILTER(
    (CONTAINS(LCASE(?task), "nlp") || CONTAINS(LCASE(?task), "language")) &&
    (?yearIntroduced > 2022 || !BOUND(?yearIntroduced)) &&
    (?isOfficial = true || !BOUND(?isOfficial))
  )
}}
ORDER BY DESC(?yearIntroduced)
LIMIT 15

Q: "Complex aggregation: models by source with multiple metrics"
A:
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?source 
       (COUNT(DISTINCT ?model) as ?totalModels)
       (COUNT(DISTINCT ?task) as ?uniqueTasks)
       (AVG(?downloads) as ?avgPopularity)
       (SUM(?likes) as ?totalEngagement)
WHERE {{
  ?model a daimo:AIModel ;
         daimo:source ?source .
  OPTIONAL {{ ?model daimo:task ?task }}
  OPTIONAL {{ ?model daimo:downloads ?downloads }}
  OPTIONAL {{ ?model daimo:likes ?likes }}
}}
GROUP BY ?source
HAVING (COUNT(?model) > 5)
ORDER BY DESC(?totalModels)

Now convert this query:
User Query: {user_query}

Generate ONLY the SPARQL query without any explanation or markdown formatting.
"""

def build_prompt(user_query: str) -> str:
    """
    Construye el prompt completo para el LLM
    
    Args:
        user_query: Consulta en lenguaje natural del usuario
        
    Returns:
        Prompt formateado listo para enviar al LLM
    """
    return TEXT_TO_SPARQL_PROMPT.format(
        ontology_context=DAIMO_ONTOLOGY_CONTEXT,
        user_query=user_query
    )


# Queries de ejemplo para testing
EXAMPLE_QUERIES = [
    # Básicas
    "show me the most popular models",
    "computer vision models",
    "models from HuggingFace",
    "PyTorch models with more than 1000 downloads",
    "text generation models",
    "models with public access",
    
    # Intermedias
    "NLP models for sentiment analysis",
    "image classification with TensorFlow",
    "generative models from Civitai",
    "academic papers about deep learning",
    
    # Avanzadas - Comparaciones
    "compare TensorFlow vs PyTorch models",
    "which repository has the most models",
    
    # Avanzadas - Multi-criterio
    "PyTorch models for computer vision with high downloads",
    "public NLP models from HuggingFace or Kaggle",
    "models with both GitHub link and high rating",
    
    # Avanzadas - Agregaciones
    "average downloads by repository",
    "count models by task category",
    "total engagement metrics per source",
    
    # Avanzadas - Filtros complejos
    "models NOT from HuggingFace with TensorFlow",
    "papers published after 2020 with official implementations",
    "generative models with version control from Civitai or Replicate",
    
    # Avanzadas - Análisis estadístico
    "repositories ranked by average model popularity",
    "distribution of models across different tasks",
    "models with downloads above average for their repository"
]

# Categorías de complejidad de queries
QUERY_COMPLEXITY = {
    'basic': [
        "show me models",
        "find PyTorch models",
        "list computer vision models"
    ],
    'intermediate': [
        "NLP models with high downloads",
        "TensorFlow models from specific repository",
        "models with public access and GitHub link"
    ],
    'advanced': [
        "compare repositories by average downloads",
        "models matching multiple criteria with aggregation",
        "statistical analysis across sources with grouping"
    ]
}

# Patterns de queries avanzadas para el LLM
ADVANCED_QUERY_PATTERNS = """
Advanced Query Patterns:

1. AGGREGATION with GROUP BY:
   - COUNT, AVG, SUM, MAX, MIN
   - Use HAVING for post-aggregation filtering
   - Example: Count models per repository with average metrics

2. MULTI-CRITERIA FILTERING:
   - Combine multiple FILTER conditions with && (AND) and || (OR)
   - Use != for negation
   - Example: Models from source A OR B, with property X AND NOT property Y

3. EXISTENCE CHECKS:
   - Use BOUND(?variable) to check if optional property exists
   - Useful for "models with GitHub links" or "papers with arXiv IDs"

4. COMPLEX ORDERING:
   - Order by multiple columns: ORDER BY DESC(?col1) DESC(?col2)
   - Useful for "sort by downloads then by rating"

5. NUMERIC COMPARISONS:
   - Use >, <, >=, <=, = for numeric filters
   - Example: ?downloads > 10000 && ?rating >= 4.0

6. SUBQUERIES (when needed):
   - Can nest SELECT in FROM or FILTER
   - Use for "above average" calculations

7. DISTINCT:
   - Use COUNT(DISTINCT ?var) to avoid duplicates in aggregations
   - Example: Count unique tasks per repository
"""
