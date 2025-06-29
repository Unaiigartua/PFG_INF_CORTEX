import { X, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { QueryLogDetail } from "../utils/api";
import { useI18n } from "../context/I18nContext";
import ModalPortal from "./ModalPortal";

interface QueryDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  query: QueryLogDetail | null;
}

export default function QueryDetailsModal({ isOpen, onClose, query }: QueryDetailsModalProps) {
  const { t } = useI18n();

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

  const getStatusText = (isExecutable: boolean) => {
    return isExecutable ? t('query_details.executable') : t('query_details.not_executable');
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
            <h2 className="text-xl font-semibold">{t('query_details.title')}</h2>
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
                <h4 className="font-semibold text-gray-800 mb-2">{t('query_details.original_question')}:</h4>
                <p className="text-gray-700 bg-gray-100 p-4 rounded-lg border border-gray-200">{query.question}</p>
              </div>

              {/* Términos médicos */}
              {query.medical_terms && query.medical_terms.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">{t('query_details.validated_medical_terms')}:</h4>
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
                  <h4 className="font-semibold text-gray-800 mb-2">{t('query_details.generated_sql')}:</h4>
                  <pre className="text-sm bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto border border-gray-300">
                    {query.generated_sql}
                  </pre>
                </div>
              )}

              {/* Estado y métricas */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-gray-100 border border-gray-200 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 font-medium">{t('query_details.status')}</div>
                  <div className="flex items-center gap-2 mt-2">
                    {getStatusIcon(query.is_executable, query.attempts_count)}
                    <span className="font-semibold text-gray-800">
                      {getStatusText(query.is_executable)}
                    </span>
                  </div>
                </div>
                
                <div className="bg-gray-100 border border-gray-200 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 font-medium">{t('query_details.attempts')}</div>
                  <div className="font-bold text-2xl text-gray-800 mt-1">{query.attempts_count}</div>
                </div>
                
                {query.processing_time && (
                  <div className="bg-gray-100 border border-gray-200 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 font-medium">{t('query_details.processing_time')}</div>
                    <div className="font-bold text-2xl text-gray-800 mt-1">{query.processing_time.toFixed(2)}s</div>
                  </div>
                )}

                {query.results_count !== null && query.results_count !== undefined && (
                  <div className="bg-gray-100 border border-gray-200 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 font-medium">{t('query_details.results_count')}</div>
                    <div className="font-bold text-2xl text-gray-800 mt-1">{query.results_count}</div>
                  </div>
                )}
              </div>

              {/* Error si existe */}
              {query.error_message && (
                <div>
                  <h4 className="font-semibold text-red-700 mb-2">{t('query_details.error')}:</h4>
                  <p className="text-red-700 bg-red-50 p-4 rounded-lg border border-red-200 border-l-4 border-l-red-500">
                    {query.error_message}
                  </p>
                </div>
              )}

              {/* Información adicional */}
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h4 className="font-semibold text-gray-800 mb-2">{t('query_details.additional_info')}:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="font-medium text-gray-600">{t('query_details.query_id')}:</span>
                    <span className="ml-2 text-gray-800">#{query.id}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-600">{t('query_details.timestamp')}:</span>
                    <span className="ml-2 text-gray-800">
                      {new Date(query.timestamp).toLocaleString()}
                    </span>
                  </div>
                  {query.title && (
                    <div className="md:col-span-2">
                      <span className="font-medium text-gray-600">{t('query_details.title_title')}:</span>
                      <span className="ml-2 text-gray-800">{query.title}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Footer con botones */}
          <div className="flex justify-end space-x-4 p-6 border-t">
            <button
              onClick={onClose}
              className="btn-cancel px-6 py-2 font-medium rounded-xl transition-all duration-200 border"
            >
              {t('general.close')}
            </button>
          </div>
        </div>
      </div>
    </ModalPortal>
  );
}