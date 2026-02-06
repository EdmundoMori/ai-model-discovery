# PapersWithCode Repository Mapping Analysis

## Overview
This document analyzes how to map PapersWithCode data to the refactored DAIMO ontology v2.1 (0% redundancy).

## Data Sources
PapersWithCode data is available via HuggingFace datasets:
1. **pwc-archive/methods** - AI models/algorithms
2. **pwc-archive/links-between-paper-and-code** - Paper-code connections
3. **pwc-archive/papers-with-abstracts** - Academic papers
4. **pwc-archive/evaluation-tables** - Benchmark results

## Sample Data Structure

### Methods (Models/Algorithms)
```
url: str                    # PapersWithCode URL
name: str                   # Method/model name
full_name: str              # Full method name
description: str            # Method description
paper: dict                 # Associated paper {title, url}
introduced_year: int        # Year introduced
source_url: str             # arXiv/paper URL
source_title: str           # Paper title
code_snippet_url: str       # Code URL (if available)
num_papers: int             # Number of papers using this method
collections: list           # Research areas [{area, area_id, collection}]
```

### Links Between Papers and Code
```
paper_url: str              # PapersWithCode paper URL
paper_title: str            # Paper title
paper_arxiv_id: str         # arXiv ID
paper_url_abs: str          # Abstract URL
paper_url_pdf: str          # PDF URL
repo_url: str               # GitHub repository URL
is_official: bool           # Is official implementation
mentioned_in_paper: bool    # Code mentioned in paper
mentioned_in_github: bool   # Paper mentioned in GitHub
framework: str              # Framework (PyTorch, TensorFlow, none, etc.)
```

### Papers
```
paper_url: str              # PapersWithCode URL
arxiv_id: str               # arXiv ID
title: str                  # Paper title
abstract: str               # Full abstract
url_abs: str                # arXiv abstract URL
url_pdf: str                # arXiv PDF URL
proceeding: str             # Conference proceeding
authors: list               # List of authors
tasks: list                 # ML tasks
date: datetime              # Publication date
conference: str             # Conference name
methods: list               # Methods used in paper
```

## Mapping Strategy to DAIMO v2.1

### Universal Properties (REUSE - 0% Redundancy Goal)

| PapersWithCode Field | DAIMO Property | Mapping Logic |
|---------------------|----------------|---------------|
| `name` / `title` | `daimo:title` | Direct mapping |
| `description` / `abstract` | `daimo:description` | Direct mapping (truncate abstract if needed) |
| `source_url` / `url_abs` | `daimo:sourceURL` | Paper arXiv URL |
| `repo_url` | `daimo:githubURL` | Direct mapping |
| `collections[].area` | `daimo:task` | Map area to task (CV, NLP, etc.) |
| `framework` | `daimo:library` | Framework name (PyTorch, TensorFlow) |
| `num_papers` (popularity) | `daimo:likes` | Use as popularity metric |
| `authors` | `daimo:creator` | Join authors as string |
| `(constant)` | `daimo:source` | "PapersWithCode" |
| `is_official` / `paper_url` | `daimo:accessLevel` | "official" / "community" |

### PapersWithCode-Specific Properties (NEW - Minimal Addition)

These are unique to academic papers and cannot be mapped to existing properties:

| New Property | Type | Description | Justification |
|-------------|------|-------------|---------------|
| `daimo:arxivId` | `xsd:string` | arXiv identifier | Unique academic identifier |
| `daimo:paper` | `xsd:string` | Associated paper URL | Link to academic paper |
| `daimo:venue` | `xsd:string` | Conference/journal venue | Publication venue |
| `daimo:yearIntroduced` | `xsd:integer` | Year method introduced | Method provenance |
| `daimo:citationCount` | `xsd:integer` | Number of citations | Academic impact metric |
| `daimo:isOfficial` | `xsd:boolean` | Is official implementation | Implementation status |

## Property Reuse Analysis

### ✅ Reusing 10 Universal Properties:
1. `daimo:title` - Method/paper name
2. `daimo:description` - Method/paper description
3. `daimo:sourceURL` - arXiv URL
4. `daimo:githubURL` - Code repository
5. `daimo:task` - Research area (Computer Vision, NLP, etc.)
6. `daimo:library` - Framework (PyTorch, TensorFlow)
7. `daimo:likes` - Popularity (num_papers)
8. `daimo:creator` - Authors
9. `daimo:source` - "PapersWithCode"
10. `daimo:accessLevel` - Official vs community implementation

### ➕ Adding 6 New Properties:
1. `daimo:arxivId` - REQUIRED (academic identifier)
2. `daimo:paper` - REQUIRED (paper reference)
3. `daimo:venue` - REQUIRED (publication venue)
4. `daimo:yearIntroduced` - REQUIRED (temporal metadata)
5. `daimo:citationCount` - OPTIONAL (academic metric)
6. `daimo:isOfficial` - OPTIONAL (implementation quality indicator)

## Ontology Impact

**Before PapersWithCode:**
- Total properties: 34
- Redundancy: 0%

**After PapersWithCode:**
- Total properties: 34 + 6 = 40
- Redundancy: 0% (new properties are unique to academic papers)
- Property increase: +17.6%

**Justification for new properties:**
All 6 new properties are specific to academic papers and have no equivalent in other repositories:
- `arxivId`, `paper`, `venue`, `yearIntroduced` are academic metadata
- `citationCount`, `isOfficial` are unique quality indicators

## Implementation Plan

### 1. Update Ontology (`ontologies/daimo.ttl`)
```turtle
# Academic Paper Properties (PapersWithCode)
daimo:arxivId a owl:DatatypeProperty ;
    rdfs:label "arXiv ID" ;
    rdfs:comment "arXiv identifier for academic papers" ;
    rdfs:domain daimo:AIModel ;
    rdfs:range xsd:string .

daimo:paper a owl:DatatypeProperty ;
    rdfs:label "Associated Paper" ;
    rdfs:comment "URL to the associated academic paper" ;
    rdfs:domain daimo:AIModel ;
    rdfs:range xsd:string .

daimo:venue a owl:DatatypeProperty ;
    rdfs:label "Publication Venue" ;
    rdfs:comment "Conference or journal where the paper was published" ;
    rdfs:domain daimo:AIModel ;
    rdfs:range xsd:string .

daimo:yearIntroduced a owl:DatatypeProperty ;
    rdfs:label "Year Introduced" ;
    rdfs:comment "Year when the method was introduced" ;
    rdfs:domain daimo:AIModel ;
    rdfs:range xsd:integer .

daimo:citationCount a owl:DatatypeProperty ;
    rdfs:label "Citation Count" ;
    rdfs:comment "Number of academic citations" ;
    rdfs:domain daimo:AIModel ;
    rdfs:range xsd:integer .

daimo:isOfficial a owl:DatatypeProperty ;
    rdfs:label "Is Official Implementation" ;
    rdfs:comment "Indicates if this is the official implementation from the paper authors" ;
    rdfs:domain daimo:AIModel ;
    rdfs:range xsd:boolean .
```

### 2. Create Repository (`utils/paperswithcode_repository.py`)
```python
class PapersWithCodeRepository(BaseRepository):
    def fetch_models(self, limit=100):
        # Load from HuggingFace datasets
        # Combine methods + links + papers data
        pass
    
    def map_to_rdf(self, model):
        # Map to universal properties (10)
        # Map to PapersWithCode-specific properties (6)
        pass
```

### 3. Update Notebook
- Add PapersWithCode to repository list (7 total)
- Update SPARQL queries to handle new properties
- Add validation for academic-specific metadata

## Redundancy Verification

### ❌ NOT Creating Redundancy:
- **Academic metadata** (`arxivId`, `paper`, `venue`, `yearIntroduced`) - Unique to papers, no equivalent in HuggingFace, Kaggle, etc.
- **Citation metrics** (`citationCount`) - Different from `likes`/`downloads` (academic vs popular impact)
- **Implementation status** (`isOfficial`) - Different from `accessLevel` (quality indicator vs access permission)

### ✅ Maintaining 0% Redundancy:
- Reusing all applicable universal properties
- Only adding properties with no semantic overlap
- Academic domain requires specialized metadata

## Conclusion

PapersWithCode can be integrated with:
- **10 reused properties** from DAIMO v2.1 (58.8% reuse rate)
- **6 new properties** unique to academic papers (41.2% new)
- **0% redundancy** maintained (academic properties are semantically distinct)
- **Total: 40 properties** in DAIMO v2.2 (17.6% increase from v2.1)

This maintains our goal of minimal redundancy while properly representing the academic domain.
