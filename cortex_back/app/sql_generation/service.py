import logging
from typing import List, Dict, Optional
from pathlib import Path

from .models import SQLGenerationRequest, SQLGenerationResponse, SimilarExample, MedicalTerm
from .ollama_client import OllamaClient
from .sql_validator import SQLValidator
from .rag_retriever import RAGRetriever

logger = logging.getLogger(__name__)

class SQLGenerationService:
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model_name: str = "deepseek-coder-v2:16b-lite-instruct-q4_K_M",
        dataset_path: str = "data/text2sql_epi_dataset_omop.xlsx",
        omop_db_path: str = "omop_testing/omop_complete.db",
        max_attempts: int = 3,
        timeout: int = 180
    ):
        self.ollama_client = OllamaClient(ollama_url)
        self.model_name = model_name
        self.sql_validator = SQLValidator(omop_db_path)
        self.rag_retriever = RAGRetriever(dataset_path)
        self.max_attempts = max_attempts
        self.timeout = timeout
        
        # Schema OMOP (cargar desde archivo si existe)
        schema_path = Path("omop_schema_stub.txt")
        if schema_path.exists():
            with open(schema_path, "r") as f:
                self.omop_schema = f.read()
        else:
            self.omop_schema = "OMOP CDM v5.3 schema not available"
    
    def generate_sql(self, request: SQLGenerationRequest) -> SQLGenerationResponse:
        """Generar SQL desde lenguaje natural"""
        
        # Verificar que Ollama esté funcionando
        if not self.ollama_client.is_ollama_running():
            return SQLGenerationResponse(
                question=request.question,
                generated_sql="",
                is_executable=False,
                error_message="Ollama no está ejecutándose. Asegúrate de que esté iniciado.",
                attempts_count=0
            )
        
        # Verificar que el modelo esté disponible
        if not self.ollama_client.check_model_availability(self.model_name):
            return SQLGenerationResponse(
                question=request.question,
                generated_sql="",
                is_executable=False,
                error_message=f"Modelo {self.model_name} no está disponible en Ollama",
                attempts_count=0
            )
        
        # Obtener ejemplo similar del RAG
        similar_examples = self.rag_retriever.get_similar_examples(request.question, k=1)
        similar_example = similar_examples[0] if similar_examples else None
        
        # Generar SQL con corrección iterativa
        attempts = []
        current_sql = None
        error_context = ""
        
        for attempt in range(self.max_attempts):
            prompt = self._create_prompt(
                question=request.question,
                medical_terms=request.medical_terms,
                similar_example=similar_example,
                iteration=attempt + 1,
                previous_sql=current_sql,
                error_msg=error_context
            )
            
            # Generar SQL con Ollama
            generated_text = self.ollama_client.generate(
                model_name=self.model_name,
                prompt=prompt,
                temperature=0.05,
                max_tokens=700,
                timeout=self.timeout // self.max_attempts
            )
            
            if not generated_text:
                attempts.append({
                    'iteration': attempt + 1,
                    'sql': "",
                    'executable': False,
                    'error': "No se pudo generar respuesta del modelo",
                    'error_type': 'GenerationError'
                })
                break
            
            # Limpiar y validar SQL
            current_sql = self.sql_validator.clean_generated_sql(generated_text)
            
            # Validación sintáctica básica
            syntax_error = self.sql_validator.validate_sql_syntax(current_sql)
            if syntax_error:
                attempts.append({
                    'iteration': attempt + 1,
                    'sql': current_sql,
                    'executable': False,
                    'error': f"Error de sintaxis: {syntax_error}",
                    'error_type': 'SyntaxError'
                })
                error_context = syntax_error
                continue
            
            # Probar ejecución en base de datos
            exec_result = self.sql_validator.test_sql_execution(current_sql)
            
            attempts.append({
                'iteration': attempt + 1,
                'sql': current_sql,
                'executable': exec_result['executable'],
                'error': exec_result['error'],
                'error_type': exec_result['error_type']
            })
            
            # Si es ejecutable, terminar
            if exec_result['executable']:
                break
            
            # Preparar contexto de error para siguiente iteración
            error_context = exec_result['error'] if exec_result['error'] else "Error desconocido"
            if len(error_context) > 150:
                error_context = error_context[:150] + "..."
        
        # Preparar respuesta
        successful_attempts = [a for a in attempts if a['executable']]
        final_attempt = successful_attempts[0] if successful_attempts else attempts[-1] if attempts else {
            'sql': '', 'executable': False, 'error': 'No se realizaron intentos'
        }
        
        return SQLGenerationResponse(
            question=request.question,
            generated_sql=final_attempt['sql'],
            is_executable=final_attempt['executable'],
            error_message=final_attempt['error'] if not final_attempt['executable'] else None,
            attempts_count=len(attempts),
            similar_example=SimilarExample(**similar_example) if similar_example else None
        )
    
    def _create_prompt(
        self,
        question: str,
        medical_terms: List[MedicalTerm],
        similar_example: Optional[Dict],
        iteration: int = 1,
        previous_sql: Optional[str] = None,
        error_msg: str = ""
    ) -> str:
        """Crear prompt para la generación SQL"""
        
        if iteration > 1 and previous_sql:
            # Prompt de corrección
            error_brief = error_msg[:150] + "..." if len(error_msg) > 150 else error_msg
            prompt = f"""Fix this SQL error for OMOP CDM v5.3:

Question: {question}

Medical codes to use:
{self._format_medical_terms(medical_terms)}

Previous SQL (FAILED):
{previous_sql[:300]}

Error: {error_brief}

Fixed SQL:"""
        else:
            # Prompt inicial
            similar_text = ""
            if similar_example:
                similar_text = f"""
Similar example:
Question: {similar_example['question']}
SQL: {similar_example['sql']}
"""
            
            prompt = f"""You are a SQL expert. Generate ONLY valid SQL for OMOP CDM v5.3.

Question: {question}

Medical codes to use:
{self._format_medical_terms(medical_terms)}
{similar_text}

Instructions:
- Generate ONLY SQL code, no explanations
- Use the provided concept IDs in your WHERE clauses
- Use standard OMOP table names (PERSON, CONDITION_OCCURRENCE, DRUG_EXPOSURE, etc.)
- End with semicolon

SQL:"""
        
        return prompt
    
    def _format_medical_terms(self, medical_terms: List[MedicalTerm]) -> str:
        """Formatear términos médicos para el prompt"""
        if not medical_terms:
            return "No specific medical codes provided"
        
        formatted = []
        for term in medical_terms:
            formatted.append(f"- {term.term} → {term.concept_id}")
        
        return "\n".join(formatted)