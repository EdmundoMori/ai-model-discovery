# Ontología DAIMO

Este directorio contiene la ontología **DAIMO** (basada en **PIONERA**) que se utiliza para modelar los metadatos de modelos de IA en el grafo de conocimiento.

## Archivo Principal

- **`daimo.ttl`**: Ontología completa en formato Turtle

## Descripción

DAIMO es una ontología diseñada para describir modelos de aprendizaje automático y sus características, incluyendo:

### Clases Principales

- **`daimo:Model`**: Modelo de IA (subclase de `dcat:Dataset`)
- **`mls:Algorithm`**: Algoritmo implementado
- **`mls:Task`**: Tarea de ML (clasificación, regresión, etc.)
- **`mls:Run`**: Ejecución de un modelo
- **`mls:ModelEvaluation`**: Evaluación con métricas
- **`mls:HyperParameter`**: Hiperparámetros del modelo
- **`odrl:Policy`**: Políticas de uso y licencias

### Propiedades Principales

#### Propiedades de Modelo
- `dcterms:identifier`: Identificador único
- `dcterms:title`: Nombre del modelo
- `dcterms:creator`: Autor/organización
- `dcterms:created`: Fecha de creación
- `dcterms:modified`: Última modificación
- `dcterms:subject`: Tema/tarea
- `dcterms:language`: Idiomas soportados

#### Propiedades Específicas de ML
- `mls:implements`: Algoritmo implementado
- `mls:hasOutput`: Resultados/evaluaciones
- `mls:hasHyperParameter`: Hiperparámetros
- `daimo:downloads`: Número de descargas
- `daimo:likes`: Número de likes
- `daimo:library`: Framework/librería

#### Propiedades de Políticas
- `odrl:hasPolicy`: Licencia o política de uso
- `odrl:permission`: Permisos
- `odrl:prohibition`: Prohibiciones
- `odrl:obligation`: Obligaciones

#### Propiedades de Provenance
- `prov:wasDerivedFrom`: Modelo base o dataset usado
- `dcat:distribution`: Distribuciones disponibles

## Namespaces Utilizados

```turtle
@prefix daimo: <http://purl.org/pionera/daimo#> .
@prefix mls: <http://www.w3.org/ns/mls#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .
@prefix sd: <https://w3id.org/okn/o/sd/> .
@prefix mlso: <http://w3id.org/mlso/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
```

## Estándares y Referencias

La ontología DAIMO integra y extiende los siguientes vocabularios estándar:

- **ML-Schema (MLS)**: http://www.w3.org/ns/mls
- **DCAT**: http://www.w3.org/ns/dcat
- **ODRL**: http://www.w3.org/ns/odrl/2/
- **PROV-O**: http://www.w3.org/ns/prov
- **Dublin Core**: http://purl.org/dc/terms/
- **FOAF**: http://xmlns.com/foaf/0.1/

## Ejemplo de Uso

```python
from rdflib import Graph, Namespace

# Cargar la ontología
g = Graph()
g.parse("ontologies/daimo.ttl", format="turtle")

# Definir namespaces
DAIMO = Namespace("http://purl.org/pionera/daimo#")
MLS = Namespace("http://www.w3.org/ns/mls#")

# Consultar clases
query = """
PREFIX daimo: <http://purl.org/pionera/daimo#>
SELECT ?class WHERE { ?class a owl:Class }
"""

results = g.query(query)
for row in results:
    print(row.class)
```

## Extensiones Futuras

Para fases posteriores del proyecto, se planea extender la ontología con:

1. **Métricas detalladas**: F1-score, accuracy, precision, recall
2. **Arquitecturas específicas**: Transformers, CNNs, RNNs
3. **Requisitos computacionales**: GPU, memoria, tiempo de inferencia
4. **Fairness y bias**: Métricas de sesgo y equidad
5. **Explicabilidad**: SHAP, LIME, attention maps

## Validación

La ontología puede ser validada usando:

- **Protégé**: Editor y razonador OWL
- **SHACL**: Shapes en `daimo-ontology/shacl-shapes/`
- **Pellet/HermiT**: Razonadores OWL

## Mantenimiento

La ontología es mantenida por:

- **Edmundo Mori Orrillo** (edmundo.mori.orrillo@upm.es)
- **Jiayun Liu** (jiayun.liu@upm.es)

Proyecto PIONERA - Universidad Politécnica de Madrid
