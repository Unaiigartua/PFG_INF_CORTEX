import { X, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { QueryLogDetail } from "../utils/api";
import ModalPortal from "./ModalPortal";

interface QueryDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  query: QueryLogDetail | null;
}

export default function QueryDetailsModal({ isOpen, onClose, query }: QueryDetailsModalProps) {
  if (!isOpen || !query) return null;

  const getStatusIcon = (isExecutable: boolean, attemptsCount: number) => {
    if (isExecutable) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    } else if (attemptsCount > 1) {
      return <AlertCircle className="w-4 h-4 text-orange-500" />;
    } else {
      return <XCircle className="w-4 h-4 text-red-500" />;
    }
  };

  return (
    <ModalPortal>
      <div 
        className="modal-overlay"
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <div 
          className="modal-content w-full max-w-5xl max-h-[90vh] animate-fade-in-down m-4"
        >
          {/* Header */}
          <div className="modal-header">
            <h2 className="text-xl font-semibold">Detalles de la consulta</h2>
            <button 
              onClick={onClose}
              className="text-white/90 hover:text-white hover:bg-white/20 p-2 rounded-lg transition-all duration-200 hover:rotate-90"
            >
              <X className="icon-md" />
            </button>
          </div>

          {/* Content area */}
          <div className="p-6 overflow-auto max-h-[70vh]">
            <div className="space-y-6">
              {/* Pregunta original */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Pregunta original:</h4>
                <p className="text-gray-700 bg-gray-100 p-4 rounded-lg border border-gray-200">{query.question}</p>
              </div>

              {/* Términos médicos */}
              {query.medical_terms && query.medical_terms.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">Términos médicos validados:</h4>
                  <div className="flex flex-wrap gap-2">
                    {query.medical_terms.map((term, index) => (
                      <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm border border-blue-200">
                        {term}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* SQL generado */}
              {query.generated_sql && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">SQL generado:</h4>
                  <pre className="text-sm bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto border border-gray-300">
                    {query.generated_sql}
                  </pre>
                </div>
              )}

              {/* Estado y métricas */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-gray-100 border border-gray-200 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 font-medium">Estado</div>
                  <div className="flex items-center gap-2 mt-2">
                    {getStatusIcon(query.is_executable, query.attempts_count)}
                    <span className="font-semibold text-gray-800">
                      {query.is_executable ? 'Ejecutable' : 'No ejecutable'}
                    </span>
                  </div>
                </div>
                
                <div className="bg-gray-100 border border-gray-200 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 font-medium">Intentos</div>
                  <div className="font-bold text-2xl text-gray-800 mt-1">{query.attempts_count}</div>
                </div>
                
                {query.processing_time && (
                  <div className="bg-gray-100 border border-gray-200 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 font-medium">Tiempo</div>
                    <div className="font-bold text-2xl text-gray-800 mt-1">{query.processing_time.toFixed(2)}s</div>
                  </div>
                )}
              </div>

              {/* Error si existe */}
              {query.error_message && (
                <div>
                  <h4 className="font-semibold text-red-700 mb-2">Error:</h4>
                  <p className="text-red-700 bg-red-50 p-4 rounded-lg border border-red-200 border-l-4 border-l-red-500">
                    {query.error_message}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Footer con botones */}
          <div className="flex justify-end space-x-4 p-6 border-t">
            <button
              onClick={onClose}
              className="btn-cancel px-6 py-2 font-medium rounded-xl transition-all duration-200 border"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </ModalPortal>
  );
}