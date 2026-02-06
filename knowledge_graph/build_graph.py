"""
Constructor del Grafo de Conocimiento RDF usando la ontología DAIMO.

Este módulo transforma los metadatos recolectados de Hugging Face a un grafo
RDF basado en la ontología DAIMO (PIONERA), permitiendo consultas semánticas
mediante SPARQL.

Mapeo conceptual:
- Modelo HF → daimo:Model (subclase de dcat:Dataset)
- Pipeline tag → tipo de tarea ML
- Licencia → odrl:Policy
- Métricas → mls:ModelEvaluation
- Ejecución → mls:Run

Referencias:
- DAIMO/PIONERA ontology
- ML-Schema (http://www.w3.org/ns/mls)
- DCAT (http://www.w3.org/ns/dcat)
- ODRL (http://www.w3.org/ns/odrl/2/)

Autor: Edmundo Mori
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, XSD
from rdflib.namespace import FOAF, DCTERMS


class DAIMOGraphBuilder:
    """
    Constructor de grafos RDF usando la ontología DAIMO.
    
    Transforma metadatos de modelos a triples RDF siguiendo la estructura
    de la ontología DAIMO/PIONERA.
    """
    
    def __init__(self, ontology_path: str = "ontologies/daimo.ttl"):
        """
        Inicializa el builder con la ontología DAIMO.
        
        Args:
            ontology_path: Ruta al archivo de la ontología
        """
        # Inicializar grafo vacío
        self.graph = Graph()
        
        # Definir namespaces
        self.DAIMO = Namespace("http://purl.org/pionera/daimo#")
        self.MLS = Namespace("http://www.w3.org/ns/mls#")
        self.DCAT = Namespace("http://www.w3.org/ns/dcat#")
        self.ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
        self.SD = Namespace("https://w3id.org/okn/o/sd/")
        self.MLSO = Namespace("http://w3id.org/mlso/")
        self.PROV = Namespace("http://www.w3.org/ns/prov#")
        
        # Bind namespaces al grafo
        self.graph.bind("daimo", self.DAIMO)
        self.graph.bind("mls", self.MLS)
        self.graph.bind("dcat", self.DCAT)
        self.graph.bind("odrl", self.ODRL)
        self.graph.bind("sd", self.SD)
        self.graph.bind("mlso", self.MLSO)
        self.graph.bind("prov", self.PROV)
        self.graph.bind("foaf", FOAF)
        self.graph.bind("dcterms", DCTERMS)
        
        # Cargar ontología base
        self.ontology_path = Path(ontology_path)
        if self.ontology_path.exists():
            print(f"📚 Cargando ontología DAIMO desde: {self.ontology_path}")
            self.graph.parse(str(self.ontology_path), format="turtle")
            print(f"✅ Ontología cargada: {len(self.graph)} triples")
        else:
            print(f"⚠️ Advertencia: No se encontró la ontología en {self.ontology_path}")

    def _normalize_datetime(self, value: Optional[str]) -> Optional[str]:
        """
        Normaliza un string de fecha/hora a formato ISO 8601 válido (con 'T').

        - Acepta valores como "YYYY-MM-DD HH:MM:SS+00:00" y los convierte a
          "YYYY-MM-DDTHH:MM:SS+00:00".
        - Si no puede normalizar, retorna None.
        """
        if not value or not isinstance(value, str):
            return None
        try:
            # Asegurar separador 'T' y zona horaria compatible
            fixed = value.replace(' ', 'T')
            fixed = fixed.replace('Z', '+00:00')
            dt = datetime.fromisoformat(fixed)
            return dt.isoformat()
        except Exception:
            return None
    
    def add_model(self, model_data: Dict) -> URIRef:
        """
        Añade un modelo al grafo RDF.
        
        Args:
            model_data: Diccionario con metadatos del modelo
            
        Returns:
            URIRef del modelo creado
        """
        # Crear URI del modelo (sanitizar el ID)
        model_id = model_data.get("modelId", model_data.get("id", "unknown"))
        model_uri = self._create_model_uri(model_id)
        
        # Tipo: daimo:Model (subclase de dcat:Dataset)
        self.graph.add((model_uri, RDF.type, self.DAIMO.Model))
        self.graph.add((model_uri, RDF.type, self.DCAT.Dataset))
        
        # Propiedades básicas
        if model_id:
            self.graph.add((model_uri, DCTERMS.identifier, Literal(model_id, datatype=XSD.string)))
            self.graph.add((model_uri, DCTERMS.title, Literal(model_id, datatype=XSD.string)))
        
        # Autor/Creador
        author = model_data.get("author")
        if author:
            author_uri = self._create_agent_uri(author)
            self.graph.add((author_uri, RDF.type, FOAF.Agent))
            self.graph.add((author_uri, FOAF.name, Literal(author, datatype=XSD.string)))
            self.graph.add((model_uri, DCTERMS.creator, author_uri))
        
        # Fechas
        created_at = model_data.get("created_at")
        if created_at:
            norm_created = self._normalize_datetime(created_at)
            if norm_created:
                self.graph.add((model_uri, DCTERMS.created, Literal(norm_created, datatype=XSD.dateTime)))
            else:
                # Si no es ISO válido, guardamos como string para evitar errores de parseo
                self.graph.add((model_uri, DCTERMS.created, Literal(str(created_at), datatype=XSD.string)))
        
        last_modified = model_data.get("last_modified")
        if last_modified:
            norm_modified = self._normalize_datetime(last_modified)
            if norm_modified:
                self.graph.add((model_uri, DCTERMS.modified, Literal(norm_modified, datatype=XSD.dateTime)))
            else:
                self.graph.add((model_uri, DCTERMS.modified, Literal(str(last_modified), datatype=XSD.string)))
        
        # Pipeline tag (tipo de tarea ML)
        pipeline_tag = model_data.get("pipeline_tag")
        if pipeline_tag:
            self.graph.add((model_uri, DCTERMS.subject, Literal(pipeline_tag, datatype=XSD.string)))
            # Crear una referencia a la tarea
            task_uri = self._create_task_uri(pipeline_tag)
            self.graph.add((task_uri, RDF.type, self.MLS.Task))
            self.graph.add((task_uri, RDFS.label, Literal(pipeline_tag, datatype=XSD.string)))
        
        # Tags adicionales
        tags = model_data.get("tags", [])
        for tag in tags:
            if isinstance(tag, str):
                self.graph.add((model_uri, self.DCAT.keyword, Literal(tag, datatype=XSD.string)))
        
        # Licencia (ODRL Policy)
        license_name = model_data.get("license")
        if license_name and license_name != "unknown":
            license_uri = self._create_license_uri(license_name)
            self.graph.add((license_uri, RDF.type, self.ODRL.Offer))
            self.graph.add((license_uri, DCTERMS.identifier, Literal(license_name, datatype=XSD.string)))
            self.graph.add((model_uri, self.ODRL.hasPolicy, license_uri))
        
        # Métricas de popularidad (como propiedades adicionales)
        downloads = model_data.get("downloads", 0)
        if downloads:
            self.graph.add((model_uri, self.DAIMO.downloads, Literal(downloads, datatype=XSD.integer)))
        
        likes = model_data.get("likes", 0)
        if likes:
            self.graph.add((model_uri, self.DAIMO.likes, Literal(likes, datatype=XSD.integer)))
        
        # Librería (framework)
        library_name = model_data.get("library_name")
        if library_name:
            self.graph.add((model_uri, self.DAIMO.library, Literal(library_name, datatype=XSD.string)))
        
        # Datasets usados para entrenamiento
        datasets = model_data.get("datasets", [])
        for dataset_name in datasets:
            if isinstance(dataset_name, str):
                dataset_uri = self._create_dataset_uri(dataset_name)
                self.graph.add((dataset_uri, RDF.type, self.DCAT.Dataset))
                self.graph.add((dataset_uri, DCTERMS.identifier, Literal(dataset_name, datatype=XSD.string)))
                self.graph.add((model_uri, self.PROV.wasDerivedFrom, dataset_uri))
        
        # Idiomas
        languages = model_data.get("language", [])
        if isinstance(languages, str):
            languages = [languages]
        for lang in languages:
            if isinstance(lang, str):
                self.graph.add((model_uri, DCTERMS.language, Literal(lang, datatype=XSD.string)))
        
        # === EXTENSIONES NIVEL 1 - CRÍTICO ===
        
        # Arquitectura del modelo
        architectures = model_data.get("architectures")
        if architectures and isinstance(architectures, list):
            for arch_name in architectures:
                if arch_name:
                    arch_uri = self._create_architecture_uri(arch_name)
                    self.graph.add((arch_uri, RDF.type, self.DAIMO.ModelArchitecture))
                    self.graph.add((arch_uri, RDFS.label, Literal(arch_name, datatype=XSD.string)))
                    self.graph.add((model_uri, self.DAIMO.hasArchitecture, arch_uri))
        
        # Tipo de modelo (alternativa si no hay architectures)
        model_type = model_data.get("model_type")
        if model_type and not architectures:
            arch_uri = self._create_architecture_uri(model_type)
            self.graph.add((arch_uri, RDF.type, self.DAIMO.ModelArchitecture))
            self.graph.add((arch_uri, RDFS.label, Literal(model_type, datatype=XSD.string)))
            self.graph.add((model_uri, self.DAIMO.hasArchitecture, arch_uri))
        
        # Control de acceso (gated)
        gated = model_data.get("gated", False)
        if gated:
            access_uri = self._create_access_policy_uri(model_id)
            self.graph.add((access_uri, RDF.type, self.DAIMO.AccessPolicy))
            self.graph.add((access_uri, RDFS.label, Literal("Gated Access", datatype=XSD.string)))
            self.graph.add((model_uri, self.DAIMO.accessControl, access_uri))
            self.graph.add((model_uri, self.DAIMO.requiresApproval, Literal(True, datatype=XSD.boolean)))
        
        # Parámetros del modelo (safetensors)
        safetensors_params = model_data.get("safetensors_parameters")
        if safetensors_params:
            self.graph.add((model_uri, self.DAIMO.parameterCount, Literal(safetensors_params, datatype=XSD.long)))
        
        # === EXTENSIONES NIVEL 2 - IMPORTANTE ===
        
        # Modelo base (fine-tuning)
        base_model = model_data.get("base_model")
        if base_model:
            base_model_uri = self._create_model_uri(base_model)
            self.graph.add((base_model_uri, RDF.type, self.DAIMO.Model))
            self.graph.add((base_model_uri, DCTERMS.identifier, Literal(base_model, datatype=XSD.string)))
            self.graph.add((model_uri, self.DAIMO.fineTunedFrom, base_model_uri))
        
        # Evaluaciones (eval_results)
        eval_results = model_data.get("eval_results")
        if eval_results and isinstance(eval_results, list):
            for eval_data in eval_results:
                if isinstance(eval_data, dict):
                    eval_uri = self._create_evaluation_uri(model_id, eval_data)
                    self.graph.add((eval_uri, RDF.type, self.MLS.ModelEvaluation))
                    
                    # Dataset de evaluación
                    eval_dataset = eval_data.get("dataset", {})
                    if isinstance(eval_dataset, dict):
                        dataset_name = eval_dataset.get("name")
                        if dataset_name:
                            self.graph.add((eval_uri, DCTERMS.description, Literal(f"Evaluated on {dataset_name}", datatype=XSD.string)))
                    
                    # Métricas
                    metrics = eval_data.get("metrics", [])
                    if isinstance(metrics, list):
                        for metric_data in metrics:
                            if isinstance(metric_data, dict):
                                metric_name = metric_data.get("name") or metric_data.get("type")
                                metric_value = metric_data.get("value")
                                if metric_name and metric_value is not None:
                                    metric_uri = self._create_metric_uri(model_id, metric_name)
                                    self.graph.add((metric_uri, RDF.type, self.MLS.EvaluationMeasure))
                                    self.graph.add((metric_uri, RDFS.label, Literal(metric_name, datatype=XSD.string)))
                                    self.graph.add((eval_uri, self.MLS.specifiedBy, metric_uri))
                                    
                                    # Valor de la métrica
                                    try:
                                        self.graph.add((eval_uri, self.MLS.hasValue, Literal(float(metric_value), datatype=XSD.float)))
                                    except (ValueError, TypeError):
                                        self.graph.add((eval_uri, self.MLS.hasValue, Literal(str(metric_value), datatype=XSD.string)))
                    
                    self.graph.add((model_uri, self.MLS.hasQuality, eval_uri))
        
        return model_uri
    
    def build_from_json(self, json_path: str) -> int:
        """
        Construye el grafo desde un archivo JSON de metadatos.
        
        Args:
            json_path: Ruta al archivo JSON con metadatos
            
        Returns:
            Número de modelos añadidos al grafo
        """
        json_file = Path(json_path)
        
        if not json_file.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {json_path}")
        
        print(f"📖 Leyendo metadatos desde: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            models_data = json.load(f)
        
        print(f"🔨 Construyendo grafo RDF para {len(models_data)} modelos...")
        
        models_added = 0
        for model_data in models_data:
            try:
                self.add_model(model_data)
                models_added += 1
            except Exception as e:
                model_id = model_data.get("id", "unknown")
                print(f"⚠️ Error añadiendo modelo {model_id}: {e}")
        
        print(f"✅ Grafo construido: {len(self.graph)} triples totales")
        print(f"📊 Modelos añadidos: {models_added}")
        
        return models_added
    
    def save(self, output_path: str, format: str = "turtle"):
        """
        Guarda el grafo en un archivo.
        
        Args:
            output_path: Ruta del archivo de salida
            format: Formato de serialización (turtle, xml, nt, json-ld)
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Guardando grafo en: {output_file} (formato: {format})")
        
        self.graph.serialize(destination=str(output_file), format=format, encoding='utf-8')
        
        print(f"✅ Grafo guardado exitosamente")
        
        # Estadísticas
        self._print_statistics()
    
    def query(self, sparql_query: str):
        """
        Ejecuta una consulta SPARQL sobre el grafo.
        
        Args:
            sparql_query: Consulta SPARQL
            
        Returns:
            Resultados de la consulta
        """
        return self.graph.query(sparql_query)
    
    def _create_model_uri(self, model_id: str) -> URIRef:
        """Crea URI para un modelo."""
        safe_id = model_id.replace("/", "_").replace(" ", "_")
        return self.DAIMO[f"model/{safe_id}"]
    
    def _create_agent_uri(self, agent_name: str) -> URIRef:
        """Crea URI para un agente (autor/organización)."""
        safe_name = agent_name.replace("/", "_").replace(" ", "_")
        return self.DAIMO[f"agent/{safe_name}"]
    
    def _create_task_uri(self, task_name: str) -> URIRef:
        """Crea URI para una tarea ML."""
        safe_name = task_name.replace("-", "_").replace(" ", "_")
        return self.DAIMO[f"task/{safe_name}"]
    
    def _create_license_uri(self, license_name: str) -> URIRef:
        """Crea URI para una licencia."""
        safe_name = license_name.replace(" ", "_").replace("-", "_")
        return self.DAIMO[f"license/{safe_name}"]
    
    def _create_dataset_uri(self, dataset_name: str) -> URIRef:
        """Crea URI para un dataset."""
        safe_name = dataset_name.replace("/", "_").replace(" ", "_")
        return self.DAIMO[f"dataset/{safe_name}"]
    
    def _create_architecture_uri(self, arch_name: str) -> URIRef:
        """Crea URI para una arquitectura de modelo."""
        safe_name = arch_name.replace(" ", "_").replace("-", "_").replace("/", "_")
        return self.DAIMO[f"architecture/{safe_name}"]
    
    def _create_access_policy_uri(self, model_id: str) -> URIRef:
        """Crea URI para una política de acceso."""
        safe_id = model_id.replace("/", "_").replace(" ", "_")
        return self.DAIMO[f"access_policy/{safe_id}"]
    
    def _create_evaluation_uri(self, model_id: str, eval_data: Dict) -> URIRef:
        """Crea URI para una evaluación."""
        safe_id = model_id.replace("/", "_").replace(" ", "_")
        dataset_name = ""
        if isinstance(eval_data.get("dataset"), dict):
            dataset_name = eval_data["dataset"].get("name", "")
        dataset_part = dataset_name.replace("/", "_").replace(" ", "_") if dataset_name else "eval"
        return self.DAIMO[f"evaluation/{safe_id}/{dataset_part}"]
    
    def _create_metric_uri(self, model_id: str, metric_name: str) -> URIRef:
        """Crea URI para una métrica."""
        safe_id = model_id.replace("/", "_").replace(" ", "_")
        safe_metric = metric_name.replace(" ", "_").replace("-", "_")
        return self.DAIMO[f"metric/{safe_id}/{safe_metric}"]
    
    def _print_statistics(self):
        """Imprime estadísticas del grafo."""
        # Contar tipos de entidades
        models_query = """
        PREFIX daimo: <http://purl.org/pionera/daimo#>
        SELECT (COUNT(?model) as ?count)
        WHERE { ?model a daimo:Model }
        """
        
        result = list(self.graph.query(models_query))
        num_models = result[0][0] if result else 0
        
        print(f"\n📈 Estadísticas del grafo:")
        print(f"  Total de triples: {len(self.graph)}")
        print(f"  Modelos: {num_models}")


def main():
    """Función principal para uso desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Construir grafo RDF desde metadatos de modelos"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/hf_models.json",
        help="Archivo JSON de entrada con metadatos"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/ai_models_multi_repo.ttl",
        help="Archivo de salida del grafo RDF"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="turtle",
        choices=["turtle", "xml", "nt", "json-ld"],
        help="Formato de serialización RDF"
    )
    parser.add_argument(
        "--ontology",
        type=str,
        default="ontologies/daimo.ttl",
        help="Ruta a la ontología DAIMO"
    )
    
    args = parser.parse_args()
    
    # Construir grafo
    builder = DAIMOGraphBuilder(ontology_path=args.ontology)
    builder.build_from_json(args.input)
    builder.save(args.output, format=args.format)


if __name__ == "__main__":
    main()
