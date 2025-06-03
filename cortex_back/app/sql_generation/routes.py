from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from .models import SQLGenerationRequest, SQLGenerationResponse
from .service import SQLGenerationService
from app.auth.routes import get_current_user
from app.auth.database import get_auth_db
from app.auth.models import QueryLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sql-generation", tags=["sql-generation"])

# Instancia global del servicio (se inicializa una vez)
sql_service = None

def get_sql_service() -> SQLGenerationService:
    """Dependencia para obtener el servicio de generación SQL"""
    global sql_service
    if sql_service is None:
        try:
            sql_service = SQLGenerationService()
            logger.info("Servicio de generación SQL inicializado")
        except Exception as e:
            logger.error(f"Error inicializando servicio SQL: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error inicializando el servicio de generación SQL"
            )
    return sql_service

@router.post("/", response_model=SQLGenerationResponse)
def generate_sql(
    request: SQLGenerationRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_auth_db),
    service: SQLGenerationService = Depends(get_sql_service)
):
    """
    Generar consulta SQL desde lenguaje natural.
    
    Requiere autenticación JWT y registra la consulta en los logs del usuario.
    """
    try:
        # Registrar la consulta en el log del usuario
        log_entry = QueryLog(
            user_id=current_user.id,
            query_text=f"SQL Generation: {request.question}"
        )
        db.add(log_entry)
        db.commit()
        
        # Generar SQL
        logger.info(f"Generando SQL para usuario {current_user.id}: {request.question}")
        result = service.generate_sql(request)
        
        # Log del resultado
        if result.is_executable:
            logger.info(f"SQL generado exitosamente en {result.attempts_count} intentos")
        else:
            logger.warning(f"SQL no ejecutable después de {result.attempts_count} intentos: {result.error_message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error generando SQL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno generando SQL: {str(e)}"
        )

@router.get("/health")
def health_check(service: SQLGenerationService = Depends(get_sql_service)):
    """
    Verificar el estado del servicio de generación SQL.
    
    No requiere autenticación para facilitar monitoreo.
    """
    try:
        ollama_running = service.ollama_client.is_ollama_running()
        model_available = service.ollama_client.check_model_availability(service.model_name)
        
        return {
            "status": "healthy" if ollama_running and model_available else "unhealthy",
            "ollama_running": ollama_running,
            "model_available": model_available,
            "model_name": service.model_name,
            "available_models": service.ollama_client.list_models()
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "error",
            "error": str(e)
        }