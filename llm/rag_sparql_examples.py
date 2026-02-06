"""
RAG Knowledge Base: SPARQL Query Examples
Base de conocimiento para retrieval de ejemplos relevantes
"""

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class SPARQLExample:
    """Ejemplo de query SPARQL con metadata para RAG"""
    id: str
    natural_query: str
    sparql_query: str
    complexity: str  # basic, intermediate, advanced
    category: str    # aggregation, filter, multi-criteria, etc.
    keywords: List[str]
    explanation: str

# Base de conocimiento de ejemplos SPARQL
SPARQL_KNOWLEDGE_BASE = [
    # === BÁSICOS ===
    SPARQLExample(
        id="basic_001",
        natural_query="list all models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?title ?source ?library
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:library ?library }
}
LIMIT 20""",
        complexity="basic",
        category="simple_select",
        keywords=["all", "list", "show", "models"],
        explanation="Simple selection of all models with basic metadata"
    ),
    
    SPARQLExample(
        id="basic_002",
        natural_query="high rated computer vision models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?title ?likes ?downloads ?library
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:library ?library }
  FILTER(BOUND(?likes) && ?likes > 10)
}
ORDER BY DESC(?likes) DESC(?downloads)
LIMIT 15""",
        complexity="basic",
        category="text_filter",
        keywords=["high rated", "likes", "popular", "computer vision", "vision", "image", "cv"],
        explanation="Filtering by likes (rating) with numeric comparison"
    ),
    
    SPARQLExample(
        id="basic_003",
        natural_query="models from HuggingFace",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?title ?downloads ?likes
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(CONTAINS(LCASE(STR(?source)), "huggingface"))
}
ORDER BY DESC(?downloads)
LIMIT 15""",
        complexity="basic",
        category="source_filter",
        keywords=["huggingface", "from", "repository", "source"],
        explanation="Filtering by HuggingFace source using case-insensitive search"
    ),
    
    # === INTERMEDIOS ===
    SPARQLExample(
        id="intermediate_001",
        natural_query="PyTorch models for NLP",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?library ?task ?downloads
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(
    CONTAINS(LCASE(?library), "pytorch") &&
    (!BOUND(?task) || CONTAINS(LCASE(?task), "nlp") || CONTAINS(LCASE(?task), "language") || CONTAINS(LCASE(?task), "text"))
  )
}
ORDER BY DESC(?downloads)
LIMIT 15""",
        complexity="intermediate",
        category="multi_filter",
        keywords=["pytorch", "nlp", "natural language", "framework", "library", "text"],
        explanation="PyTorch models with optional NLP task filtering - task is OPTIONAL to avoid over-filtering"
    ),
    
    SPARQLExample(
        id="intermediate_002",
        natural_query="most popular models by downloads",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?title ?downloads ?source ?library
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:downloads ?downloads .
  OPTIONAL { ?model dcterms:source ?source }
  OPTIONAL { ?model daimo:library ?library }
  FILTER(?downloads > 0)
}
ORDER BY DESC(?downloads)
LIMIT 20""",
        complexity="intermediate",
        category="multi_criteria",
        keywords=["popular", "most", "top", "downloads", "ranking"],
        explanation="Models ranked by download count with positive downloads filter"
    ),
    
    SPARQLExample(
        id="intermediate_003",
        natural_query="count models for task",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?library (COUNT(?model) as ?modelCount)
WHERE {
  ?model a daimo:Model ;
         daimo:library ?library .
}
GROUP BY ?library
ORDER BY DESC(?modelCount)""",
        complexity="intermediate",
        category="aggregation",
        keywords=["count", "group by", "library", "task", "aggregate", "statistics"],
        explanation="Count models grouped by library/framework using GROUP BY"
    ),
    
    # === NUEVOS EJEMPLOS: PYTORCH + NLP ===
    SPARQLExample(
        id="intermediate_004",
        natural_query="pytorch models for nlp",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(
    CONTAINS(LCASE(?library), "pytorch") &&
    (!BOUND(?task) || 
     CONTAINS(LCASE(?task), "nlp") || 
     CONTAINS(LCASE(?task), "natural language") ||
     CONTAINS(LCASE(?task), "text"))
  )
}
LIMIT 15""",
        complexity="intermediate",
        category="library_task_filter",
        keywords=["pytorch", "nlp", "natural language", "text", "optional", "bound"],
        explanation="Finds PyTorch models for NLP using OPTIONAL with !BOUND to handle NULL tasks safely"
    ),
    
    SPARQLExample(
        id="intermediate_005",
        natural_query="pytorch models with nlp in title",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(
    CONTAINS(LCASE(?library), "pytorch") &&
    (CONTAINS(LCASE(?title), "nlp") || 
     CONTAINS(LCASE(?title), "language") ||
     CONTAINS(LCASE(?title), "text") ||
     CONTAINS(LCASE(?title), "sentiment") ||
     CONTAINS(LCASE(?title), "translation"))
  )
}
LIMIT 15""",
        complexity="intermediate",
        category="title_based_filter",
        keywords=["pytorch", "nlp", "language", "text", "title", "sentiment", "translation"],
        explanation="Finds PyTorch NLP models by detecting keywords in title (nlp, language, text, sentiment)"
    ),
    
    SPARQLExample(
        id="intermediate_006",
        natural_query="transformer models for natural language",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(
    CONTAINS(LCASE(?library), "transformers") ||
    (CONTAINS(LCASE(?library), "pytorch") && CONTAINS(LCASE(?title), "bert"))
  )
}
LIMIT 15""",
        complexity="intermediate",
        category="library_alternative",
        keywords=["transformers", "huggingface", "bert", "natural language", "nlp"],
        explanation="Finds models using transformers library or PyTorch BERT models (common for NLP)"
    ),
    
    # === AVANZADOS - AGREGACIÓN ===
    SPARQLExample(
        id="advanced_001",
        natural_query="compare TensorFlow vs PyTorch by popularity",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?library (COUNT(?model) as ?modelCount) (AVG(?downloads) as ?avgDownloads) (MAX(?downloads) as ?maxDownloads)
WHERE {
  ?model a daimo:Model ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(CONTAINS(LCASE(?library), "tensorflow") || CONTAINS(LCASE(?library), "pytorch"))
}
GROUP BY ?library
ORDER BY DESC(?avgDownloads)""",
        complexity="advanced",
        category="aggregation",
        keywords=["compare", "vs", "comparison", "average", "aggregate", "group"],
        explanation="GROUP BY with multiple aggregations (COUNT, AVG, MAX)"
    ),
    
    SPARQLExample(
        id="advanced_002",
        natural_query="average downloads by repository",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?source (COUNT(?model) as ?totalModels) (AVG(?downloads) as ?avgDownloads) (MAX(?downloads) as ?maxDownloads) (MIN(?downloads) as ?minDownloads)
WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(BOUND(?downloads))
}
GROUP BY ?source
ORDER BY DESC(?avgDownloads)""",
        complexity="advanced",
        category="aggregation",
        keywords=["average", "by repository", "statistics", "aggregate", "per source"],
        explanation="Statistical aggregation per repository with BOUND check"
    ),
    
    SPARQLExample(
        id="advanced_003",
        natural_query="count models by task category",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?task (COUNT(?model) as ?count)
WHERE {
  ?model a daimo:Model ;
         daimo:task ?task .
}
GROUP BY ?task
ORDER BY DESC(?count)""",
        complexity="advanced",
        category="aggregation",
        keywords=["count", "distribution", "by task", "category", "breakdown"],
        explanation="Simple GROUP BY for distribution analysis"
    ),
    
    # === AVANZADOS - MULTI-CRITERIO ===
    SPARQLExample(
        id="advanced_004",
        natural_query="PyTorch models for computer vision with high engagement",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?title ?source ?library ?task ?downloads ?likes
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:library ?library ;
         daimo:task ?task .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(
    CONTAINS(LCASE(?library), "pytorch") &&
    (CONTAINS(LCASE(?task), "vision") || CONTAINS(LCASE(?task), "image")) &&
    (?downloads > 10000 || ?likes > 100)
  )
}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 15""",
        complexity="advanced",
        category="multi_criteria",
        keywords=["pytorch", "computer vision", "high", "engagement", "multiple conditions"],
        explanation="Three-way filtering: library + task + metrics"
    ),
    
    SPARQLExample(
        id="advanced_005",
        natural_query="models NOT from HuggingFace with TensorFlow",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?source ?library ?task ?downloads
WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         dcterms:title ?title ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(
    ?source != "HuggingFace"^^xsd:string &&
    CONTAINS(LCASE(?library), "tensorflow")
  )
}
ORDER BY DESC(?downloads)
LIMIT 10""",
        complexity="advanced",
        category="negation",
        keywords=["not", "exclude", "except", "without", "negation"],
        explanation="Negation with != for exclusion filtering"
    ),
    
    # === AVANZADOS - ACADÉMICO ===
    SPARQLExample(
        id="advanced_006",
        natural_query="academic papers published after 2020 with official implementations",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?arxivId ?paper ?yearIntroduced ?isOfficial ?task
WHERE {
  ?model a daimo:Model ;
         dcterms:source "PapersWithCode"^^xsd:string ;
         dcterms:title ?title ;
         daimo:yearIntroduced ?year .
  OPTIONAL { ?model daimo:arxivId ?arxivId }
  OPTIONAL { ?model daimo:paper ?paper }
  OPTIONAL { ?model daimo:isOfficial ?isOfficial }
  OPTIONAL { ?model daimo:task ?task }
  FILTER(?year > 2020 && (?isOfficial = true || !BOUND(?isOfficial)))
}
ORDER BY DESC(?year)
LIMIT 20""",
        complexity="advanced",
        category="academic",
        keywords=["papers", "academic", "recent", "after", "official", "arxiv", "year"],
        explanation="Temporal filtering with optional boolean check"
    ),
    
    # === AVANZADOS - EXISTENCIA ===
    SPARQLExample(
        id="advanced_007",
        natural_query="models with GitHub links and high engagement",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?title ?source ?githubURL ?likes ?downloads ?task
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:githubURL ?githubURL .
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:task ?task }
  FILTER(BOUND(?githubURL) && (?likes > 50 || ?downloads > 5000))
}
ORDER BY DESC(?likes) DESC(?downloads)
LIMIT 20""",
        complexity="advanced",
        category="existence",
        keywords=["with", "has", "github", "link", "bound", "exists"],
        explanation="BOUND() to check property existence"
    ),
    
    # === AVANZADOS - AGREGACIÓN COMPLEJA ===
    SPARQLExample(
        id="advanced_008",
        natural_query="repositories with multiple metrics aggregated",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?source 
       (COUNT(DISTINCT ?model) as ?totalModels)
       (COUNT(DISTINCT ?task) as ?uniqueTasks)
       (AVG(?downloads) as ?avgPopularity)
       (SUM(?likes) as ?totalEngagement)
WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
}
GROUP BY ?source
HAVING (COUNT(?model) > 5)
ORDER BY DESC(?totalModels)""",
        complexity="advanced",
        category="complex_aggregation",
        keywords=["multiple metrics", "aggregation", "having", "distinct", "statistics"],
        explanation="Complex aggregation with HAVING clause and DISTINCT"
    ),
    
    # === NUEVOS EJEMPLOS DEL NOTEBOOK 02 - MULTI-REPOSITORY ===
    
    SPARQLExample(
        id="advanced_009",
        natural_query="production-ready models with inference endpoints",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?title ?source ?inferenceEndpoint ?downloads ?task
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:inferenceEndpoint ?inferenceEndpoint .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:task ?task }
  FILTER(BOUND(?inferenceEndpoint))
}
ORDER BY DESC(?downloads)
LIMIT 25""",
        complexity="advanced",
        category="deployment",
        keywords=["production", "inference", "endpoint", "deployment", "ready", "api"],
        explanation="Filter by inference endpoint for production-ready models"
    ),
    
    SPARQLExample(
        id="advanced_010",
        natural_query="compare popularity metrics across repositories",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?title ?source ?downloads ?likes ?runCount ?task
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:runCount ?runCount }
  OPTIONAL { ?model daimo:task ?task }
  FILTER(BOUND(?downloads) || BOUND(?likes) || BOUND(?runCount))
}
ORDER BY DESC(?downloads) DESC(?likes) DESC(?runCount)
LIMIT 30""",
        complexity="advanced",
        category="multi_metric_comparison",
        keywords=["compare", "popularity", "metrics", "downloads", "likes", "runs", "multiple"],
        explanation="Multi-metric popularity comparison with multiple OPTIONAL clauses"
    ),
    
    SPARQLExample(
        id="advanced_011",
        natural_query="task distribution analysis across all repositories",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?task (COUNT(?model) as ?modelCount)
WHERE {
  ?model a daimo:Model ;
         daimo:task ?task .
  FILTER(BOUND(?task))
}
GROUP BY ?task
ORDER BY DESC(?modelCount)
LIMIT 20""",
        complexity="advanced",
        category="distribution_analysis",
        keywords=["distribution", "task", "breakdown", "analysis", "count", "by task"],
        explanation="Task distribution with GROUP BY and COUNT"
    ),
    
    SPARQLExample(
        id="advanced_012",
        natural_query="models by access level and content restrictions",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?source ?accessLevel ?nsfw ?task ?downloads
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:accessLevel ?accessLevel }
  OPTIONAL { ?model daimo:nsfw ?nsfw }
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(?accessLevel = "public"^^xsd:string || !BOUND(?accessLevel))
}
ORDER BY DESC(?downloads)
LIMIT 25""",
        complexity="advanced",
        category="access_control",
        keywords=["access", "public", "private", "nsfw", "restrictions", "content", "level"],
        explanation="Access level filtering with NSFW consideration"
    ),
    
    SPARQLExample(
        id="advanced_013",
        natural_query="model versioning information from Replicate",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?versionId ?cogVersion ?endpoint ?runCount ?owner
WHERE {
  ?model a daimo:Model ;
         dcterms:source "Replicate"^^xsd:string ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:versionId ?versionId }
  OPTIONAL { ?model daimo:cogVersion ?cogVersion }
  OPTIONAL { ?model daimo:inferenceEndpoint ?endpoint }
  OPTIONAL { ?model daimo:runCount ?runCount }
  OPTIONAL { ?model daimo:owner ?owner }
  FILTER(BOUND(?versionId))
}
ORDER BY DESC(?runCount)
LIMIT 20""",
        complexity="advanced",
        category="versioning",
        keywords=["version", "replicate", "cog", "versioning", "specific", "repository-specific"],
        explanation="Repository-specific properties for version tracking"
    ),
    
    SPARQLExample(
        id="advanced_014",
        natural_query="repository statistics with all aggregations",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?source 
       (COUNT(?model) as ?total)
       (AVG(?downloads) as ?avgDownloads)
       (MAX(?downloads) as ?maxDownloads)
       (MIN(?downloads) as ?minDownloads)
       (SUM(?downloads) as ?totalDownloads)
WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:downloads ?downloads .
  FILTER(BOUND(?downloads))
}
GROUP BY ?source
ORDER BY DESC(?totalDownloads)""",
        complexity="advanced",
        category="comprehensive_statistics",
        keywords=["statistics", "repository", "all", "comprehensive", "avg", "max", "min", "sum", "total"],
        explanation="Complete statistical analysis per repository with all aggregations"
    ),
    
    SPARQLExample(
        id="advanced_015",
        natural_query="academic models with paper metadata",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?paper ?yearIntroduced ?arxivId ?isOfficial ?task ?framework
WHERE {
  ?model a daimo:Model ;
         dcterms:source "PapersWithCode"^^xsd:string ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:paper ?paper }
  OPTIONAL { ?model daimo:yearIntroduced ?yearIntroduced }
  OPTIONAL { ?model daimo:arxivId ?arxivId }
  OPTIONAL { ?model daimo:isOfficial ?isOfficial }
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:framework ?framework }
}
ORDER BY DESC(?yearIntroduced)
LIMIT 25""",
        complexity="advanced",
        category="academic_metadata",
        keywords=["academic", "paper", "arxiv", "official", "research", "publication", "paperswithcode"],
        explanation="Academic paper metadata with multiple optional properties"
    ),
    
    SPARQLExample(
        id="advanced_016",
        natural_query="multi-repository comparison with task filtering",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?source ?task ?downloads ?likes ?library
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:task ?task .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:library ?library }
  FILTER(
    (?source = "HuggingFace"^^xsd:string || 
     ?source = "Kaggle"^^xsd:string || 
     ?source = "Replicate"^^xsd:string) &&
    CONTAINS(LCASE(?task), "text-generation")
  )
}
ORDER BY DESC(?downloads)
LIMIT 20""",
        complexity="advanced",
        category="multi_repo_filter",
        keywords=["multiple repositories", "comparison", "text-generation", "nlp", "across"],
        explanation="Filter across multiple repositories with task matching"
    ),
    
    SPARQLExample(
        id="advanced_017",
        natural_query="models with complete metadata from all sources",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?title ?source ?task ?library ?downloads ?likes ?accessLevel ?nsfw
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:task ?task ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:accessLevel ?accessLevel }
  OPTIONAL { ?model daimo:nsfw ?nsfw }
  FILTER(
    BOUND(?task) && 
    BOUND(?library) && 
    (BOUND(?downloads) || BOUND(?likes))
  )
}
ORDER BY DESC(?downloads)
LIMIT 30""",
        complexity="advanced",
        category="complete_metadata",
        keywords=["complete", "metadata", "rich", "full", "all properties", "comprehensive"],
        explanation="Filter models with complete metadata across multiple properties"
    ),
    
    SPARQLExample(
        id="advanced_018",
        natural_query="aggregate downloads and likes by task category",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?task 
       (COUNT(?model) as ?modelCount)
       (AVG(?downloads) as ?avgDownloads)
       (SUM(?likes) as ?totalLikes)
       (MAX(?downloads) as ?topDownloads)
WHERE {
  ?model a daimo:Model ;
         daimo:task ?task .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(BOUND(?task))
}
GROUP BY ?task
HAVING (COUNT(?model) > 3)
ORDER BY DESC(?avgDownloads)
LIMIT 15""",
        complexity="advanced",
        category="task_aggregation",
        keywords=["aggregate", "by task", "category", "average", "sum", "group by task"],
        explanation="Task-based aggregation with multiple metrics and HAVING clause"
    ),
    
    # === NUEVOS EJEMPLOS: MULTI-SOURCE (Kaggle, Replicate) ===
    SPARQLExample(
        id="multi_source_001",
        natural_query="models from kaggle or replicate",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  FILTER(CONTAINS(LCASE(STR(?source)), "kaggle") || 
         CONTAINS(LCASE(STR(?source)), "replicate"))
}
LIMIT 20""",
        complexity="intermediate",
        category="multi_source_filter",
        keywords=["kaggle", "replicate", "multiple", "sources", "repositories", "or"],
        explanation="Filter models from Kaggle OR Replicate repositories"
    ),
    
    SPARQLExample(
        id="multi_source_002",
        natural_query="kaggle or replicate models with downloads",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?downloads ?runCount WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:runCount ?runCount }
  FILTER(CONTAINS(LCASE(STR(?source)), "kaggle") || 
         CONTAINS(LCASE(STR(?source)), "replicate"))
}
ORDER BY DESC(?downloads) DESC(?runCount)
LIMIT 20""",
        complexity="intermediate",
        category="multi_source_metrics",
        keywords=["kaggle", "replicate", "downloads", "metrics", "popular", "runs"],
        explanation="Multi-repository models sorted by engagement metrics"
    ),
    
    SPARQLExample(
        id="multi_source_003",
        natural_query="kaggle or replicate models by task",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?task ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:library ?library }
  FILTER(CONTAINS(LCASE(STR(?source)), "kaggle") || 
         CONTAINS(LCASE(STR(?source)), "replicate"))
}
LIMIT 20""",
        complexity="intermediate",
        category="multi_source_task",
        keywords=["kaggle", "replicate", "task", "category", "library", "framework"],
        explanation="Multi-repository models with task and library information"
    ),
    
    SPARQLExample(
        id="multi_source_004",
        natural_query="kaggle models for nlp",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(
    CONTAINS(LCASE(STR(?source)), "kaggle") &&
    (!BOUND(?task) || CONTAINS(LCASE(?task), "nlp") || CONTAINS(LCASE(?task), "text"))
  )
}
LIMIT 15""",
        complexity="intermediate",
        category="source_task_specific",
        keywords=["kaggle", "nlp", "text", "natural language", "source-specific"],
        explanation="Kaggle-specific models filtered by NLP/text task"
    ),
    
    # === NUEVOS EJEMPLOS: HUGGINGFACE DOWNLOADS ===
    SPARQLExample(
        id="hf_downloads_001",
        natural_query="most downloaded models on huggingface",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:downloads ?downloads .
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(CONTAINS(LCASE(STR(?source)), "huggingface") && ?downloads > 0)
}
ORDER BY DESC(?downloads)
LIMIT 15""",
        complexity="intermediate",
        category="source_downloads",
        keywords=["huggingface", "most downloaded", "popular", "top", "downloads", "hf"],
        explanation="Top HuggingFace models by download count"
    ),
    
    SPARQLExample(
        id="hf_downloads_002",
        natural_query="top downloaded huggingface models by task",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:downloads ?downloads .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(CONTAINS(LCASE(STR(?source)), "huggingface") && ?downloads > 1000)
}
ORDER BY DESC(?downloads)
LIMIT 15""",
        complexity="intermediate",
        category="source_downloads_task",
        keywords=["huggingface", "downloads", "task", "popular", "threshold"],
        explanation="HuggingFace models with high downloads, showing task categories"
    ),
    
    SPARQLExample(
        id="hf_downloads_003",
        natural_query="huggingface models sorted by downloads",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:downloads ?downloads .
  OPTIONAL { ?model daimo:library ?library }
  FILTER(CONTAINS(LCASE(STR(?source)), "huggingface") && BOUND(?downloads))
}
ORDER BY DESC(?downloads)
LIMIT 20""",
        complexity="intermediate",
        category="source_downloads_library",
        keywords=["huggingface", "downloads", "library", "framework", "sorted", "ranked"],
        explanation="HuggingFace models with library/framework information, sorted by downloads"
    ),
    
    SPARQLExample(
        id="hf_downloads_004",
        natural_query="average downloads per task on huggingface",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?task (COUNT(?model) as ?count) (AVG(?downloads) as ?avgDownloads) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:task ?task ;
         daimo:downloads ?downloads .
  FILTER(CONTAINS(LCASE(STR(?source)), "huggingface"))
}
GROUP BY ?task
ORDER BY DESC(?avgDownloads)
LIMIT 15""",
        complexity="advanced",
        category="source_aggregation",
        keywords=["huggingface", "average", "aggregation", "by task", "statistics", "group by"],
        explanation="Statistical aggregation of HuggingFace downloads grouped by task"
    ),
    
    # === NUEVOS EJEMPLOS: COMPUTER VISION MULTI-REPO ===
    SPARQLExample(
        id="cv_all_001",
        natural_query="computer vision models from all repositories",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(!BOUND(?task) || 
         CONTAINS(LCASE(?task), "vision") || 
         CONTAINS(LCASE(?task), "image") ||
         CONTAINS(LCASE(?task), "object-detection") ||
         CONTAINS(LCASE(?task), "segmentation"))
}
LIMIT 20""",
        complexity="intermediate",
        category="task_all_sources",
        keywords=["computer vision", "vision", "image", "all repositories", "cv", "multi-source"],
        explanation="Computer vision models across all available repositories"
    ),
    
    SPARQLExample(
        id="cv_all_002",
        natural_query="computer vision models count by repository",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "vision") || 
         CONTAINS(LCASE(?task), "image") ||
         CONTAINS(LCASE(?task), "detection"))
}
GROUP BY ?source
ORDER BY DESC(?count)""",
        complexity="advanced",
        category="task_source_aggregation",
        keywords=["computer vision", "by repository", "count", "aggregation", "distribution"],
        explanation="Distribution of CV models across repositories"
    ),
    
    SPARQLExample(
        id="cv_all_003",
        natural_query="top computer vision models by engagement",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:task ?task }
  FILTER(!BOUND(?task) || CONTAINS(LCASE(?task), "vision") || CONTAINS(LCASE(?task), "image"))
  FILTER(BOUND(?downloads) || BOUND(?likes))
}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 15""",
        complexity="intermediate",
        category="task_engagement",
        keywords=["computer vision", "engagement", "popular", "downloads", "likes", "top"],
        explanation="Most popular CV models ranked by user engagement"
    ),
    
    SPARQLExample(
        id="cv_all_004",
        natural_query="models with vision or image in title",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:library ?library }
  FILTER(CONTAINS(LCASE(?title), "vision") || 
         CONTAINS(LCASE(?title), "image") ||
         CONTAINS(LCASE(?title), "cv") ||
         CONTAINS(LCASE(?title), "yolo") ||
         CONTAINS(LCASE(?title), "resnet"))
}
LIMIT 20""",
        complexity="intermediate",
        category="title_based_task",
        keywords=["computer vision", "title", "image", "detection", "yolo", "resnet", "cv"],
        explanation="Title-based search for computer vision models"
    ),
    
    # === NUEVOS EJEMPLOS: HIGH RATED PER REPOSITORY ===
    SPARQLExample(
        id="high_rated_001",
        natural_query="high rated models by repository",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:likes ?likes .
  FILTER(?likes > 10)
}
ORDER BY ?source DESC(?likes)
LIMIT 20""",
        complexity="intermediate",
        category="rating_per_source",
        keywords=["high rated", "likes", "repository", "popular", "top", "by source"],
        explanation="High-rated models organized by repository"
    ),
    
    SPARQLExample(
        id="high_rated_002",
        natural_query="average rating per repository",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (AVG(?likes) as ?avgLikes) (MAX(?likes) as ?maxLikes) (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:likes ?likes .
  FILTER(?likes > 0)
}
GROUP BY ?source
ORDER BY DESC(?avgLikes)""",
        complexity="advanced",
        category="rating_aggregation",
        keywords=["average", "rating", "by repository", "aggregation", "statistics", "likes"],
        explanation="Statistical analysis of model ratings per repository"
    ),
    
    SPARQLExample(
        id="high_rated_003",
        natural_query="top 5 models per repository by likes",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?likes ?downloads WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:likes ?likes .
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(?likes > 5)
}
ORDER BY ?source DESC(?likes)
LIMIT 25""",
        complexity="intermediate",
        category="top_per_source",
        keywords=["top", "per repository", "likes", "best", "each source", "top-n"],
        explanation="Top-rated models from each repository"
    ),
    
    SPARQLExample(
        id="high_rated_004",
        natural_query="high rated huggingface models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?likes ?downloads WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:likes ?likes .
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(CONTAINS(LCASE(STR(?source)), "huggingface") && ?likes > 50)
}
ORDER BY DESC(?likes)
LIMIT 15""",
        complexity="intermediate",
        category="source_high_rating",
        keywords=["high rated", "huggingface", "likes", "quality", "top", "hf"],
        explanation="High-quality HuggingFace models with significant user approval"
    ),
    
    # === NUEVOS EJEMPLOS: TEXT-TO-IMAGE / IMAGE-TO-TEXT ===
    SPARQLExample(
        id="text_image_001",
        natural_query="text to image models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(!BOUND(?task) || 
         CONTAINS(LCASE(?task), "text-to-image") ||
         CONTAINS(LCASE(?task), "image-generation") ||
         CONTAINS(LCASE(?title), "stable diffusion") ||
         CONTAINS(LCASE(?title), "dall") ||
         CONTAINS(LCASE(?title), "midjourney"))
}
LIMIT 20""",
        complexity="intermediate",
        category="text_to_image",
        keywords=["text to image", "generation", "diffusion", "dall-e", "stable diffusion", "t2i"],
        explanation="Text-to-image generation models including diffusion models"
    ),
    
    SPARQLExample(
        id="text_image_002",
        natural_query="image to text models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(!BOUND(?task) || 
         CONTAINS(LCASE(?task), "image-to-text") ||
         CONTAINS(LCASE(?task), "image-caption") ||
         CONTAINS(LCASE(?task), "visual-question") ||
         CONTAINS(LCASE(?title), "clip") ||
         CONTAINS(LCASE(?title), "blip"))
}
LIMIT 20""",
        complexity="intermediate",
        category="image_to_text",
        keywords=["image to text", "caption", "visual", "clip", "blip", "i2t", "vqa"],
        explanation="Image-to-text models including captioning and visual QA"
    ),
    
    SPARQLExample(
        id="text_image_003",
        natural_query="multimodal text and image models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(CONTAINS(LCASE(?title), "multimodal") ||
         CONTAINS(LCASE(?title), "vision-language") ||
         CONTAINS(LCASE(?title), "vl-") ||
         CONTAINS(LCASE(?task), "multimodal"))
}
LIMIT 15""",
        complexity="intermediate",
        category="multimodal",
        keywords=["multimodal", "vision-language", "vl", "text-image", "cross-modal"],
        explanation="Multimodal models handling both text and vision"
    ),
    
    SPARQLExample(
        id="text_image_004",
        natural_query="popular text to image generation models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?downloads ?runCount WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:runCount ?runCount }
  OPTIONAL { ?model daimo:task ?task }
  FILTER(CONTAINS(LCASE(?title), "stable") ||
         CONTAINS(LCASE(?title), "diffusion") ||
         CONTAINS(LCASE(?title), "dall") ||
         CONTAINS(LCASE(?task), "text-to-image"))
  FILTER(BOUND(?downloads) || BOUND(?runCount))
}
ORDER BY DESC(?downloads) DESC(?runCount)
LIMIT 15""",
        complexity="intermediate",
        category="generation_popular",
        keywords=["text to image", "popular", "generation", "stable diffusion", "downloads", "trending"],
        explanation="Most popular text-to-image generation models by usage"
    ),
    
    # === NUEVOS EJEMPLOS: NLP COMPREHENSIVE ===
    SPARQLExample(
        id="nlp_models_001",
        natural_query="natural language processing models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(!BOUND(?task) ||
         CONTAINS(LCASE(?task), "nlp") ||
         CONTAINS(LCASE(?task), "text") ||
         CONTAINS(LCASE(?task), "language") ||
         CONTAINS(LCASE(?task), "translation") ||
         CONTAINS(LCASE(?task), "sentiment"))
}
LIMIT 20""",
        complexity="intermediate",
        category="nlp_general",
        keywords=["nlp", "natural language", "text", "language processing", "text processing"],
        explanation="Comprehensive NLP models across all text-related tasks"
    ),
    
    SPARQLExample(
        id="nlp_models_002",
        natural_query="nlp models by specific task",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?task (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "text") ||
         CONTAINS(LCASE(?task), "language") ||
         CONTAINS(LCASE(?task), "translation") ||
         CONTAINS(LCASE(?task), "sentiment") ||
         CONTAINS(LCASE(?task), "question-answering"))
}
GROUP BY ?task
ORDER BY DESC(?count)
LIMIT 20""",
        complexity="advanced",
        category="nlp_task_breakdown",
        keywords=["nlp", "by task", "breakdown", "text tasks", "aggregation", "distribution"],
        explanation="Distribution of NLP models by specific task categories"
    ),
    
    SPARQLExample(
        id="nlp_models_003",
        natural_query="transformer models for nlp",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:library ?library }
  OPTIONAL { ?model daimo:task ?task }
  FILTER(CONTAINS(LCASE(?library), "transformers") ||
         CONTAINS(LCASE(?title), "bert") ||
         CONTAINS(LCASE(?title), "gpt") ||
         CONTAINS(LCASE(?title), "t5") ||
         CONTAINS(LCASE(?title), "roberta"))
}
LIMIT 20""",
        complexity="intermediate",
        category="nlp_transformers",
        keywords=["transformers", "bert", "gpt", "nlp", "language models", "t5", "roberta"],
        explanation="Transformer-based NLP models (BERT, GPT family)"
    ),
    
    SPARQLExample(
        id="nlp_models_004",
        natural_query="most popular nlp models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:task ?task }
  FILTER(!BOUND(?task) ||
         CONTAINS(LCASE(?task), "nlp") ||
         CONTAINS(LCASE(?task), "text") ||
         CONTAINS(LCASE(?title), "bert") ||
         CONTAINS(LCASE(?title), "gpt"))
  FILTER(BOUND(?downloads) || BOUND(?likes))
}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 20""",
        complexity="intermediate",
        category="nlp_popular",
        keywords=["nlp", "popular", "most downloaded", "text", "language", "trending"],
        explanation="Most popular NLP models by downloads and engagement"
    ),

    # ============================================================================

    # ============================================================================
    # NUEVOS 49 QUERIES COMPLEJOS (Advanced/Intermediate)
    # ============================================================================

    SPARQLExample(
        id="complex_repo_001",
        natural_query="top models per repository with multiple metrics",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source ?title (MAX(?downloads) as ?maxDownloads) (MAX(?likes) as ?maxLikes) WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(BOUND(?downloads) || BOUND(?likes))
}
GROUP BY ?source ?title
ORDER BY ?source DESC(?maxDownloads)
LIMIT 25""",
        complexity="advanced",
        category="multi_repo_top_metrics",
        keywords=['multi-repository', 'top', 'downloads', 'likes', 'comparison'],
        explanation="Top models per repository with multiple metrics"
    ),
    SPARQLExample(
        id="complex_repo_002",
        natural_query="repositories with most diverse tasks",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (COUNT(DISTINCT ?task) as ?taskVariety) (COUNT(?model) as ?totalModels) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:task ?task .
}
GROUP BY ?source
HAVING(COUNT(DISTINCT ?task) > 2)
ORDER BY DESC(?taskVariety)
LIMIT 15""",
        complexity="advanced",
        category="multi_repo_task_diversity",
        keywords=['diversity', 'variety', 'tasks', 'by repository', 'distinct'],
        explanation="Repositories with most diverse tasks"
    ),
    SPARQLExample(
        id="complex_repo_003",
        natural_query="compare pytorch hub and tensorflow hub models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (COUNT(?model) as ?count) (AVG(?likes) as ?avgLikes) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(CONTAINS(LCASE(STR(?source)), "pytorch") || CONTAINS(LCASE(STR(?source)), "tensorflow"))
}
GROUP BY ?source
ORDER BY DESC(?count)""",
        complexity="advanced",
        category="multi_repo_hub_comparison",
        keywords=['pytorch', 'tensorflow', 'hub', 'comparison', 'framework'],
        explanation="Compare pytorch hub and tensorflow hub models"
    ),
    SPARQLExample(
        id="complex_repo_004",
        natural_query="compare huggingface metrics with other repositories",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (AVG(?downloads) as ?avgDl) (AVG(?likes) as ?avgLikes) (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(BOUND(?downloads) || BOUND(?likes))
}
GROUP BY ?source
ORDER BY DESC(?avgDl)
LIMIT 10""",
        complexity="advanced",
        category="multi_repo_metrics_comparison",
        keywords=['comparison', 'huggingface', 'metrics', 'average', 'repositories'],
        explanation="Compare huggingface metrics with other repositories"
    ),
    SPARQLExample(
        id="complex_repo_005",
        natural_query="nlp models count by repository",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (COUNT(?model) as ?nlpCount) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(!BOUND(?task) || CONTAINS(LCASE(?task), "nlp") || CONTAINS(LCASE(?task), "text") || CONTAINS(LCASE(?task), "language"))
}
GROUP BY ?source
ORDER BY DESC(?nlpCount)
LIMIT 10""",
        complexity="advanced",
        category="multi_repo_nlp_distribution",
        keywords=['nlp', 'by repository', 'distribution', 'count', 'text'],
        explanation="Nlp models count by repository"
    ),
    SPARQLExample(
        id="complex_repo_006",
        natural_query="repositories with computer vision vs nlp models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source 
       (COUNT(?cvModel) as ?cvCount) 
       (COUNT(?nlpModel) as ?nlpCount)
WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source .
  OPTIONAL { 
    ?model daimo:task ?task .
    BIND(IF(CONTAINS(LCASE(?task), "vision") || CONTAINS(LCASE(?task), "image"), ?model, ?unbound) as ?cvModel)
    BIND(IF(CONTAINS(LCASE(?task), "nlp") || CONTAINS(LCASE(?task), "text"), ?model, ?unbound) as ?nlpModel)
  }
}
GROUP BY ?source
ORDER BY DESC(?cvCount)
LIMIT 10""",
        complexity="advanced",
        category="multi_repo_cv_nlp_split",
        keywords=['cv', 'nlp', 'split', 'comparison', 'by repository'],
        explanation="Repositories with computer vision vs nlp models"
    ),
    SPARQLExample(
        id="complex_repo_007",
        natural_query="repositories ranked by total engagement",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (SUM(?downloads) as ?totalDownloads) (SUM(?likes) as ?totalLikes) (COUNT(?model) as ?modelCount) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
}
GROUP BY ?source
ORDER BY DESC(?totalDownloads) DESC(?totalLikes)
LIMIT 10""",
        complexity="advanced",
        category="multi_repo_engagement_ranking",
        keywords=['ranking', 'engagement', 'total', 'by repository', 'sum'],
        explanation="Repositories ranked by total engagement"
    ),
    SPARQLExample(
        id="complex_agg_001",
        natural_query="average metrics by task and library combination",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?task ?library (AVG(?downloads) as ?avgDownloads) (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         daimo:task ?task ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:downloads ?downloads }
}
GROUP BY ?task ?library
HAVING(COUNT(?model) > 1)
ORDER BY ?task DESC(?avgDownloads)
LIMIT 25""",
        complexity="advanced",
        category="agg_task_library_metrics",
        keywords=['task', 'library', 'average', 'multi-dimensional', 'combination'],
        explanation="Average metrics by task and library combination"
    ),
    SPARQLExample(
        id="complex_agg_002",
        natural_query="models per source and task with download ranges",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source ?task (MIN(?downloads) as ?minDl) (MAX(?downloads) as ?maxDl) (AVG(?downloads) as ?avgDl) (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:task ?task ;
         daimo:downloads ?downloads .
  FILTER(?downloads > 0)
}
GROUP BY ?source ?task
HAVING(COUNT(?model) > 1)
ORDER BY DESC(?avgDl)
LIMIT 20""",
        complexity="advanced",
        category="agg_source_task_ranges",
        keywords=['source', 'task', 'ranges', 'min', 'max', 'percentiles'],
        explanation="Models per source and task with download ranges"
    ),
    SPARQLExample(
        id="complex_agg_003",
        natural_query="libraries ranked by downloads to likes ratio",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?library (SUM(?downloads) as ?totalDl) (SUM(?likes) as ?totalLikes) (SUM(?downloads)/SUM(?likes) as ?ratio) WHERE {
  ?model a daimo:Model ;
         daimo:library ?library ;
         daimo:downloads ?downloads ;
         daimo:likes ?likes .
  FILTER(?downloads > 0 && ?likes > 0)
}
GROUP BY ?library
HAVING(SUM(?likes) > 50)
ORDER BY DESC(?ratio)
LIMIT 15""",
        complexity="advanced",
        category="agg_library_ratio",
        keywords=['library', 'ratio', 'downloads', 'likes', 'efficiency'],
        explanation="Libraries ranked by downloads to likes ratio"
    ),
    SPARQLExample(
        id="complex_agg_004",
        natural_query="most popular task per repository",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source ?task (COUNT(?model) as ?count) (AVG(?likes) as ?avgPop) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:task ?task .
  OPTIONAL { ?model daimo:likes ?likes }
}
GROUP BY ?source ?task
ORDER BY ?source DESC(?count)
LIMIT 30""",
        complexity="advanced",
        category="agg_task_popularity_per_source",
        keywords=['task', 'popularity', 'per source', 'most popular', 'ranking'],
        explanation="Most popular task per repository"
    ),
    SPARQLExample(
        id="complex_agg_005",
        natural_query="task coverage by library framework",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?library (COUNT(DISTINCT ?task) as ?taskCoverage) (COUNT(?model) as ?totalModels) WHERE {
  ?model a daimo:Model ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:task ?task }
}
GROUP BY ?library
HAVING(COUNT(?model) > 3)
ORDER BY DESC(?taskCoverage)
LIMIT 15""",
        complexity="advanced",
        category="agg_task_coverage_library",
        keywords=['coverage', 'tasks', 'library', 'diversity', 'distinct'],
        explanation="Task coverage by library framework"
    ),
    SPARQLExample(
        id="complex_agg_006",
        natural_query="tasks ranked by total engagement score",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?task 
       (SUM(COALESCE(?downloads, 0)) as ?totalDownloads) 
       (SUM(COALESCE(?likes, 0)) as ?totalLikes)
       (SUM(COALESCE(?downloads, 0) + COALESCE(?likes, 0)) as ?engagement)
WHERE {
  ?model a daimo:Model ;
         daimo:task ?task .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
}
GROUP BY ?task
ORDER BY DESC(?engagement)
LIMIT 15""",
        complexity="advanced",
        category="agg_task_engagement_score",
        keywords=['engagement', 'score', 'by task', 'total', 'ranking'],
        explanation="Tasks ranked by total engagement score"
    ),
    SPARQLExample(
        id="complex_agg_007",
        natural_query="tasks with high average downloads and many models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?task (AVG(?downloads) as ?avgDownloads) (COUNT(?model) as ?modelCount) WHERE {
  ?model a daimo:Model ;
         daimo:task ?task ;
         daimo:downloads ?downloads .
  FILTER(?downloads > 500)
}
GROUP BY ?task
HAVING(COUNT(?model) > 3 && AVG(?downloads) > 5000)
ORDER BY DESC(?avgDownloads)
LIMIT 15""",
        complexity="advanced",
        category="agg_threshold_multi_condition",
        keywords=['threshold', 'average', 'having', 'multi-condition', 'high'],
        explanation="Tasks with high average downloads and many models"
    ),
    SPARQLExample(
        id="complex_filter_001",
        natural_query="huggingface transformers models with high engagement",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(
    CONTAINS(LCASE(STR(?source)), "huggingface") &&
    CONTAINS(LCASE(?library), "transformers") &&
    (BOUND(?downloads) || BOUND(?likes))
  )
}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 20""",
        complexity="advanced",
        category="filter_multi_hf_transformers",
        keywords=['huggingface', 'transformers', 'engagement', 'popular', 'metrics'],
        explanation="Huggingface transformers models with high engagement"
    ),
    SPARQLExample(
        id="complex_filter_002",
        natural_query="highly downloaded transformer nlp models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library ?downloads WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library ;
         daimo:downloads ?downloads .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(
    CONTAINS(LCASE(?library), "transformers") &&
    (!BOUND(?task) || CONTAINS(LCASE(?task), "nlp") || CONTAINS(LCASE(?task), "text")) &&
    ?downloads > 10000
  )
}
ORDER BY DESC(?downloads)
LIMIT 15""",
        complexity="advanced",
        category="filter_transformers_nlp_popular",
        keywords=['transformers', 'nlp', 'high downloads', 'text', 'popular'],
        explanation="Highly downloaded transformer nlp models"
    ),
    SPARQLExample(
        id="complex_filter_003",
        natural_query="most run models on replicate",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?runCount WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:runCount ?runCount .
  FILTER(
    CONTAINS(LCASE(STR(?source)), "replicate") &&
    ?runCount > 100
  )
}
ORDER BY DESC(?runCount)
LIMIT 20""",
        complexity="intermediate",
        category="filter_replicate_runs",
        keywords=['replicate', 'runs', 'popular', 'most used', 'active'],
        explanation="Most run models on replicate"
    ),
    SPARQLExample(
        id="complex_filter_004",
        natural_query="classification models from multiple sources with specific library",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:task ?task ;
         daimo:library ?library .
  FILTER(
    (CONTAINS(LCASE(STR(?source)), "huggingface") || CONTAINS(LCASE(STR(?source)), "pytorch")) &&
    CONTAINS(LCASE(?task), "classification") &&
    (CONTAINS(LCASE(?library), "pytorch") || CONTAINS(LCASE(?library), "transformers"))
  )
}
LIMIT 20""",
        complexity="advanced",
        category="filter_multi_classification_library",
        keywords=['classification', 'multi-source', 'library', 'specific', 'pytorch'],
        explanation="Classification models from multiple sources with specific library"
    ),
    SPARQLExample(
        id="complex_filter_005",
        natural_query="models with task library and multiple engagement metrics",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task ?library ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task ;
         daimo:library ?library ;
         daimo:downloads ?downloads ;
         daimo:likes ?likes .
  FILTER(?downloads > 1000 && ?likes > 10)
}
ORDER BY DESC(?downloads)
LIMIT 20""",
        complexity="intermediate",
        category="filter_complete_with_metrics",
        keywords=['complete', 'task', 'library', 'metrics', 'engagement'],
        explanation="Models with task library and multiple engagement metrics"
    ),
    SPARQLExample(
        id="complex_filter_006",
        natural_query="speech models with transformers or pytorch library",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(
    (CONTAINS(LCASE(?library), "transformers") || CONTAINS(LCASE(?library), "pytorch")) &&
    (!BOUND(?task) || CONTAINS(LCASE(?task), "speech") || CONTAINS(LCASE(?task), "audio") || CONTAINS(LCASE(?title), "whisper"))
  )
}
LIMIT 20""",
        complexity="advanced",
        category="filter_speech_frameworks",
        keywords=['speech', 'audio', 'transformers', 'pytorch', 'whisper'],
        explanation="Speech models with transformers or pytorch library"
    ),
    SPARQLExample(
        id="complex_filter_007",
        natural_query="high quality embedding models with metrics",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(
    (!BOUND(?task) || CONTAINS(LCASE(?task), "embedding") || CONTAINS(LCASE(?task), "sentence-similarity") || CONTAINS(LCASE(?title), "embed")) &&
    ((BOUND(?downloads) && ?downloads > 5000) || (BOUND(?likes) && ?likes > 30))
  )
}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 15""",
        complexity="advanced",
        category="filter_embeddings_quality",
        keywords=['embeddings', 'high quality', 'sentence', 'similarity', 'popular'],
        explanation="High quality embedding models with metrics"
    ),
    SPARQLExample(
        id="complex_trend_001",
        natural_query="top ten percent models by downloads",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:downloads ?downloads .
  FILTER(?downloads > 50000)
}
ORDER BY DESC(?downloads)
LIMIT 20""",
        complexity="intermediate",
        category="trend_top_percentile",
        keywords=['top', 'percentile', 'downloads', 'trending', 'popular'],
        explanation="Top ten percent models by downloads"
    ),
    SPARQLExample(
        id="complex_trend_002",
        natural_query="trending models with high recent engagement",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source (?downloads + ?likes * 10 + COALESCE(?runCount, 0) * 5 as ?trendScore) WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:runCount ?runCount }
  FILTER(BOUND(?downloads) || BOUND(?likes))
}
ORDER BY DESC(?trendScore)
LIMIT 20""",
        complexity="advanced",
        category="trend_engagement_score",
        keywords=['trending', 'engagement', 'score', 'recent', 'popular'],
        explanation="Trending models with high recent engagement"
    ),
    SPARQLExample(
        id="complex_trend_003",
        natural_query="emerging tasks with multiple models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?task (COUNT(?model) as ?count) (AVG(?downloads) as ?avgPop) WHERE {
  ?model a daimo:Model ;
         daimo:task ?task .
  OPTIONAL { ?model daimo:downloads ?downloads }
}
GROUP BY ?task
HAVING(COUNT(?model) >= 5)
ORDER BY DESC(?count) DESC(?avgPop)
LIMIT 15""",
        complexity="advanced",
        category="trend_emerging_tasks",
        keywords=['emerging', 'tasks', 'new', 'growing', 'multiple models'],
        explanation="Emerging tasks with multiple models"
    ),
    SPARQLExample(
        id="complex_trend_004",
        natural_query="growing libraries by model count and popularity",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?library (COUNT(?model) as ?modelCount) (SUM(?likes) as ?totalLikes) WHERE {
  ?model a daimo:Model ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:likes ?likes }
}
GROUP BY ?library
HAVING(COUNT(?model) > 3)
ORDER BY DESC(?totalLikes) DESC(?modelCount)
LIMIT 15""",
        complexity="advanced",
        category="trend_growing_libraries",
        keywords=['growing', 'libraries', 'adoption', 'trending', 'frameworks'],
        explanation="Growing libraries by model count and popularity"
    ),
    SPARQLExample(
        id="complex_trend_005",
        natural_query="viral models with high likes to downloads ratio",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes (?likes * 100 / ?downloads as ?viralScore) WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:downloads ?downloads ;
         daimo:likes ?likes .
  FILTER(?downloads > 100 && ?likes > 10)
}
ORDER BY DESC(?viralScore)
LIMIT 20""",
        complexity="advanced",
        category="trend_viral_models",
        keywords=['viral', 'ratio', 'likes', 'trending', 'popular'],
        explanation="Viral models with high likes to downloads ratio"
    ),
    SPARQLExample(
        id="complex_trend_006",
        natural_query="most active repositories by model count",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (COUNT(?model) as ?modelCount) (SUM(?downloads) as ?totalActivity) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:downloads ?downloads }
}
GROUP BY ?source
ORDER BY DESC(?modelCount) DESC(?totalActivity)
LIMIT 10""",
        complexity="advanced",
        category="trend_active_repositories",
        keywords=['active', 'repositories', 'model count', 'activity', 'growing'],
        explanation="Most active repositories by model count"
    ),
    SPARQLExample(
        id="complex_trend_007",
        natural_query="underrated models with high downloads but low likes",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:downloads ?downloads ;
         daimo:likes ?likes .
  FILTER(?downloads > 10000 && ?likes < 50)
}
ORDER BY DESC(?downloads)
LIMIT 20""",
        complexity="intermediate",
        category="trend_underrated",
        keywords=['underrated', 'hidden gems', 'downloads', 'low likes', 'overlooked'],
        explanation="Underrated models with high downloads but low likes"
    ),
    SPARQLExample(
        id="complex_spec_001",
        natural_query="large language models ranked by popularity",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(
    CONTAINS(LCASE(?title), "gpt") ||
    CONTAINS(LCASE(?title), "llama") ||
    CONTAINS(LCASE(?title), "mistral") ||
    CONTAINS(LCASE(?title), "gemma") ||
    CONTAINS(LCASE(?title), "llm")
  )
}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 20""",
        complexity="intermediate",
        category="spec_llm_popular",
        keywords=['llm', 'large language model', 'gpt', 'llama', 'popular'],
        explanation="Large language models ranked by popularity"
    ),
    SPARQLExample(
        id="complex_spec_002",
        natural_query="object detection models across repositories",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(
    (!BOUND(?task) || CONTAINS(LCASE(?task), "object-detection") || CONTAINS(LCASE(?task), "detection")) ||
    CONTAINS(LCASE(?title), "yolo") ||
    CONTAINS(LCASE(?title), "detection") ||
    CONTAINS(LCASE(?title), "rcnn")
  )
}
LIMIT 20""",
        complexity="intermediate",
        category="spec_object_detection",
        keywords=['object detection', 'yolo', 'detection', 'cv', 'computer vision'],
        explanation="Object detection models across repositories"
    ),
    SPARQLExample(
        id="complex_spec_003",
        natural_query="advanced multimodal models with metrics",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?downloads WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(
    (!BOUND(?task) || CONTAINS(LCASE(?task), "multimodal")) ||
    CONTAINS(LCASE(?title), "clip") ||
    CONTAINS(LCASE(?title), "blip") ||
    CONTAINS(LCASE(?title), "vision-language") ||
    CONTAINS(LCASE(?title), "flamingo")
  )
}
ORDER BY DESC(?downloads)
LIMIT 15""",
        complexity="intermediate",
        category="spec_multimodal_advanced",
        keywords=['multimodal', 'clip', 'blip', 'vision-language', 'cross-modal'],
        explanation="Advanced multimodal models with metrics"
    ),
    SPARQLExample(
        id="complex_spec_004",
        natural_query="machine translation models by popularity",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:downloads ?downloads }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(
    (!BOUND(?task) || CONTAINS(LCASE(?task), "translation")) ||
    CONTAINS(LCASE(?title), "translation") ||
    CONTAINS(LCASE(?title), "mt5") ||
    CONTAINS(LCASE(?title), "opus")
  )
}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 15""",
        complexity="intermediate",
        category="spec_translation",
        keywords=['translation', 'machine translation', 'mt', 'multilingual', 'opus'],
        explanation="Machine translation models by popularity"
    ),
    SPARQLExample(
        id="complex_spec_005",
        natural_query="semantic segmentation models with high engagement",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(
    (!BOUND(?task) || CONTAINS(LCASE(?task), "segmentation") || CONTAINS(LCASE(?task), "semantic-segmentation")) ||
    CONTAINS(LCASE(?title), "segment") ||
    CONTAINS(LCASE(?title), "sam") ||
    CONTAINS(LCASE(?title), "unet")
  )
}
ORDER BY DESC(?likes)
LIMIT 20""",
        complexity="intermediate",
        category="spec_segmentation_semantic",
        keywords=['segmentation', 'semantic', 'sam', 'unet', 'cv'],
        explanation="Semantic segmentation models with high engagement"
    ),
    SPARQLExample(
        id="complex_spec_006",
        natural_query="sentiment analysis models from multiple sources",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(
    (!BOUND(?task) || CONTAINS(LCASE(?task), "sentiment")) ||
    CONTAINS(LCASE(?title), "sentiment") ||
    CONTAINS(LCASE(?title), "emotion")
  )
}
LIMIT 20""",
        complexity="intermediate",
        category="spec_sentiment_analysis",
        keywords=['sentiment', 'analysis', 'emotion', 'nlp', 'text classification'],
        explanation="Sentiment analysis models from multiple sources"
    ),
    SPARQLExample(
        id="complex_spec_007",
        natural_query="image super resolution models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  OPTIONAL { ?model daimo:task ?task }
  FILTER(
    (!BOUND(?task) || CONTAINS(LCASE(?task), "super-resolution") || CONTAINS(LCASE(?task), "upscaling")) ||
    CONTAINS(LCASE(?title), "super") ||
    CONTAINS(LCASE(?title), "upscale") ||
    CONTAINS(LCASE(?title), "sr") ||
    CONTAINS(LCASE(?title), "esrgan")
  )
}
LIMIT 15""",
        complexity="intermediate",
        category="spec_super_resolution",
        keywords=['super resolution', 'upscaling', 'image enhancement', 'sr', 'esrgan'],
        explanation="Image super resolution models"
    ),
    SPARQLExample(
        id="complex_comp_001",
        natural_query="tasks with most model alternatives",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?task (COUNT(DISTINCT ?title) as ?uniqueModels) (COUNT(?model) as ?total) WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
}
GROUP BY ?task
HAVING(COUNT(?model) > 3)
ORDER BY DESC(?uniqueModels)
LIMIT 15""",
        complexity="advanced",
        category="comp_model_density_by_task",
        keywords=['alternatives', 'density', 'task', 'options', 'variety'],
        explanation="Tasks with most model alternatives"
    ),
    SPARQLExample(
        id="complex_comp_002",
        natural_query="similar models by library and task combination",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?library ?task (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         daimo:library ?library ;
         daimo:task ?task .
}
GROUP BY ?library ?task
HAVING(COUNT(?model) > 2)
ORDER BY DESC(?count)
LIMIT 20""",
        complexity="advanced",
        category="comp_similar_library_task",
        keywords=['similar', 'library', 'task', 'grouping', 'alternatives'],
        explanation="Similar models by library and task combination"
    ),
    SPARQLExample(
        id="complex_comp_003",
        natural_query="compare frameworks for specific task",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?task ?library (COUNT(?model) as ?count) (AVG(?downloads) as ?avgPop) WHERE {
  ?model a daimo:Model ;
         daimo:task ?task ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:downloads ?downloads }
}
GROUP BY ?task ?library
HAVING(COUNT(?model) > 1)
ORDER BY ?task DESC(?count)
LIMIT 30""",
        complexity="advanced",
        category="comp_framework_by_task",
        keywords=['comparison', 'framework', 'by task', 'alternatives', 'library'],
        explanation="Compare frameworks for specific task"
    ),
    SPARQLExample(
        id="complex_comp_004",
        natural_query="compare light vs large model variants",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?title ?downloads 
       (IF(CONTAINS(LCASE(?title), "mini") || CONTAINS(LCASE(?title), "small") || CONTAINS(LCASE(?title), "tiny"), "light", "heavy") as ?variant)
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(
    CONTAINS(LCASE(?title), "mini") ||
    CONTAINS(LCASE(?title), "small") ||
    CONTAINS(LCASE(?title), "tiny") ||
    CONTAINS(LCASE(?title), "large") ||
    CONTAINS(LCASE(?title), "-xl")
  )
}
ORDER BY ?variant DESC(?downloads)
LIMIT 25""",
        complexity="advanced",
        category="comp_light_vs_heavy",
        keywords=['light', 'heavy', 'mini', 'large', 'size comparison'],
        explanation="Compare light vs large model variants"
    ),
    SPARQLExample(
        id="complex_comp_005",
        natural_query="compare base and finetuned model variants",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?title 
       (IF(CONTAINS(LCASE(?title), "base"), "base", "finetuned") as ?variant)
       ?downloads
WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(
    CONTAINS(LCASE(?title), "base") ||
    CONTAINS(LCASE(?title), "fine") ||
    CONTAINS(LCASE(?title), "-ft")
  )
}
ORDER BY ?variant DESC(?downloads)
LIMIT 20""",
        complexity="intermediate",
        category="comp_base_vs_finetuned",
        keywords=['base', 'finetuned', 'variants', 'comparison', 'versions'],
        explanation="Compare base and finetuned model variants"
    ),
    SPARQLExample(
        id="complex_comp_006",
        natural_query="model families with multiple variants",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?title ?downloads WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  OPTIONAL { ?model daimo:downloads ?downloads }
  FILTER(
    CONTAINS(?title, "bert") ||
    CONTAINS(?title, "gpt") ||
    CONTAINS(?title, "llama") ||
    CONTAINS(?title, "stable-diffusion") ||
    CONTAINS(?title, "clip")
  )
}
ORDER BY DESC(?downloads)
LIMIT 20""",
        complexity="intermediate",
        category="comp_model_families",
        keywords=['families', 'variants', 'series', 'related', 'versions'],
        explanation="Model families with multiple variants"
    ),
    SPARQLExample(
        id="complex_comp_007",
        natural_query="open source alternatives by task",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?task (COUNT(?model) as ?alternatives) (AVG(?likes) as ?avgRating) WHERE {
  ?model a daimo:Model ;
         daimo:task ?task .
  OPTIONAL { ?model daimo:likes ?likes }
  FILTER(BOUND(?task))
}
GROUP BY ?task
HAVING(COUNT(?model) > 3)
ORDER BY DESC(?alternatives)
LIMIT 15""",
        complexity="advanced",
        category="comp_opensource_alternatives",
        keywords=['open source', 'alternatives', 'by task', 'options', 'free'],
        explanation="Open source alternatives by task"
    ),
    SPARQLExample(
        id="complex_perf_001",
        natural_query="most efficient models by engagement ratio",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (SUM(?downloads)/COUNT(?model) as ?efficiency) (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:downloads ?downloads .
  FILTER(?downloads > 0)
}
GROUP BY ?source
HAVING(COUNT(?model) > 3)
ORDER BY DESC(?efficiency)
LIMIT 10""",
        complexity="advanced",
        category="perf_efficiency_ratio",
        keywords=['efficiency', 'ratio', 'performance', 'optimized', 'best'],
        explanation="Most efficient models by engagement ratio"
    ),
    SPARQLExample(
        id="complex_perf_002",
        natural_query="libraries with best adoption rate",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?library (COUNT(?model) as ?modelCount) (AVG(?likes) as ?avgLikes) (AVG(?downloads) as ?avgDownloads) WHERE {
  ?model a daimo:Model ;
         daimo:library ?library .
  OPTIONAL { ?model daimo:likes ?likes }
  OPTIONAL { ?model daimo:downloads ?downloads }
}
GROUP BY ?library
HAVING(COUNT(?model) > 5)
ORDER BY DESC(?avgLikes) DESC(?avgDownloads)
LIMIT 15""",
        complexity="advanced",
        category="perf_adoption_rate",
        keywords=['adoption', 'rate', 'library', 'popular', 'growing'],
        explanation="Libraries with best adoption rate"
    ),
    SPARQLExample(
        id="complex_perf_003",
        natural_query="tasks with best engagement per model",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT ?task (SUM(?likes)/COUNT(?model) as ?roi) (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         daimo:task ?task ;
         daimo:likes ?likes .
  FILTER(?likes > 0)
}
GROUP BY ?task
HAVING(COUNT(?model) > 2)
ORDER BY DESC(?roi)
LIMIT 15""",
        complexity="advanced",
        category="perf_task_roi",
        keywords=['roi', 'engagement', 'per model', 'efficiency', 'best'],
        explanation="Tasks with best engagement per model"
    ),
    SPARQLExample(
        id="complex_perf_004",
        natural_query="repositories with highest quality score",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source (AVG(?likes) as ?avgQuality) (COUNT(?model) as ?modelCount) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:likes ?likes .
  FILTER(?likes > 5)
}
GROUP BY ?source
HAVING(COUNT(?model) > 5)
ORDER BY DESC(?avgQuality)
LIMIT 10""",
        complexity="advanced",
        category="perf_repository_quality",
        keywords=['quality', 'repository', 'score', 'best', 'rating'],
        explanation="Repositories with highest quality score"
    ),
    SPARQLExample(
        id="complex_perf_005",
        natural_query="models with balanced engagement metrics",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:downloads ?downloads ;
         daimo:likes ?likes .
  FILTER(?downloads > 1000 && ?likes > 5 && ?downloads / ?likes < 1000)
}
ORDER BY (?downloads / ?likes)
LIMIT 20""",
        complexity="advanced",
        category="perf_balanced_engagement",
        keywords=['balanced', 'equilibrium', 'ratio', 'engagement', 'consistent'],
        explanation="Models with balanced engagement metrics"
    ),
    SPARQLExample(
        id="complex_perf_006",
        natural_query="best performing models by source and task",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?source ?task (MAX(?downloads) as ?maxPerf) (COUNT(?model) as ?count) WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source ;
         daimo:task ?task ;
         daimo:downloads ?downloads .
  FILTER(?downloads > 1000)
}
GROUP BY ?source ?task
ORDER BY ?source DESC(?maxPerf)
LIMIT 25""",
        complexity="advanced",
        category="perf_best_by_source_task",
        keywords=['best', 'performing', 'source', 'task', 'top'],
        explanation="Best performing models by source and task"
    ),
    SPARQLExample(
        id="complex_perf_007",
        natural_query="top performing models with all metrics",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source ?downloads ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source ;
         daimo:downloads ?downloads ;
         daimo:likes ?likes .
  FILTER(?downloads > 5000 && ?likes > 20)
}
ORDER BY DESC(?downloads) DESC(?likes)
LIMIT 20""",
        complexity="intermediate",
        category="perf_top_multi_metrics",
        keywords=['top', 'performers', 'multiple metrics', 'best', 'high quality'],
        explanation="Top performing models with all metrics"
    ),


    SPARQLExample(
        id="basic_simple_001",
        natural_query="find bert models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "bert"))
}
LIMIT 20""",
        complexity="basic",
        category="search_by_name",
        keywords=['bert', 'search', 'find', 'title'],
        explanation="Simple search for models with 'bert' in title"
    ),
    SPARQLExample(
        id="basic_simple_002",
        natural_query="search for gpt",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "gpt"))
}
LIMIT 20""",
        complexity="basic",
        category="search_by_name",
        keywords=['gpt', 'search', 'language', 'llm'],
        explanation="Search for GPT models by title"
    ),
    SPARQLExample(
        id="basic_simple_003",
        natural_query="find diffusion models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "diffusion"))
}
LIMIT 20""",
        complexity="basic",
        category="search_by_name",
        keywords=['diffusion', 'search', 'image', 'generation'],
        explanation="Find models with 'diffusion' in title"
    ),
    SPARQLExample(
        id="basic_simple_004",
        natural_query="models with resnet in title",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "resnet"))
}
LIMIT 20""",
        complexity="basic",
        category="search_by_name",
        keywords=['resnet', 'vision', 'search', 'cv'],
        explanation="Basic search for ResNet models"
    ),
    SPARQLExample(
        id="basic_simple_005",
        natural_query="find whisper models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "whisper"))
}
LIMIT 20""",
        complexity="basic",
        category="search_by_name",
        keywords=['whisper', 'audio', 'speech', 'asr'],
        explanation="Search for Whisper speech models"
    ),
    SPARQLExample(
        id="basic_simple_006",
        natural_query="models from huggingface",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  FILTER(CONTAINS(LCASE(?source), "huggingface"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_repository",
        keywords=['huggingface', 'repository', 'source'],
        explanation="Filter models by HuggingFace repository"
    ),
    SPARQLExample(
        id="basic_simple_007",
        natural_query="find kaggle models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  FILTER(CONTAINS(LCASE(?source), "kaggle"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_repository",
        keywords=['kaggle', 'repository', 'competition'],
        explanation="Find models from Kaggle platform"
    ),
    SPARQLExample(
        id="basic_simple_008",
        natural_query="replicate models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  FILTER(CONTAINS(LCASE(?source), "replicate"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_repository",
        keywords=['replicate', 'api', 'cloud'],
        explanation="Models available on Replicate"
    ),
    SPARQLExample(
        id="basic_simple_009",
        natural_query="pytorch hub models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  FILTER(CONTAINS(LCASE(?source), "pytorch"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_repository",
        keywords=['pytorch', 'hub', 'torch'],
        explanation="Models from PyTorch Hub"
    ),
    SPARQLExample(
        id="basic_simple_010",
        natural_query="tensorflow models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?source WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:source ?source .
  FILTER(CONTAINS(LCASE(?source), "tensorflow"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_repository",
        keywords=['tensorflow', 'hub', 'google'],
        explanation="Filter by TensorFlow Hub repository"
    ),
    SPARQLExample(
        id="basic_simple_011",
        natural_query="classification models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "classification"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_task",
        keywords=['classification', 'task', 'category'],
        explanation="Models for classification tasks"
    ),
    SPARQLExample(
        id="basic_simple_012",
        natural_query="text generation models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "generation"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_task",
        keywords=['generation', 'text', 'llm'],
        explanation="Find text generation models"
    ),
    SPARQLExample(
        id="basic_simple_013",
        natural_query="question answering models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "question") || CONTAINS(LCASE(?task), "qa"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_task",
        keywords=['question', 'answering', 'qa', 'nlp'],
        explanation="Question answering task models"
    ),
    SPARQLExample(
        id="basic_simple_014",
        natural_query="translation models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "translation"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_task",
        keywords=['translation', 'language', 'multilingual'],
        explanation="Models for language translation"
    ),
    SPARQLExample(
        id="basic_simple_015",
        natural_query="summarization models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "summarization"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_task",
        keywords=['summarization', 'summary', 'text'],
        explanation="Text summarization models"
    ),
    SPARQLExample(
        id="basic_simple_016",
        natural_query="pytorch models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(CONTAINS(LCASE(?library), "pytorch"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_library",
        keywords=['pytorch', 'library', 'framework'],
        explanation="Models using PyTorch framework"
    ),
    SPARQLExample(
        id="basic_simple_017",
        natural_query="transformers library models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(CONTAINS(LCASE(?library), "transformers"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_library",
        keywords=['transformers', 'huggingface', 'library'],
        explanation="Models using transformers library"
    ),
    SPARQLExample(
        id="basic_simple_018",
        natural_query="tensorflow models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(CONTAINS(LCASE(?library), "tensorflow"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_library",
        keywords=['tensorflow', 'library', 'google'],
        explanation="TensorFlow framework models"
    ),
    SPARQLExample(
        id="basic_simple_019",
        natural_query="diffusers library",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(CONTAINS(LCASE(?library), "diffusers"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_library",
        keywords=['diffusers', 'image', 'generation'],
        explanation="Models using diffusers library"
    ),
    SPARQLExample(
        id="basic_simple_020",
        natural_query="jax models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?library WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:library ?library .
  FILTER(CONTAINS(LCASE(?library), "jax"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_library",
        keywords=['jax', 'library', 'google'],
        explanation="JAX framework models"
    ),
    SPARQLExample(
        id="basic_simple_021",
        natural_query="models with downloads",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:downloads ?downloads .
  FILTER(?downloads > 0)
}
ORDER BY DESC(?downloads)
LIMIT 20""",
        complexity="basic",
        category="filter_by_metrics",
        keywords=['downloads', 'metrics', 'popular'],
        explanation="Models sorted by download count"
    ),
    SPARQLExample(
        id="basic_simple_022",
        natural_query="models with likes",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:likes ?likes .
  FILTER(?likes > 0)
}
ORDER BY DESC(?likes)
LIMIT 20""",
        complexity="basic",
        category="filter_by_metrics",
        keywords=['likes', 'metrics', 'popular'],
        explanation="Models with most likes"
    ),
    SPARQLExample(
        id="basic_simple_023",
        natural_query="most downloaded models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?downloads WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:downloads ?downloads .
}
ORDER BY DESC(?downloads)
LIMIT 20""",
        complexity="basic",
        category="filter_by_metrics",
        keywords=['most', 'downloaded', 'top', 'popular'],
        explanation="Top downloaded models"
    ),
    SPARQLExample(
        id="basic_simple_024",
        natural_query="most liked models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?likes WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:likes ?likes .
}
ORDER BY DESC(?likes)
LIMIT 20""",
        complexity="basic",
        category="filter_by_metrics",
        keywords=['most', 'liked', 'top', 'favorites'],
        explanation="Most liked models ranking"
    ),
    SPARQLExample(
        id="basic_simple_025",
        natural_query="models with run count",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?runCount WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:runCount ?runCount .
  FILTER(?runCount > 0)
}
ORDER BY DESC(?runCount)
LIMIT 20""",
        complexity="basic",
        category="filter_by_metrics",
        keywords=['run', 'count', 'usage', 'executions'],
        explanation="Models sorted by execution count"
    ),
    SPARQLExample(
        id="basic_simple_026",
        natural_query="computer vision models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?domain WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:domain ?domain .
  FILTER(CONTAINS(LCASE(?domain), "computer") || CONTAINS(LCASE(?domain), "vision") || CONTAINS(LCASE(?domain), "cv"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_domain",
        keywords=['computer', 'vision', 'cv', 'image'],
        explanation="Computer vision domain models"
    ),
    SPARQLExample(
        id="basic_simple_027",
        natural_query="nlp models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?domain WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:domain ?domain .
  FILTER(CONTAINS(LCASE(?domain), "nlp") || CONTAINS(LCASE(?domain), "language"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_domain",
        keywords=['nlp', 'language', 'text'],
        explanation="Natural language processing models"
    ),
    SPARQLExample(
        id="basic_simple_028",
        natural_query="audio models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?domain WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:domain ?domain .
  FILTER(CONTAINS(LCASE(?domain), "audio") || CONTAINS(LCASE(?domain), "speech"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_domain",
        keywords=['audio', 'speech', 'sound'],
        explanation="Audio processing models"
    ),
    SPARQLExample(
        id="basic_simple_029",
        natural_query="image generation models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "image") && CONTAINS(LCASE(?task), "generation"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_domain",
        keywords=['image', 'generation', 'creative'],
        explanation="Image generation models"
    ),
    SPARQLExample(
        id="basic_simple_030",
        natural_query="object detection models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "object") && CONTAINS(LCASE(?task), "detection"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_domain",
        keywords=['object', 'detection', 'cv', 'yolo'],
        explanation="Object detection models"
    ),
    SPARQLExample(
        id="basic_simple_031",
        natural_query="show recent models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?lastModified WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         dcterms:modified ?lastModified .
}
ORDER BY DESC(?lastModified)
LIMIT 20""",
        complexity="basic",
        category="list_metadata",
        keywords=['recent', 'new', 'latest', 'updated'],
        explanation="Recently updated models"
    ),
    SPARQLExample(
        id="basic_simple_032",
        natural_query="list all available models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
}
LIMIT 50""",
        complexity="basic",
        category="list_metadata",
        keywords=['list', 'all', 'available', 'models'],
        explanation="List all models in catalog"
    ),
    SPARQLExample(
        id="basic_simple_033",
        natural_query="show model sources",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?source WHERE {
  ?model a daimo:Model ;
         dcterms:source ?source .
}""",
        complexity="basic",
        category="list_metadata",
        keywords=['sources', 'repositories', 'platforms'],
        explanation="List all model sources"
    ),
    SPARQLExample(
        id="basic_simple_034",
        natural_query="what tasks are available",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT DISTINCT ?task WHERE {
  ?model a daimo:Model ;
         daimo:task ?task .
}
ORDER BY ?task""",
        complexity="basic",
        category="list_metadata",
        keywords=['tasks', 'available', 'types'],
        explanation="List all available tasks"
    ),
    SPARQLExample(
        id="basic_simple_035",
        natural_query="list all libraries",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>

SELECT DISTINCT ?library WHERE {
  ?model a daimo:Model ;
         daimo:library ?library .
}
ORDER BY ?library
LIMIT 20""",
        complexity="basic",
        category="list_metadata",
        keywords=['libraries', 'frameworks', 'tools'],
        explanation="List available libraries/frameworks"
    ),
    SPARQLExample(
        id="basic_simple_036",
        natural_query="small models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "small") || CONTAINS(LCASE(?title), "mini") || CONTAINS(LCASE(?title), "tiny"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_size",
        keywords=['small', 'mini', 'tiny', 'lite'],
        explanation="Small/lightweight models"
    ),
    SPARQLExample(
        id="basic_simple_037",
        natural_query="large models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "large") || CONTAINS(LCASE(?title), "xl"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_size",
        keywords=['large', 'xl', 'big'],
        explanation="Large-scale models"
    ),
    SPARQLExample(
        id="basic_simple_038",
        natural_query="base models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "base"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_size",
        keywords=['base', 'standard', 'default'],
        explanation="Base/standard model variants"
    ),
    SPARQLExample(
        id="basic_simple_039",
        natural_query="fine-tuned models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "tuned") || CONTAINS(LCASE(?title), "finetuned") || CONTAINS(LCASE(?title), "ft"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_size",
        keywords=['tuned', 'finetuned', 'adapted'],
        explanation="Fine-tuned model variants"
    ),
    SPARQLExample(
        id="basic_simple_040",
        natural_query="instruct models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "instruct") || CONTAINS(LCASE(?title), "chat"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_size",
        keywords=['instruct', 'chat', 'conversation'],
        explanation="Instruction-tuned models"
    ),
    SPARQLExample(
        id="basic_simple_041",
        natural_query="sentiment analysis models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "sentiment"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_usecase",
        keywords=['sentiment', 'analysis', 'emotion'],
        explanation="Sentiment analysis models"
    ),
    SPARQLExample(
        id="basic_simple_042",
        natural_query="embedding models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "embedding") || CONTAINS(LCASE(?title), "embedding"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_usecase",
        keywords=['embedding', 'vector', 'representation'],
        explanation="Text/image embedding models"
    ),
    SPARQLExample(
        id="basic_simple_043",
        natural_query="segmentation models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "segmentation"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_usecase",
        keywords=['segmentation', 'mask', 'instance'],
        explanation="Image segmentation models"
    ),
    SPARQLExample(
        id="basic_simple_044",
        natural_query="text-to-speech models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "text-to-speech") || CONTAINS(LCASE(?task), "tts"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_usecase",
        keywords=['tts', 'text-to-speech', 'synthesis'],
        explanation="Text-to-speech synthesis models"
    ),
    SPARQLExample(
        id="basic_simple_045",
        natural_query="speech recognition models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title ?task WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title ;
         daimo:task ?task .
  FILTER(CONTAINS(LCASE(?task), "speech") || CONTAINS(LCASE(?task), "asr"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_usecase",
        keywords=['asr', 'speech', 'recognition', 'transcription'],
        explanation="Automatic speech recognition models"
    ),
    SPARQLExample(
        id="basic_simple_046",
        natural_query="llama models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "llama"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_architecture",
        keywords=['llama', 'meta', 'llm'],
        explanation="LLaMA model family"
    ),
    SPARQLExample(
        id="basic_simple_047",
        natural_query="clip models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "clip"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_architecture",
        keywords=['clip', 'vision', 'openai'],
        explanation="CLIP vision-language models"
    ),
    SPARQLExample(
        id="basic_simple_048",
        natural_query="vit models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "vit"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_architecture",
        keywords=['vit', 'vision', 'transformer'],
        explanation="Vision Transformer models"
    ),
    SPARQLExample(
        id="basic_simple_049",
        natural_query="t5 models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "t5"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_architecture",
        keywords=['t5', 'text', 'google'],
        explanation="T5 (Text-to-Text) models"
    ),
    SPARQLExample(
        id="basic_simple_050",
        natural_query="efficientnet models",
        sparql_query="""PREFIX daimo: <http://purl.org/pionera/daimo#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?model ?title WHERE {
  ?model a daimo:Model ;
         dcterms:title ?title .
  FILTER(CONTAINS(LCASE(?title), "efficient"))
}
LIMIT 20""",
        complexity="basic",
        category="filter_by_architecture",
        keywords=['efficientnet', 'efficient', 'architecture'],
        explanation="EfficientNet model family"
    ),
]


def get_all_examples() -> List[SPARQLExample]:
    """Retorna todos los ejemplos de la base de conocimiento"""
    return SPARQL_KNOWLEDGE_BASE


def get_examples_by_complexity(complexity: str) -> List[SPARQLExample]:
    """Filtra ejemplos por nivel de complejidad"""
    return [ex for ex in SPARQL_KNOWLEDGE_BASE if ex.complexity == complexity]


def get_examples_by_category(category: str) -> List[SPARQLExample]:
    """Filtra ejemplos por categoría"""
    return [ex for ex in SPARQL_KNOWLEDGE_BASE if ex.category == category]


def search_examples_by_keywords(keywords: List[str]) -> List[SPARQLExample]:
    """Busca ejemplos que contengan alguna de las keywords"""
    results = []
    keywords_lower = [k.lower() for k in keywords]
    
    for example in SPARQL_KNOWLEDGE_BASE:
        example_keywords_lower = [k.lower() for k in example.keywords]
        query_lower = example.natural_query.lower()
        
        # Check if any keyword matches
        for kw in keywords_lower:
            if any(kw in ek for ek in example_keywords_lower) or kw in query_lower:
                results.append(example)
                break
    
    return results
