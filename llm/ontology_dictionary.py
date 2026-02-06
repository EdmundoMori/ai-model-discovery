"""
Diccionario de Propiedades de la Ontología DAIMO

Este diccionario proporciona contexto semántico sobre las propiedades
de la ontología para mejorar la generación de queries SPARQL.

Autor: Edmundo Mori
Fecha: 2026-02-05
"""

from typing import Dict, List

# Diccionario completo de propiedades (agrupado por categoría)
ONTOLOGY_PROPERTIES = {
    "metadata": [
        {
            "name": "title",
            "namespace": "dcterms",
            "desc": "Model name or title",
            "type": "string",
            "examples": ["FILTER(CONTAINS(?title, 'bert'))", "SELECT ?model ?title"],
            "frequency": "very_high"
        },
        {
            "name": "description",
            "namespace": "dcterms",
            "desc": "Detailed model description",
            "type": "string",
            "examples": ["FILTER(CONTAINS(?description, 'sentiment'))", "SELECT ?model ?description"],
            "frequency": "high"
        },
        {
            "name": "source",
            "namespace": "dcterms",
            "desc": "Repository source (HuggingFace, PyTorch Hub, etc.)",
            "type": "string",
            "examples": ["FILTER(?source = 'huggingface')", "SELECT DISTINCT ?source"],
            "frequency": "very_high"
        },
        {
            "name": "creator",
            "namespace": "dcterms",
            "desc": "Model author or organization",
            "type": "string",
            "examples": ["FILTER(?creator = 'google')", "SELECT ?model ?creator"],
            "frequency": "high"
        },
        {
            "name": "created",
            "namespace": "dcterms",
            "desc": "Creation date",
            "type": "datetime",
            "examples": ["FILTER(YEAR(?created) = 2024)", "ORDER BY DESC(?created)"],
            "frequency": "high"
        },
        {
            "name": "modified",
            "namespace": "dcterms",
            "desc": "Last modification date",
            "type": "datetime",
            "examples": ["FILTER(?modified > '2024-01-01')", "ORDER BY DESC(?modified)"],
            "frequency": "high"
        },
        {
            "name": "identifier",
            "namespace": "dcterms",
            "desc": "Unique model identifier",
            "type": "string",
            "examples": ["FILTER(?identifier = 'bert-base-uncased')", "SELECT ?identifier"],
            "frequency": "high"
        },
        {
            "name": "subject",
            "namespace": "dcterms",
            "desc": "Subject or topic area",
            "type": "string",
            "examples": ["FILTER(?subject = 'NLP')", "SELECT DISTINCT ?subject"],
            "frequency": "high"
        }
    ],
    
    "technical": [
        {
            "name": "library",
            "namespace": "daimo",
            "desc": "ML framework (PyTorch, TensorFlow, etc.)",
            "type": "string",
            "examples": ["FILTER(?library = 'PyTorch')", "SELECT ?model WHERE { ?model daimo:library 'PyTorch' }"],
            "frequency": "very_high"
        },
        {
            "name": "task",
            "namespace": "daimo",
            "desc": "ML task (image-classification, text-generation, etc.)",
            "type": "string",
            "examples": ["FILTER(?task = 'text-generation')", "SELECT DISTINCT ?task"],
            "frequency": "very_high"
        },
        {
            "name": "architecture",
            "namespace": "daimo",
            "desc": "Model architecture (BERT, GPT, ResNet, etc.)",
            "type": "string",
            "examples": ["FILTER(CONTAINS(?arch, 'transformer'))", "?model daimo:hasArchitecture/daimo:architecture ?arch"],
            "frequency": "medium"
        },
        {
            "name": "parameterCount",
            "namespace": "daimo",
            "desc": "Number of model parameters (in millions)",
            "type": "integer",
            "examples": ["FILTER(?params < 1000000000)", "ORDER BY ?params"],
            "frequency": "low"
        },
        {
            "name": "baseModel",
            "namespace": "daimo",
            "desc": "Base model used for fine-tuning",
            "type": "string",
            "examples": ["FILTER(?baseModel = 'bert-base')", "SELECT ?model ?baseModel"],
            "frequency": "medium"
        },
        {
            "name": "fineTunedFrom",
            "namespace": "daimo",
            "desc": "Original model before fine-tuning",
            "type": "uri",
            "examples": ["?model daimo:fineTunedFrom ?original", "FILTER(BOUND(?fineTunedFrom))"],
            "frequency": "medium"
        },
        {
            "name": "framework",
            "namespace": "daimo",
            "desc": "Additional framework or tooling",
            "type": "string",
            "examples": ["FILTER(?framework = 'transformers')", "SELECT ?framework"],
            "frequency": "low"
        },
        {
            "name": "language",
            "namespace": "daimo",
            "desc": "Natural language (for NLP models)",
            "type": "string",
            "examples": ["FILTER(?language = 'English')", "FILTER(?language IN ('en', 'es'))"],
            "frequency": "low"
        },
        {
            "name": "modelType",
            "namespace": "daimo",
            "desc": "Model type (generative, discriminative, etc.)",
            "type": "string",
            "examples": ["FILTER(?modelType = 'generative')", "SELECT DISTINCT ?modelType"],
            "frequency": "low"
        }
    ],
    
    "metrics": [
        {
            "name": "downloads",
            "namespace": "daimo",
            "desc": "Total number of downloads",
            "type": "integer",
            "examples": ["FILTER(?downloads > 1000)", "ORDER BY DESC(?downloads)"],
            "frequency": "very_high"
        },
        {
            "name": "likes",
            "namespace": "daimo",
            "desc": "Number of likes or favorites",
            "type": "integer",
            "examples": ["FILTER(?likes > 100)", "ORDER BY DESC(?likes)"],
            "frequency": "very_high"
        },
        {
            "name": "rating",
            "namespace": "daimo",
            "desc": "User rating (0-5 scale)",
            "type": "float",
            "examples": ["FILTER(?rating >= 4.0)", "ORDER BY DESC(?rating)"],
            "frequency": "medium"
        },
        {
            "name": "runCount",
            "namespace": "daimo",
            "desc": "Number of times model was run",
            "type": "integer",
            "examples": ["FILTER(?runCount > 500)", "ORDER BY DESC(?runCount)"],
            "frequency": "medium"
        }
    ],
    
    "access": [
        {
            "name": "accessLevel",
            "namespace": "daimo",
            "desc": "Access level (public, community, gated, official)",
            "type": "string",
            "examples": ["FILTER(?accessLevel = 'public')", "SELECT DISTINCT ?accessLevel"],
            "frequency": "high"
        },
        {
            "name": "requiresApproval",
            "namespace": "daimo",
            "desc": "Whether model requires approval to access",
            "type": "boolean",
            "examples": ["FILTER(?requiresApproval = false)", "SELECT ?model WHERE { ?model daimo:requiresApproval true }"],
            "frequency": "medium"
        },
        {
            "name": "isGated",
            "namespace": "daimo",
            "desc": "Whether model is behind access gate",
            "type": "boolean",
            "examples": ["FILTER(?isGated = false)", "SELECT COUNT(?model) WHERE { ?model daimo:isGated true }"],
            "frequency": "medium"
        },
        {
            "name": "isPrivate",
            "namespace": "daimo",
            "desc": "Whether model is private",
            "type": "boolean",
            "examples": ["FILTER(?isPrivate = false)", "SELECT ?model WHERE { ?model daimo:isPrivate false }"],
            "frequency": "medium"
        },
        {
            "name": "license",
            "namespace": "daimo",
            "desc": "Model license (MIT, Apache, etc.)",
            "type": "string",
            "examples": ["FILTER(?license = 'mit')", "SELECT DISTINCT ?license"],
            "frequency": "low"
        },
        {
            "name": "accessControl",
            "namespace": "daimo",
            "desc": "Access control policy",
            "type": "string",
            "examples": ["FILTER(?accessControl = 'open')", "SELECT ?model ?accessControl"],
            "frequency": "medium"
        }
    ],
    
    "resources": [
        {
            "name": "sourceURL",
            "namespace": "daimo",
            "desc": "URL to model source repository",
            "type": "uri",
            "examples": ["SELECT ?model ?sourceURL", "FILTER(CONTAINS(STR(?sourceURL), 'huggingface'))"],
            "frequency": "high"
        },
        {
            "name": "githubURL",
            "namespace": "daimo",
            "desc": "GitHub repository URL",
            "type": "uri",
            "examples": ["FILTER(BOUND(?githubURL))", "SELECT ?model ?githubURL"],
            "frequency": "medium"
        },
        {
            "name": "paper",
            "namespace": "daimo",
            "desc": "Associated research paper",
            "type": "uri",
            "examples": ["FILTER(BOUND(?paper))", "?model daimo:paper ?paper"],
            "frequency": "medium"
        },
        {
            "name": "arxivId",
            "namespace": "daimo",
            "desc": "ArXiv paper identifier",
            "type": "string",
            "examples": ["FILTER(BOUND(?arxivId))", "SELECT ?model ?arxivId"],
            "frequency": "medium"
        },
        {
            "name": "coverImageURL",
            "namespace": "daimo",
            "desc": "URL to model cover image",
            "type": "uri",
            "examples": ["FILTER(BOUND(?coverImageURL))", "SELECT ?model ?coverImageURL"],
            "frequency": "medium"
        },
        {
            "name": "hasFile",
            "namespace": "daimo",
            "desc": "Model has associated files",
            "type": "uri",
            "examples": ["?model daimo:hasFile ?file", "SELECT COUNT(?file) WHERE { ?model daimo:hasFile ?file }"],
            "frequency": "very_high"
        }
    ],
    
    "temporal": [
        {
            "name": "yearIntroduced",
            "namespace": "daimo",
            "desc": "Year model was introduced",
            "type": "integer",
            "examples": ["FILTER(?yearIntroduced >= 2020)", "ORDER BY DESC(?yearIntroduced)"],
            "frequency": "medium"
        },
        {
            "name": "versionId",
            "namespace": "daimo",
            "desc": "Model version identifier",
            "type": "string",
            "examples": ["FILTER(?versionId = 'v2.0')", "SELECT ?model ?versionId"],
            "frequency": "medium"
        }
    ],
    
    "flags": [
        {
            "name": "isOfficial",
            "namespace": "daimo",
            "desc": "Whether model is official release",
            "type": "boolean",
            "examples": ["FILTER(?isOfficial = true)", "SELECT ?model WHERE { ?model daimo:isOfficial true }"],
            "frequency": "medium"
        },
        {
            "name": "isNSFW",
            "namespace": "daimo",
            "desc": "Whether model generates NSFW content",
            "type": "boolean",
            "examples": ["FILTER(?isNSFW = false)", "SELECT ?model WHERE { ?model daimo:isNSFW false }"],
            "frequency": "medium"
        },
        {
            "name": "isPOI",
            "namespace": "daimo",
            "desc": "Whether model is point of interest",
            "type": "boolean",
            "examples": ["FILTER(?isPOI = true)", "SELECT ?model WHERE { ?model daimo:isPOI true }"],
            "frequency": "medium"
        }
    ]
}


def get_all_properties() -> List[Dict]:
    """Obtener lista plana de todas las propiedades"""
    all_props = []
    for category in ONTOLOGY_PROPERTIES.values():
        all_props.extend(category)
    return all_props


def get_properties_by_frequency(frequency: str) -> List[Dict]:
    """Obtener propiedades filtradas por frecuencia"""
    all_props = get_all_properties()
    return [p for p in all_props if p["frequency"] == frequency]


def get_top_properties(n: int = 10) -> List[Dict]:
    """Obtener las N propiedades más frecuentes"""
    all_props = get_all_properties()
    
    # Ordenar por frecuencia
    freq_order = {"very_high": 0, "high": 1, "medium": 2, "low": 3}
    sorted_props = sorted(all_props, key=lambda p: freq_order[p["frequency"]])
    
    return sorted_props[:n]


def get_property_context_compact(properties: List[Dict]) -> str:
    """
    Generar contexto compacto de propiedades para el prompt
    
    Formato optimizado para minimizar tokens
    """
    lines = ["AVAILABLE PROPERTIES:"]
    
    for prop in properties:
        ns_prefix = "daimo" if prop["namespace"] == "daimo" else "dcterms"
        examples_str = " | ".join(prop["examples"][:1])  # Solo 1 ejemplo
        
        line = f"• {ns_prefix}:{prop['name']} - {prop['desc']} - Ex: {examples_str}"
        lines.append(line)
    
    return "\n".join(lines)


def get_property_context_detailed(properties: List[Dict]) -> str:
    """
    Generar contexto detallado de propiedades por categoría
    
    Usado cuando RAG score es bajo
    """
    lines = ["AVAILABLE PROPERTIES (by category):\n"]
    
    for category, props in ONTOLOGY_PROPERTIES.items():
        # Filtrar solo las propiedades en la lista
        category_props = [p for p in props if p in properties]
        
        if category_props:
            lines.append(f"\n{category.upper()}:")
            for prop in category_props:
                ns_prefix = "daimo" if prop["namespace"] == "daimo" else "dcterms"
                lines.append(f"• {ns_prefix}:{prop['name']} ({prop['type']}) - {prop['desc']}")
                lines.append(f"  Examples: {'; '.join(prop['examples'][:2])}")
    
    return "\n".join(lines)


def get_property_suggestions(query: str) -> List[str]:
    """
    Sugerir propiedades relevantes basadas en la query del usuario
    
    Usa palabras clave para matchear propiedades
    """
    query_lower = query.lower()
    suggestions = []
    
    # Mapeo de palabras clave a propiedades
    keyword_map = {
        "download": ["downloads"],
        "popular": ["downloads", "likes"],
        "like": ["likes"],
        "rating": ["rating", "likes"],
        "framework": ["library", "framework"],
        "pytorch": ["library"],
        "tensorflow": ["library"],
        "task": ["task"],
        "classification": ["task"],
        "generation": ["task"],
        "date": ["created", "modified", "yearIntroduced"],
        "year": ["yearIntroduced"],
        "recent": ["created", "modified"],
        "access": ["accessLevel", "requiresApproval", "isGated"],
        "public": ["accessLevel"],
        "private": ["isPrivate", "accessLevel"],
        "official": ["isOfficial"],
        "author": ["creator"],
        "size": ["parameterCount"],
        "parameters": ["parameterCount"],
        "architecture": ["architecture"],
        "paper": ["paper", "arxivId"],
        "license": ["license"],
        "language": ["language"],
        "version": ["versionId"]
    }
    
    for keyword, props in keyword_map.items():
        if keyword in query_lower:
            suggestions.extend(props)
    
    return list(set(suggestions))  # Remover duplicados
