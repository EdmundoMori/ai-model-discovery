"""
Enriched Ontology Dictionary - DAIMO v2.2

This dictionary provides semantic context about DAIMO properties
ENRICHED with real values extracted from the knowledge graph.

**AUTOMATICALLY GENERATED** by strategies/semantic_enrichment/generate_enriched_dictionary.py
Generation date: 1770932715.6133206

DO NOT EDIT MANUALLY - Use normalization pipeline instead.

Author: Edmundo Mori
"""

from typing import Dict, List


# Ontology properties enriched with real values from KG
ONTOLOGY_PROPERTIES_ENRICHED = {
    "metadata": [
        {
            "name": "title",
            "namespace": "dcterms",
            "desc": "Model name or title",
            "type": "string",
            "examples": ["FILTER(CONTAINS(?title, 'bert'))", 'SELECT ?model ?title'],
            "frequency": "very_high",
            "values": ['vocab.txt', 'LICENSE', 'flax_model.msgpack', 'onnx/model.onnx', 'modules.json'],
            "has_real_values": True,
            "value_count": 5,
        },
        {
            "name": "description",
            "namespace": "dcterms",
            "desc": "Detailed model description",
            "type": "string",
            "examples": ["FILTER(CONTAINS(?description, 'sentiment'))", 'SELECT ?model ?description'],
            "frequency": "high",
            "values": ['Please enter a description about the method here'],
            "has_real_values": True,
            "value_count": 1,
        },
        {
            "name": "source",
            "namespace": "dcterms",
            "desc": "Repository source (HuggingFace, PyTorch Hub, etc.)",
            "type": "string",
            "examples": ["FILTER(?source = 'huggingface')", 'SELECT DISTINCT ?source'],
            "frequency": "very_high",
            "values": ['PapersWithCode', 'HuggingFace', 'PyTorch Hub', 'Civitai', 'Kaggle', 'TensorFlow Hub', 'Replicate'],
            "has_real_values": True,
            "value_count": 7,
        },
        {
            "name": "creator",
            "namespace": "dcterms",
            "desc": "Model author or organization",
            "type": "string",
            "examples": ["FILTER(?creator = 'google')", 'SELECT ?model ?creator'],
            "frequency": "high",
            "values": ['0_1_Deep_Neural_Networks_via_Block_Coordinate_Descent', 'pytorch', 'Qwen', 'TensorFlow', 'ultralytics', 'google', 'microsoft', 'facebook', 'facebookresearch', 'sentence-transformers', '0-1_laws_for_pattern_occurrences_in_phylogenetic_trees_and_networks', 'meta-llama', 'openai', 'timm', '0-1_phase_transitions_in_sparse_spiked_matrix_estimation'],
            "has_real_values": True,
            "value_count": 15,
        },
        {
            "name": "created",
            "namespace": "dcterms",
            "desc": "Creation date",
            "type": "datetime",
            "examples": ['FILTER(YEAR(?created) = 2024)', 'ORDER BY DESC(?created)'],
            "frequency": "high",
            "values": ['2022-03-02T23:29:05+00:00', '2020-10-06T00:00:00', '2022-03-02T23:29:04+00:00'],
            "has_real_values": True,
            "value_count": 3,
        },
        {
            "name": "modified",
            "namespace": "dcterms",
            "desc": "Last modification date",
            "type": "datetime",
            "examples": ["FILTER(?modified > '2024-01-01')", 'ORDER BY DESC(?modified)'],
            "frequency": "high",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
        {
            "name": "identifier",
            "namespace": "dcterms",
            "desc": "Unique model identifier",
            "type": "string",
            "examples": ["FILTER(?identifier = 'bert-base-uncased')", 'SELECT ?identifier'],
            "frequency": "high",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
        {
            "name": "subject",
            "namespace": "dcterms",
            "desc": "Subject or topic area",
            "type": "string",
            "examples": ["FILTER(?subject = 'NLP')", 'SELECT DISTINCT ?subject'],
            "frequency": "high",
            "values": ['General', 'Computer Vision', 'image-classification', 'text-generation', 'sentence-similarity', 'feature-extraction', 'fill-mask', 'image-text-to-text', 'automatic-speech-recognition', 'Natural Language Processing', 'text-classification', 'object-detection', 'Graphs', 'zero-shot-image-classification', 'image-segmentation'],
            "has_real_values": True,
            "value_count": 15,
        },
    ],

    "technical": [
        {
            "name": "library",
            "namespace": "daimo",
            "desc": "ML framework (PyTorch, TensorFlow, etc.)",
            "type": "string",
            "examples": ["FILTER(?library = 'PyTorch')", "SELECT ?model WHERE { ?model daimo:library 'PyTorch' }"],
            "frequency": "very_high",
            "values": ['transformers', 'PyTorch', 'diffusers', 'sentence-transformers', 'ModelFramework.MODEL_FRAMEWORK_TENSOR_FLOW_2', 'ModelFramework.MODEL_FRAMEWORK_PY_TORCH', '0.16.11', 'TensorFlow', 'ModelFramework.MODEL_FRAMEWORK_TRANSFORMERS', 'ModelFramework.MODEL_FRAMEWORK_TF_LITE', 'ModelFramework.MODEL_FRAMEWORK_KERAS', 'timm', 'pyannote-audio', 'ModelFramework.MODEL_FRAMEWORK_TF_JS', 'diffusion-single-file'],
            "has_real_values": True,
            "value_count": 15,
        },
        {
            "name": "task",
            "namespace": "daimo",
            "desc": "ML task (image-classification, text-generation, etc.)",
            "type": "string",
            "examples": ["FILTER(?task = 'text-generation')", 'SELECT DISTINCT ?task'],
            "frequency": "very_high",
            "values": ['image-classification', 'other', 'text-generation', 'model', 'Graphs', 'sentence-similarity', 'feature-extraction', 'object-detection', 'fill-mask', 'image-text-to-text', 'automatic-speech-recognition', 'Reinforcement Learning', 'text-classification', 'Sequential', 'zero-shot-image-classification'],
            "has_real_values": True,
            "value_count": 15,
        },
        {
            "name": "architecture",
            "namespace": "daimo",
            "desc": "Model architecture (BERT, GPT, ResNet, etc.)",
            "type": "string",
            "examples": ["FILTER(CONTAINS(?arch, 'transformer'))", '?model daimo:hasArchitecture/daimo:architecture ?arch'],
            "frequency": "medium",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
        {
            "name": "parameterCount",
            "namespace": "daimo",
            "desc": "Number of model parameters (in millions)",
            "type": "integer",
            "examples": ['FILTER(?params < 1000000000)', 'ORDER BY ?params'],
            "frequency": "low",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
        {
            "name": "baseModel",
            "namespace": "daimo",
            "desc": "Base model used for fine-tuning",
            "type": "string",
            "examples": ["FILTER(?baseModel = 'bert-base')", 'SELECT ?model ?baseModel'],
            "frequency": "medium",
            "values": ['SD 1.5', 'Illustrious', 'Pony', 'SDXL 1.0'],
            "has_real_values": True,
            "value_count": 4,
        },
        {
            "name": "fineTunedFrom",
            "namespace": "daimo",
            "desc": "Original model before fine-tuning",
            "type": "uri",
            "examples": ['?model daimo:fineTunedFrom ?original', 'FILTER(BOUND(?fineTunedFrom))'],
            "frequency": "medium",
            "values": ['base_SD_1.5', 'base_Illustrious', 'base_Pony', 'base_SDXL_1.0'],
            "has_real_values": True,
            "value_count": 4,
        },
        {
            "name": "framework",
            "namespace": "daimo",
            "desc": "Additional framework or tooling",
            "type": "string",
            "examples": ["FILTER(?framework = 'transformers')", 'SELECT ?framework'],
            "frequency": "low",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
        {
            "name": "language",
            "namespace": "daimo",
            "desc": "Natural language (for NLP models)",
            "type": "string",
            "examples": ["FILTER(?language = 'English')", "FILTER(?language IN ('en', 'es'))"],
            "frequency": "low",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
        {
            "name": "modelType",
            "namespace": "daimo",
            "desc": "Model type (generative, discriminative, etc.)",
            "type": "string",
            "examples": ["FILTER(?modelType = 'generative')", 'SELECT DISTINCT ?modelType'],
            "frequency": "low",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
    ],

    "metrics": [
        {
            "name": "downloads",
            "namespace": "daimo",
            "desc": "Total number of downloads",
            "type": "integer",
            "examples": ['FILTER(?downloads > 1000)', 'ORDER BY DESC(?downloads)'],
            "frequency": "very_high",
            "values": ['1751000', '5681300', '354400'],
            "has_real_values": True,
            "value_count": 3,
        },
        {
            "name": "likes",
            "namespace": "daimo",
            "desc": "Number of likes or favorites",
            "type": "integer",
            "examples": ['FILTER(?likes > 100)', 'ORDER BY DESC(?likes)'],
            "frequency": "very_high",
            "values": ['17510', '56813', '3544', '10', '13', '19', '25', '18', '12', '20', '14'],
            "has_real_values": True,
            "value_count": 11,
        },
        {
            "name": "rating",
            "namespace": "daimo",
            "desc": "User rating (0-5 scale)",
            "type": "float",
            "examples": ['FILTER(?rating >= 4.0)', 'ORDER BY DESC(?rating)'],
            "frequency": "medium",
            "values": ['0.0'],
            "has_real_values": True,
            "value_count": 1,
        },
        {
            "name": "runCount",
            "namespace": "daimo",
            "desc": "Number of times model was run",
            "type": "integer",
            "examples": ['FILTER(?runCount > 500)', 'ORDER BY DESC(?runCount)'],
            "frequency": "medium",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
    ],

    "access": [
        {
            "name": "accessLevel",
            "namespace": "daimo",
            "desc": "Access level (public, community, gated, official)",
            "type": "string",
            "examples": ["FILTER(?accessLevel = 'public')", 'SELECT DISTINCT ?accessLevel'],
            "frequency": "high",
            "values": ['public', 'community', 'gated', 'official'],
            "has_real_values": True,
            "value_count": 4,
        },
        {
            "name": "requiresApproval",
            "namespace": "daimo",
            "desc": "Whether model requires approval to access",
            "type": "boolean",
            "examples": ['FILTER(?requiresApproval = false)', 'SELECT ?model WHERE { ?model daimo:requiresApproval true }'],
            "frequency": "medium",
            "values": ['true'],
            "has_real_values": True,
            "value_count": 1,
        },
        {
            "name": "isGated",
            "namespace": "daimo",
            "desc": "Whether model is behind access gate",
            "type": "boolean",
            "examples": ['FILTER(?isGated = false)', 'SELECT COUNT(?model) WHERE { ?model daimo:isGated true }'],
            "frequency": "medium",
            "values": ['false'],
            "has_real_values": True,
            "value_count": 1,
        },
        {
            "name": "isPrivate",
            "namespace": "daimo",
            "desc": "Whether model is private",
            "type": "boolean",
            "examples": ['FILTER(?isPrivate = false)', 'SELECT ?model WHERE { ?model daimo:isPrivate false }'],
            "frequency": "medium",
            "values": ['false'],
            "has_real_values": True,
            "value_count": 1,
        },
        {
            "name": "license",
            "namespace": "daimo",
            "desc": "Model license (MIT, Apache, etc.)",
            "type": "string",
            "examples": ["FILTER(?license = 'mit')", 'SELECT DISTINCT ?license'],
            "frequency": "low",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
        {
            "name": "accessControl",
            "namespace": "daimo",
            "desc": "Access control policy",
            "type": "string",
            "examples": ["FILTER(?accessControl = 'open')", 'SELECT ?model ?accessControl'],
            "frequency": "medium",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
    ],

    "resources": [
        {
            "name": "sourceURL",
            "namespace": "daimo",
            "desc": "URL to model source repository",
            "type": "uri",
            "examples": ['SELECT ?model ?sourceURL', "FILTER(CONTAINS(STR(?sourceURL), 'huggingface'))"],
            "frequency": "high",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
        {
            "name": "githubURL",
            "namespace": "daimo",
            "desc": "GitHub repository URL",
            "type": "uri",
            "examples": ['FILTER(BOUND(?githubURL))', 'SELECT ?model ?githubURL'],
            "frequency": "medium",
            "values": ['vision', 'yolov5', 'pytorchvideo'],
            "has_real_values": True,
            "value_count": 3,
        },
        {
            "name": "paper",
            "namespace": "daimo",
            "desc": "Associated research paper",
            "type": "uri",
            "examples": ['FILTER(BOUND(?paper))', '?model daimo:paper ?paper'],
            "frequency": "medium",
            "values": ['https://paperswithcode.com/paper/0-1-deep-neural-networks-via-block-coordinate', 'https://paperswithcode.com/paper/0-1-laws-for-pattern-occurrences-in', 'https://paperswithcode.com/paper/0-1-phase-transitions-in-sparse-spiked-matrix'],
            "has_real_values": True,
            "value_count": 3,
        },
        {
            "name": "arxivId",
            "namespace": "daimo",
            "desc": "ArXiv paper identifier",
            "type": "string",
            "examples": ['FILTER(BOUND(?arxivId))', 'SELECT ?model ?arxivId'],
            "frequency": "medium",
            "values": ['2206.09379', '2402.04499', '1911.05030'],
            "has_real_values": True,
            "value_count": 3,
        },
        {
            "name": "coverImageURL",
            "namespace": "daimo",
            "desc": "URL to model cover image",
            "type": "uri",
            "examples": ['FILTER(BOUND(?coverImageURL))', 'SELECT ?model ?coverImageURL'],
            "frequency": "medium",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
        {
            "name": "hasFile",
            "namespace": "daimo",
            "desc": "Model has associated files",
            "type": "uri",
            "examples": ['?model daimo:hasFile ?file', 'SELECT COUNT(?file) WHERE { ?model daimo:hasFile ?file }'],
            "frequency": "very_high",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
    ],

    "temporal": [
        {
            "name": "yearIntroduced",
            "namespace": "daimo",
            "desc": "Year model was introduced",
            "type": "integer",
            "examples": ['FILTER(?yearIntroduced >= 2020)', 'ORDER BY DESC(?yearIntroduced)'],
            "frequency": "medium",
            "values": ['2000'],
            "has_real_values": True,
            "value_count": 1,
        },
        {
            "name": "versionId",
            "namespace": "daimo",
            "desc": "Model version identifier",
            "type": "string",
            "examples": ["FILTER(?versionId = 'v2.0')", 'SELECT ?model ?versionId'],
            "frequency": "medium",
            "values": [],
            "has_real_values": False,
            "value_count": 0,
        },
    ],

    "flags": [
        {
            "name": "isOfficial",
            "namespace": "daimo",
            "desc": "Whether model is official release",
            "type": "boolean",
            "examples": ['FILTER(?isOfficial = true)', 'SELECT ?model WHERE { ?model daimo:isOfficial true }'],
            "frequency": "medium",
            "values": ['false', 'true'],
            "has_real_values": True,
            "value_count": 2,
        },
        {
            "name": "isNSFW",
            "namespace": "daimo",
            "desc": "Whether model generates NSFW content",
            "type": "boolean",
            "examples": ['FILTER(?isNSFW = false)', 'SELECT ?model WHERE { ?model daimo:isNSFW false }'],
            "frequency": "medium",
            "values": ['false', 'true'],
            "has_real_values": True,
            "value_count": 2,
        },
        {
            "name": "isPOI",
            "namespace": "daimo",
            "desc": "Whether model is point of interest",
            "type": "boolean",
            "examples": ['FILTER(?isPOI = true)', 'SELECT ?model WHERE { ?model daimo:isPOI true }'],
            "frequency": "medium",
            "values": ['false'],
            "has_real_values": True,
            "value_count": 1,
        },
    ],

}

# Alias for backwards compatibility
ONTOLOGY_PROPERTIES = ONTOLOGY_PROPERTIES_ENRICHED


def get_all_properties() -> List[Dict]:
    """Get flat list of all properties"""
    all_props = []
    for category in ONTOLOGY_PROPERTIES_ENRICHED.values():
        all_props.extend(category)
    return all_props


def get_properties_with_values() -> List[Dict]:
    """Get only properties that have real values from KG"""
    return [p for p in get_all_properties() if p["has_real_values"]]


def get_property_values(property_name: str) -> List[str]:
    """
    Get real values for a specific property
    
    Args:
        property_name: Name of property (e.g., "task", "library")
    
    Returns:
        List of real values from KG
    """
    for prop in get_all_properties():
        if prop["name"] == property_name:
            return prop.get("values", [])
    return []


def get_property_context_with_values(properties: List[Dict]) -> str:
    """
    Generate context for prompt INCLUDING real values
    
    This is the key enhancement: Instead of just describing properties,
    we show the LLM actual values that exist in the database.
    """
    lines = ["AVAILABLE PROPERTIES (with real values):\\n"]
    
    for prop in properties:
        ns_prefix = "daimo" if prop["namespace"] == "daimo" else "dcterms"
        prop_name = prop["name"]
        prop_desc = prop["desc"]
        prop_line = f"• {ns_prefix}:{prop_name} - {prop_desc}"
        
        if prop.get("has_real_values") and prop.get("values"):
            prop_values = prop["values"][:10]
            values_list = [f'"{v}"' for v in prop_values]
            values_str = ", ".join(values_list)
            prop_line += f"\\n  Values: [{values_str}]"
        
        lines.append(prop_line)
    
    return "\\n".join(lines)


# Statistics
TOTAL_PROPERTIES = 38
PROPERTIES_WITH_VALUES = 24
TOTAL_VALUES_EXTRACTED = 136


# ============================================================================
# Backwards compatibility functions from original ontology_dictionary.py
# ============================================================================

def get_properties_by_frequency(frequency: str) -> List[Dict]:
    """Get properties filtered by frequency"""
    all_props = get_all_properties()
    return [p for p in all_props if p.get("frequency") == frequency]


def get_top_properties(n: int = 10) -> List[Dict]:
    """Get top N most frequent properties"""
    all_props = get_all_properties()
    
    # Sort by frequency
    freq_order = {"very_high": 0, "high": 1, "medium": 2, "low": 3}
    sorted_props = sorted(all_props, key=lambda p: freq_order.get(p.get("frequency", "low"), 3))
    
    return sorted_props[:n]


def get_property_context_compact(properties: List[Dict]) -> str:
    """
    Generate compact context for prompt (optimized for fewer tokens)
    
    ENHANCED: Includes real values when available
    """
    lines = ["AVAILABLE PROPERTIES:"]
    
    for prop in properties:
        ns_prefix = "daimo" if prop["namespace"] == "daimo" else "dcterms"
        examples_str = " | ".join(prop["examples"][:1]) if prop.get("examples") else ""
        
        line = f"• {ns_prefix}:{prop['name']} - {prop['desc']}"
        if examples_str:
            line += f" - Ex: {examples_str}"
        
        # Add values if available
        if prop.get("has_real_values") and prop.get("values"):
            vals = prop["values"][:5]
            line += f" - Values: {', '.join(str(v) for v in vals)}"
        
        lines.append(line)
    
    return "\n".join(lines)


def get_property_context_detailed(properties: List[Dict]) -> str:
    """
    Generate detailed context by category
    
    ENHANCED: Includes real values when available
    """
    lines = ["AVAILABLE PROPERTIES (by category):\\n"]
    
    for category, props in ONTOLOGY_PROPERTIES.items():
        # Filter only properties in the list
        category_props = [p for p in props if p in properties]
        
        if category_props:
            lines.append(f"\\n{category.upper()}:")
            for prop in category_props:
                ns_prefix = "daimo" if prop["namespace"] == "daimo" else "dcterms"
                lines.append(f"• {ns_prefix}:{prop['name']} ({prop.get('type', 'string')}) - {prop['desc']}")
                
                if prop.get("examples"):
                    lines.append(f"  Examples: {'; '.join(prop['examples'][:2])}")
                
                # Add real values
                if prop.get("has_real_values") and prop.get("values"):
                    vals_str = ', '.join(f'"{v}"' for v in prop["values"][:10])
                    lines.append(f"  Real values: [{vals_str}]")
    
    return "\\n".join(lines)


def get_property_suggestions(query: str) -> List[str]:
    """
    Suggest relevant properties based on user query
    
    Uses keywords to match properties
    """
    query_lower = query.lower()
    suggestions = []
    
    # Keyword mapping to properties
    keyword_map = {
        "download": ["downloads"],
        "popular": ["downloads", "likes"],
        "like": ["likes"],
        "rating": ["rating", "likes"],
        "framework": ["library", "framework"],
        "pytorch": ["library"],
        "tensorflow": ["library"],
        "transformers": ["library"],
        "diffusers": ["library"],
        "task": ["task"],
        "classification": ["task"],
        "generation": ["task"],
        "detection": ["task"],
        "language": ["language", "task"],
        "vision": ["task"],
        "computer vision": ["task"],
        "nlp": ["task"],
        "image": ["task"],
        "text": ["task"],
        "date": ["created", "modified", "yearIntroduced"],
        "year": ["yearIntroduced"],
        "recent": ["created", "modified"],
        "new": ["created"],
        "license": ["license"],
        "open": ["accessLevel", "license"],
        "private": ["isPrivate", "accessLevel"],
        "public": ["accessLevel"],
        "paper": ["paper", "arxivId"],
        "arxiv": ["arxivId"],
        "github": ["githubURL"],
        "base model": ["baseModel", "fineTunedFrom"],
        "fine-tun": ["fineTunedFrom", "baseModel"],
        "author": ["creator"],
        "created by": ["creator"],
        "made by": ["creator"],
    }
    
    # Match keywords
    for keyword, props in keyword_map.items():
        if keyword in query_lower:
            suggestions.extend(props)
    
    # Remove duplicates while preserving order
    seen = set()
    suggestions = [x for x in suggestions if not (x in seen or seen.add(x))]
    
    return suggestions[:10]
