import re
from typing import Optional
from pathlib import Path
import sqlite3
import logging

logger = logging.getLogger(__name__)

class SQLValidator:
    def __init__(self, omop_db_path: str = "omop_testing/omop_test.db"):
        self.omop_db_path = Path(omop_db_path)
        
    def validate_sql_syntax(self, sql: str) -> Optional[str]:
        """Validación básica de sintaxis SQL"""
        if not sql or sql.strip() == ';':
            return "SQL vacío"
        
        sql_upper = sql.upper()
        
        # Verificar que tenga keywords básicos
        required_keywords = ['SELECT', 'FROM']
        if not all(keyword in sql_upper for keyword in required_keywords):
            return "SQL debe contener SELECT y FROM"
        
        # Verificar operaciones prohibidas
        prohibited = ['CREATE', 'DROP', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'ALTER']
        for op in prohibited:
            if op in sql_upper:
                return f"Operación prohibida: {op}"
        
        # Verificar longitud razonable
        if len(sql) > 5000:
            return "SQL demasiado largo"
        
        # Verificar número excesivo de SELECT anidados
        if sql.count('SELECT') > 20:
            return "Demasiados SELECT anidados"
        
        return None
    
    def clean_generated_sql(self, generated_text: str) -> str:
        """Limpiar el texto generado para extraer solo el SQL"""
        text = generated_text.strip()
        
        # Intentar extraer SQL de bloques de código
        sql_patterns = [
            r'```sql\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'SQL:\s*(.*?)(?:\n\n|\Z)',
        ]
        
        for pattern in sql_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                sql = match.group(1).strip()
                if sql and 'SELECT' in sql.upper():
                    return self._clean_sql_text(sql)
        
        # Si no hay bloques, extraer líneas que parecen SQL
        lines = text.split('\n')
        sql_lines = []
        
        for line in lines:
            line = line.strip()
            # Saltar líneas explicativas
            if any(phrase in line.lower() for phrase in [
                'explanation:', 'the query', 'this sql', 'note:', 'answer:'
            ]):
                continue
            
            # Saltar comentarios largos
            if line.startswith('--') and len(line) > 50:
                continue
                
            # Incluir líneas con keywords SQL
            if any(keyword in line.upper() for keyword in [
                'SELECT', 'FROM', 'WHERE', 'JOIN', 'WITH', 'GROUP', 'ORDER', 'HAVING', 'UNION'
            ]):
                sql_lines.append(line)
            elif sql_lines and line and not line.startswith('--'):
                sql_lines.append(line)
        
        if sql_lines:
            return self._clean_sql_text('\n'.join(sql_lines))
        
        return self._clean_sql_text(text)
    
    def _clean_sql_text(self, sql: str) -> str:
        """Limpiar texto SQL"""
        lines = sql.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Saltar comentarios muy largos
            if line.startswith('--') and len(line) > 80:
                continue
            if line:
                cleaned_lines.append(line)
        
        sql = '\n'.join(cleaned_lines).strip()
        
        # Asegurar que termine con punto y coma
        if sql and not sql.endswith(';'):
            sql += ';'
        
        return sql
    
    def test_sql_execution(self, sql: str, timeout: int = 30) -> dict:
        """Probar la ejecución del SQL en la base de datos OMOP de prueba"""
        result = {
            'executable': False,
            'error': None,
            'execution_time': None,
            'row_count': None,
            'error_type': None
        }
        
        if not self.omop_db_path.exists():
            result['error'] = f"Base de datos OMOP no encontrada: {self.omop_db_path}"
            result['error_type'] = 'DatabaseNotFound'
            return result
        
        try:
            import time
            start_time = time.time()
            
            with sqlite3.connect(self.omop_db_path, timeout=timeout) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                
                if sql.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    result['row_count'] = len(rows)
                else:
                    result['row_count'] = cursor.rowcount
                    
                result['executable'] = True
                result['execution_time'] = time.time() - start_time
                
        except sqlite3.OperationalError as e:
            result['error'] = str(e)
            result['error_type'] = 'OperationalError'
        except sqlite3.DatabaseError as e:
            result['error'] = str(e)
            result['error_type'] = 'DatabaseError'
        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__
            
        return result