"""
SPARQL Query Validator
Valida sintaxis y estructura de queries SPARQL generadas
"""

import re
from typing import Dict, List, Optional
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery


class SPARQLValidator:
    """Valida queries SPARQL antes de ejecutarlas"""
    
    REQUIRED_PATTERNS = {
        'prefix': r'PREFIX\s+\w+:\s+<[^>]+>',
        'select': r'SELECT\s+',
        'where': r'WHERE\s*\{',
        'closing_brace': r'\}'
    }
    
    RECOMMENDED_PATTERNS = {
        'daimo_prefix': r'PREFIX daimo:',
        'aimodel_filter': r'daimo:AIModel',
        'limit': r'LIMIT\s+\d+'
    }
    
    def __init__(self, test_graph: Optional[Graph] = None):
        """
        Inicializa el validador
        
        Args:
            test_graph: Grafo RDF opcional para validar ejecución de queries
        """
        self.errors = []
        self.warnings = []
        self.test_graph = test_graph
    
    def validate(self, sparql_query: str) -> Dict[str, any]:
        """
        Valida una query SPARQL
        
        Args:
            sparql_query: Query SPARQL a validar
            
        Returns:
            Dict con 'valid' (bool), 'errors' (list), 'warnings' (list)
        """
        self.errors = []
        self.warnings = []
        
        if not sparql_query or not sparql_query.strip():
            self.errors.append("Empty query")
            return self._build_result()
        
        # Validaciones obligatorias
        self._check_required_patterns(sparql_query)
        self._check_balanced_braces(sparql_query)
        self._check_dangerous_patterns(sparql_query)
        self._check_syntax_with_parser(sparql_query)
        
        # Validar ejecución si hay grafo de prueba
        if self.test_graph and len(self.errors) == 0:
            self._check_executability(sparql_query)
        
        # Validaciones recomendadas
        self._check_recommended_patterns(sparql_query)
        
        return self._build_result()
    
    def _check_required_patterns(self, query: str):
        """Verifica patrones obligatorios en la query"""
        for name, pattern in self.REQUIRED_PATTERNS.items():
            if not re.search(pattern, query, re.IGNORECASE):
                self.errors.append(f"Missing required pattern: {name}")
    
    def _check_balanced_braces(self, query: str):
        """Verifica que las llaves estén balanceadas"""
        open_count = query.count('{')
        close_count = query.count('}')
        
        if open_count != close_count:
            self.errors.append(f"Unbalanced braces: {open_count} open, {close_count} close")
    
    def _check_dangerous_patterns(self, query: str):
        """Detecta patrones potencialmente peligrosos"""
        # Evitar DELETE, INSERT, DROP
        dangerous_ops = ['DELETE', 'INSERT', 'DROP', 'CLEAR', 'CREATE']
        for op in dangerous_ops:
            if re.search(rf'\b{op}\b', query, re.IGNORECASE):
                self.errors.append(f"Dangerous operation detected: {op}")
        
        # Verificar LIMIT razonable
        limit_match = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
        if limit_match:
            limit_value = int(limit_match.group(1))
            if limit_value > 100:
                self.warnings.append(f"Very high LIMIT value: {limit_value}")
    
    def _check_recommended_patterns(self, query: str):
        """Verifica patrones recomendados"""
        for name, pattern in self.RECOMMENDED_PATTERNS.items():
            if not re.search(pattern, query, re.IGNORECASE):
                self.warnings.append(f"Missing recommended pattern: {name}")
    
    def _check_syntax_with_parser(self, query: str):
        """Valida sintaxis usando el parser de RDFlib"""
        try:
            prepareQuery(query)
        except Exception as e:
            error_msg = str(e)
            # Extraer solo el mensaje relevante
            if "Expected" in error_msg:
                error_msg = error_msg.split('\n')[0]
            self.errors.append(f"SPARQL syntax error: {error_msg}")
    
    def _check_executability(self, query: str):
        """Intenta ejecutar la query contra el grafo de prueba"""
        try:
            # Intentar ejecutar la query
            results = list(self.test_graph.query(query))
            # Si se ejecuta correctamente, agregar información
            if len(results) == 0:
                self.warnings.append("Query executes but returns no results")
        except Exception as e:
            error_msg = str(e)
            # Limpiar mensaje de error
            if "Expected" in error_msg:
                error_msg = error_msg.split('\n')[0]
            self.errors.append(f"Execution error: {error_msg}")
    
    def _build_result(self) -> Dict:
        """Construye el resultado de la validación"""
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }
    
    def format_report(self, validation_result: Dict) -> str:
        """
        Formatea un reporte legible de la validación
        
        Args:
            validation_result: Resultado de validate()
            
        Returns:
            String con el reporte formateado
        """
        lines = []
        
        if validation_result['valid']:
            lines.append("✅ Query is valid")
        else:
            lines.append("❌ Query is INVALID")
        
        if validation_result['errors']:
            lines.append(f"\n🚨 Errors ({len(validation_result['errors'])}):")
            for error in validation_result['errors']:
                lines.append(f"   - {error}")
        
        if validation_result['warnings']:
            lines.append(f"\n⚠️  Warnings ({len(validation_result['warnings'])}):")
            for warning in validation_result['warnings']:
                lines.append(f"   - {warning}")
        
        return '\n'.join(lines)


def validate_sparql(query: str) -> Dict:
    """
    Helper function para validación rápida
    
    Args:
        query: SPARQL query string
        
    Returns:
        Validation result dict
    """
    validator = SPARQLValidator()
    return validator.validate(query)
