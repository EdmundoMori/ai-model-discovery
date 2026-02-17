"""
SPARQL Error Corrector - Soluciones Generalizadas

Este módulo implementa correcciones automáticas para errores comunes en SPARQL
generado por LLMs, basado en análisis de 18 errores del evaluation pipeline.
"""
import re
from typing import Optional, Dict, List, Tuple


class SPARQLErrorCorrector:
    """
    Corrector automático de errores comunes en SPARQL generado por LLMs.
    
    Errores corregidos:
    1. Lowercase 'as' en agregaciones → Uppercase 'AS' (11 errores)
    2. Propiedades incorrectas → Mappings correctos (7 errores) 
    3. Estructura de licencias incorrecta
    """
    
    # Mapeo de propiedades incorrectas a correctas
    PROPERTY_CORRECTIONS = {
        # Licencias: usar estructura ODRL completa
        'daimo:license': {
            'pattern': r'daimo:license\s+\?(\w+)\s*\.',
            'replacement': r'odrl:hasPolicy ?policy .\n  ?policy dcterms:identifier ?\1 .',
            'required_prefixes': ['odrl: <http://www.w3.org/ns/odrl/2/>']
        },
        
        # Implementación: usar estructura MLS completa  
        'daimo:implementation': {
            'pattern': r'(\?model[^\n]+)daimo:implementation\s+\?(\w+)\s*\.',
            'replacement': r'\1mls:implements ?impl .\n  ?impl mls:hasHyperParameter ?\2 .',
            'required_prefixes': ['mls: <http://www.w3.org/ns/mls#>']
        }
    }
    
    def __init__(self):
        self.corrections_applied = []
        self.warnings = []
    
    def correct_sparql(self, sparql: str) -> Tuple[str, Dict]:
        """
        Aplica todas las correcciones al SPARQL.
        
        Args:
            sparql: Query SPARQL original
            
        Returns:
            Tuple[str, Dict]: (sparql_corregido, metadata)
        """
        self.corrections_applied = []
        self.warnings = []
        
        original_sparql = sparql
        
        # Corrección 1: Uppercase AS en agregaciones (CRÍTICO)
        sparql = self._fix_aggregation_as(sparql)
        
        # Corrección 2: Paréntesis y llaves balanceados (CRÍTICO)
        sparql = self._fix_balanced_delimiters(sparql)
        
        # Corrección 3: ORDER BY/GROUP BY sin variables (CRÍTICO)
        sparql = self._fix_order_group_by_variables(sparql)
        
        # Corrección 4: Propiedades incorrectas
        sparql = self._fix_property_mappings(sparql)
        
        # Corrección 5: Filtros de licencia
        sparql = self._fix_license_filters(sparql)
        
        # Corrección 6: Doble llaves {{ }}
        sparql = self._fix_double_braces(sparql)
        
        # Corrección 7: Limpieza final
        sparql = self._final_cleanup(sparql)
        
        metadata = {
            'original_sparql': original_sparql,
            'corrections_applied': self.corrections_applied,
            'warnings': self.warnings,
            'was_modified': sparql != original_sparql
        }
        
        return sparql, metadata
    
    def _fix_aggregation_as(self, sparql: str) -> str:
        """
        Corrige lowercase 'as' a uppercase 'AS' en agregaciones.
        
        Patrón detectado: (COUNT(?x) as ?y) → (COUNT(?x) AS ?y)
        Afecta: 11/18 errores (61% de errores)
        
        También corrige variables faltantes después de 'as': (COUNT(?x) as ) → Eliminar el 'as' huérfano
        """
        original = sparql
        
        # PASO 1: Corregir 'as' minúscula a 'AS' mayúscula
        # Patrón: (FUNCION(?var) as ?resultado)
        pattern_lowercase = r'\(((COUNT|AVG|SUM|MIN|MAX|GROUP_CONCAT)\([^)]+\))\s+as\s+(\?\w+)\)'
        
        def replace_as(match):
            """Reemplaza 'as' minúscula con 'AS' mayúscula preservando todo lo demás"""
            full_match = match.group(0)
            aggregation = match.group(1)  # COUNT(?var) o similar
            variable = match.group(3)  # ?resultado
            return f'({aggregation} AS {variable})'
        
        sparql = re.sub(pattern_lowercase, replace_as, sparql, flags=re.IGNORECASE)
        
        # PASO 2: Detectar y corregir 'as' sin variable (bug de elimina variable)
        # Patrón: (COUNT(?x) as ) - falta la variable después de 'as'
        pattern_missing_var = r'\(((COUNT|AVG|SUM|MIN|MAX|GROUP_CONCAT)\([^)]+\))\s+(?:as|AS)\s*\)'
        
        # Buscar todas las ocurrencias
        matches_missing = list(re.finditer(pattern_missing_var, sparql, re.IGNORECASE))
        
        if matches_missing:
            # Para cada agregación sin variable, generar una variable automáticamente
            for i, match in enumerate(reversed(matches_missing)):  # Reverso para no desplazar índices
                aggregation_full = match.group(1)  # COUNT(?model)
                func_name = match.group(2).lower()  # count, avg, sum, etc.
                
                # Extraer variable de entrada
                var_match = re.search(r'\?(\w+)', aggregation_full)
                if var_match:
                    input_var = var_match.group(1)  # model, downloads, etc.
                    
                    # Generar variable de salida basada en función y variable
                    if func_name == 'count':
                        output_var = f'?{input_var}Count'
                    elif func_name == 'avg':
                        output_var = f'?avg{input_var.capitalize()}'
                    elif func_name == 'sum':
                        output_var = f'?total{input_var.capitalize()}'
                    elif func_name == 'max':
                        output_var = f'?max{input_var.capitalize()}'
                    elif func_name == 'min':
                        output_var = f'?min{input_var.capitalize()}'
                    else:
                        output_var = f'?result{i+1}'
                else:
                    # Sin variable de entrada, usar nombre genérico
                    output_var = f'?result{i+1}'
                
                # Reemplazar (FUNC(?var) as ) con (FUNC(?var) AS ?varFunc)
                old_text = match.group(0)
                new_text = f'({aggregation_full} AS {output_var})'
                
                sparql = sparql[:match.start()] + new_text + sparql[match.end():]
            
            self.corrections_applied.append({
                'type': 'aggregation_missing_variable',
                'count': len(matches_missing),
                'impact': 'critical',
                'error_prevented': 'Expected SelectQuery, found \'(\' - Variables restauradas',
            })
        
        # PASO 3: Verificar si hubo cambios en lowercase 'as'
        if sparql != original and not matches_missing:
            num_replacements = len(re.findall(pattern_lowercase, original, re.IGNORECASE))
            self.corrections_applied.append({
                'type': 'aggregation_as_uppercase',
                'count': num_replacements,
                'impact': 'high',
                'error_prevented': 'Expected SelectQuery, found \'(\'',
            })
        
        return sparql
    
    def _fix_balanced_delimiters(self, sparql: str) -> str:
        """
        Corrige paréntesis y llaves desbalanceados.
        
        CRÍTICO: Errores de sintaxis por delimitadores desbalanceados.
        """
        original = sparql
        
        # 1. Paréntesis desbalanceados
        open_paren = sparql.count('(')
        close_paren = sparql.count(')')
        
        if open_paren != close_paren:
            diff = open_paren - close_paren
            
            if diff > 0:
                # Faltan paréntesis de cierre
                # Agregar al final de la query
                sparql = sparql.rstrip() + ')' * diff
                
                self.corrections_applied.append({
                    'type': 'parentheses_balanced',
                    'added': diff,
                    'impact': 'critical',
                    'error_prevented': 'Syntax error: unbalanced parentheses',
                })
            else:
                # Sobran paréntesis de cierre - eliminar los últimos
                for _ in range(abs(diff)):
                    last_paren = sparql.rfind(')')
                    if last_paren > 0:
                        sparql = sparql[:last_paren] + sparql[last_paren+1:]
                
                self.corrections_applied.append({
                    'type': 'parentheses_balanced',
                    'removed': abs(diff),
                    'impact': 'critical',
                    'error_prevented': 'Syntax error: unbalanced parentheses',
                })
        
        # 2. Llaves desbalanceadas
        open_brace = sparql.count('{')
        close_brace = sparql.count('}')
        
        if open_brace != close_brace:
            diff = open_brace - close_brace
            
            if diff > 0:
                # Faltan llaves de cierre
                # Agregar antes de LIMIT/ORDER BY o al final
                insert_pos = len(sparql)
                for keyword in ['LIMIT', 'ORDER BY', 'GROUP BY']:
                    match = re.search(rf'\b{keyword}\b', sparql, re.IGNORECASE)
                    if match:
                        insert_pos = min(insert_pos, match.start())
                
                closing = '\n' + '}' * diff + '\n'
                sparql = sparql[:insert_pos].rstrip() + closing + sparql[insert_pos:]
                
                self.corrections_applied.append({
                    'type': 'braces_balanced',
                    'added': diff,
                    'impact': 'critical',
                    'error_prevented': 'Syntax error: unbalanced braces',
                })
            else:
                # Sobran llaves de cierre - eliminar las últimas
                for _ in range(abs(diff)):
                    last_brace = sparql.rfind('}')
                    if last_brace > 0:
                        sparql = sparql[:last_brace] + sparql[last_brace+1:]
                
                self.corrections_applied.append({
                    'type': 'braces_balanced',
                    'removed': abs(diff),
                    'impact': 'critical',
                    'error_prevented': 'Syntax error: unbalanced braces',
                })
        
        return sparql
    
    def _fix_order_group_by_variables(self, sparql: str) -> str:
        """
        Corrige ORDER BY y GROUP BY con variables faltantes.
        
        Patrón detectado: ORDER BY DESC( ) o GROUP BY
        """
        original = sparql
        
        # 1. ORDER BY sin variable: ORDER BY DESC( ) o ORDER BY ASC( )
        pattern_order_empty = r'ORDER\s+BY\s+(DESC|ASC)?\s*\(\s*\)'
        
        if re.search(pattern_order_empty, sparql, re.IGNORECASE):
            # Buscar agregaciones en SELECT para usar la primera
            select_match = re.search(r'SELECT\s+(.+?)\s+WHERE', sparql, re.DOTALL | re.IGNORECASE)
            if select_match:
                select_clause = select_match.group(1)
                
                # Buscar primera agregación o variable
                agg_match = re.search(r'\((?:COUNT|AVG|SUM|MAX|MIN)\([^)]+\)\s+AS\s+(\?\w+)\)', select_clause, re.IGNORECASE)
                
                if agg_match:
                    order_var = agg_match.group(1)
                    
                    # Reemplazar ORDER BY vacío con variable
                    sparql = re.sub(
                        pattern_order_empty,
                        rf'ORDER BY DESC({order_var})',
                        sparql,
                        flags=re.IGNORECASE
                    )
                    
                    self.corrections_applied.append({
                        'type': 'order_by_variable_added',
                        'variable': order_var,
                        'impact': 'critical',
                        'error_prevented': 'Syntax error: ORDER BY without variable',
                    })
                else:
                    # No hay agregación, usar primera variable
                    var_match = re.search(r'(\?\w+)', select_clause)
                    if var_match:
                        order_var = var_match.group(1)
                        sparql = re.sub(
                            pattern_order_empty,
                            rf'ORDER BY {order_var}',
                            sparql,
                            flags=re.IGNORECASE
                        )
                        
                        self.corrections_applied.append({
                            'type': 'order_by_variable_added',
                            'variable': order_var,
                            'impact': 'critical',
                            'error_prevented': 'Syntax error: ORDER BY without variable',
                        })
        
        # 2. GROUP BY sin variable pero con agregación
        if re.search(r'\bGROUP\s+BY\s*$', sparql, re.IGNORECASE | re.MULTILINE):
            # Buscar variable no agregada en SELECT
            select_match = re.search(r'SELECT\s+(.+?)\s+WHERE', sparql, re.DOTALL | re.IGNORECASE)
            if select_match:
                select_clause = select_match.group(1)
                
                # Buscar variable simple (no agregación)
                simple_vars = re.findall(r'(\?\w+)(?!\s+AS\s+\?\w+)', select_clause)
                
                if simple_vars:
                    group_var = simple_vars[0]
                    sparql = re.sub(
                        r'GROUP\s+BY\s*$',
                        f'GROUP BY {group_var}',
                        sparql,
                        flags=re.IGNORECASE | re.MULTILINE
                    )
                    
                    self.corrections_applied.append({
                        'type': 'group_by_variable_added',
                        'variable': group_var,
                        'impact': 'critical',
                        'error_prevented': 'Syntax error: GROUP BY without variable',
                    })
        
        return sparql
    
    def _final_cleanup(self, sparql: str) -> str:
        """
        Limpieza final: espacios, líneas vacías, formato.
        """
        # Eliminar múltiples espacios
        sparql = re.sub(r' {2,}', ' ', sparql)
        
        # Eliminar múltiples líneas vacías
        sparql = re.sub(r'\n{3,}', '\n\n', sparql)
        
        # Asegurar que PREFIX tienen salto de línea
        sparql = re.sub(r'(PREFIX[^\n]+)(\s*)PREFIX', r'\1\n\2PREFIX', sparql)
        
        # Limpiar espacios al inicio/final
        sparql = sparql.strip()
        
        return sparql
    
    def _fix_property_mappings(self, sparql: str) -> str:
        """
        Corrige propiedades incorrectas según ontología.
        
        Afecta: 7/18 errores (39% de errores)
        """
        corrected_sparql = sparql
        
        for incorrect_prop, correction_info in self.PROPERTY_CORRECTIONS.items():
            pattern = correction_info['pattern']
            replacement = correction_info['replacement']
            required_prefixes = correction_info['required_prefixes']
            
            if re.search(pattern, corrected_sparql):
                # Aplicar corrección
                corrected_sparql = re.sub(pattern, replacement, corrected_sparql)
                
                # Añadir prefijos necesarios
                for prefix in required_prefixes:
                    prefix_name = prefix.split(':')[0]
                    if f'PREFIX {prefix}' not in corrected_sparql:
                        # Insertar después de otros PREFIX
                        corrected_sparql = re.sub(
                            r'(PREFIX[^\n]+\n)',
                            r'\1PREFIX ' + prefix + '\n',
                            corrected_sparql,
                            count=1
                        )
                
                self.corrections_applied.append({
                    'type': 'property_mapping',
                    'incorrect_property': incorrect_prop,
                    'correction': replacement,
                    'impact': 'high',
                    'error_prevented': 'Unknown error (wrong property path)',
                })
        
        return corrected_sparql
    
    def _fix_license_filters(self, sparql: str) -> str:
        """
        Corrige filtros de licencia para usar estructura ODRL.
        
        Patrón incorrecto: FILTER(CONTAINS(LCASE(str(?license)), "mit"))
        Patrón correcto: ?policy dcterms:identifier "mit"^^xsd:string
        """
        # Detectar filtros de licencia incorrectos
        license_filter_pattern = r'FILTER\s*\(\s*CONTAINS\s*\(\s*LCASE\s*\(\s*str\s*\(\s*\?license\s*\)\s*\)\s*,\s*"([^"]+)"\s*\)\s*\)'
        
        match = re.search(license_filter_pattern, sparql, re.IGNORECASE)
        if match:
            license_value = match.group(1)
            
            # Verificar si ya usa estructura ODRL
            if 'odrl:hasPolicy' in sparql:
                # Ya tiene estructura correcta, solo reemplazar filtro
                corrected = re.sub(
                    license_filter_pattern,
                    f'# License filter moved to WHERE clause',
                    sparql,
                    flags=re.IGNORECASE
                )
                
                # Asegurar que existe la cláusula de identifer
                if 'dcterms:identifier' not in corrected:
                    corrected = corrected.replace(
                        'odrl:hasPolicy ?policy .',
                        f'odrl:hasPolicy ?policy .\n  ?policy dcterms:identifier "{license_value}"^^xsd:string .'
                    )
                
                self.corrections_applied.append({
                    'type': 'license_filter_to_where',
                    'license': license_value,
                    'impact': 'medium',
                })
                
                return corrected
        
        return sparql
    
    def _fix_double_braces(self, sparql: str) -> str:
        """
        Corrige dobles llaves {{ }} que pueden causar problemas.
        
        Algunas veces el LLM genera {{ }} por formateo de strings.
        """
        if '{{' in sparql:
            corrected = sparql.replace('{{', '{').replace('}}', '}')
            
            if corrected != sparql:
                self.corrections_applied.append({
                    'type': 'double_braces_removed',
                    'impact': 'low',
                })
            
            return corrected
        
        return sparql
    
    def validate_syntax(self, sparql: str) -> Tuple[bool, Optional[str]]:
        """
        Valida sintaxis básica del SPARQL.
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Validaciones básicas
        errors = []
        
        # 1. Paréntesis balanceados
        if sparql.count('(') != sparql.count(')'):
            errors.append("Unbalanced parentheses")
        
        # 2. Llaves balanceadas
        if sparql.count('{') != sparql.count('}'):
            errors.append("Unbalanced braces")
        
        # 3. SELECT presente
        if not re.search(r'\bSELECT\b', sparql, re.IGNORECASE):
            errors.append("Missing SELECT clause")
        
        # 4. WHERE presente (o estructura valid sin WHERE)
        if not re.search(r'\bWHERE\b', sparql, re.IGNORECASE):
            if '{' not in sparql:
                errors.append("Missing WHERE clause")
        
        # 5. Variables en SELECT deben estar en WHERE
        select_vars = re.findall(r'\?(\w+)', sparql.split('WHERE')[0])
        where_clause = sparql.split('WHERE')[-1] if 'WHERE' in sparql.upper() else ''
        where_vars = re.findall(r'\?(\w+)', where_clause)
        
        for var in select_vars:
            if var not in where_vars and not var.startswith('_'):
                self.warnings.append(f"Variable ?{var} in SELECT not found in WHERE")
        
        if errors:
            return False, '; '.join(errors)
        
        return True, None


def apply_error_corrections(sparql: str, enable_logging: bool = True) -> Dict:
    """
    Función de conveniencia para aplicar correcciones.
    
    Args:
        sparql: Query SPARQL a corregir
        enable_logging: Si True, imprime correcciones aplicadas
        
    Returns:
        Dict con sparql corregido y metadata
    """
    corrector = SPARQLErrorCorrector()
    corrected_sparql, metadata = corrector.correct_sparql(sparql)
    
    # Validar sintaxis
    is_valid, validation_error = corrector.validate_syntax(corrected_sparql)
    metadata['is_valid'] = is_valid
    metadata['validation_error'] = validation_error
    
    if enable_logging and metadata['corrections_applied']:
        print(f"✅ Applied {len(metadata['corrections_applied'])} corrections:")
        for correction in metadata['corrections_applied']:
            print(f"  - {correction['type']}: {correction.get('error_prevented', 'N/A')}")
        
        if metadata['warnings']:
            print(f"⚠️  {len(metadata['warnings'])} warnings:")
            for warning in metadata['warnings']:
                print(f"  - {warning}")
    
    return {
        'sparql': corrected_sparql,
        'metadata': metadata
    }


# Ejemplo de uso
if __name__ == '__main__':
    # Ejemplo 1: Corrección de agregación
    faulty_sparql_1 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    SELECT ?library (COUNT(?model) as ?count)
    WHERE {
      ?model a daimo:Model ;
             daimo:library ?library .
    }
    GROUP BY ?library
    """
    
    print("=" * 80)
    print("Ejemplo 1: Agregación con 'as' minúscula")
    print("=" * 80)
    result = apply_error_corrections(faulty_sparql_1)
    print(f"\n✅ Corregido:\n{result['sparql']}")
    
    # Ejemplo 2: Corrección de propiedad de licencia
    faulty_sparql_2 = """
    PREFIX daimo: <http://purl.org/pionera/daimo#>
    SELECT ?model WHERE {
      ?model a daimo:Model ;
             daimo:license ?license .
      FILTER(CONTAINS(LCASE(str(?license)), "mit"))
    }
    """
    
    print("\n" + "=" * 80)
    print("Ejemplo 2: Propiedad de licencia incorrecta")
    print("=" * 80)
    result = apply_error_corrections(faulty_sparql_2)
    print(f"\n✅ Corregido:\n{result['sparql']}")
