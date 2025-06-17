import { useState, useEffect } from "react";
import { X, Clock, CheckCircle, XCircle, Eye, Trash2, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useI18n } from "../context/I18nContext";
import { api, QueryLogSummary, QueryLogDetail } from "../utils/api";
import QueryDetailsModal from "./QueryDetailsModal";

interface QueryHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (query: string) => void;
}

export default function QueryHistory({ isOpen, onClose, onSelect }: QueryHistoryProps) {
  const [queries, setQueries] = useState<QueryLogSummary[]>([]);
  const [selectedQuery, setSelectedQuery] = useState<QueryLogDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const { isAuthenticated, token } = useAuth();
  const { t } = useI18n();

  useEffect(() => {
    if (isOpen && isAuthenticated && token) {
      fetchQueries();
    }
  }, [isOpen, isAuthenticated, token]);

  const fetchQueries = async () => {
    if (!token) return;
    
    setIsLoading(true);
    try {
      const data = await api.getQueryHistory(token);
      setQueries(data);
    } catch (error) {
      console.error("Error fetching query history:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewDetails = async (queryId: number) => {
    if (!token) return;
    
    setIsLoadingDetails(true);
    try {
      const details = await api.getQueryDetails(queryId, token);
      setSelectedQuery(details);
      setShowDetailsModal(true);
    } catch (error) {
      console.error("Error fetching query details:", error);
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const handleDeleteQuery = async (queryId: number) => {
    if (!token) return;
    
    if (confirm("¿Estás seguro de que quieres eliminar esta consulta?")) {
      try {
        await api.deleteQuery(queryId, token);
        setQueries(queries.filter(q => q.id !== queryId));
      } catch (error) {
        console.error("Error deleting query:", error);
      }
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (isExecutable: boolean, attemptsCount: number) => {
    if (isExecutable) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    } else if (attemptsCount > 1) {
      return <AlertCircle className="w-4 h-4 text-orange-500" />;
    } else {
      return <XCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusText = (isExecutable: boolean, attemptsCount: number) => {
    if (isExecutable) {
      return `Ejecutable (${attemptsCount} ${attemptsCount === 1 ? 'intento' : 'intentos'})`;
    } else {
      return `No ejecutable (${attemptsCount} ${attemptsCount === 1 ? 'intento' : 'intentos'})`;
    }
  };


  return (
    <>
      {/* Overlay sin difuminar el header */}
      {isOpen && (
        <div 
          className="fixed bg-text/20 z-30"
          style={{ 
            top: '4rem', // Empezar después del header
            left: 0,
            right: 0,
            bottom: 0
          }}
          onClick={onClose}
        ></div>
      )}
      
      {/* Main Drawer */}
      <div 
        className={`fixed top-0 left-0 history-drawer w-96 bg-white shadow-large z-40 transform transition-transform duration-300 ease-in-out border-r border-secondary/20 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="modal-header">
          <h2 className="text-xl font-semibold">{t('history.title')}</h2>
          <button
            onClick={onClose}
            className="text-white/90 hover:text-white hover:bg-white/20 p-2 rounded-lg transition-all duration-200 hover:rotate-90"
          >
            <X className="icon-md" />
          </button>
        </div>

        <div className="p-4 history-content overflow-auto">
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
            </div>
          ) : queries.length === 0 ? (
            <div className="text-center py-8 text-text-muted">
              {t('history.no_queries')}
            </div>
          ) : (
            <ul className="space-y-3">
              {queries.map((query) => (
                <li
                  key={query.id}
                  className="p-3 hover:bg-background-soft rounded-xl cursor-pointer transition-all duration-200 border border-secondary/10 hover:border-primary/30 hover:shadow-soft group"
                >
                  <div 
                    className="flex flex-col"
                    onClick={() => onSelect(query.question)}
                  >
                    {/* Título */}
                    <div className="font-medium text-primary mb-2 line-clamp-3">
                      {query.title || query.question}
                    </div>
                    
                    {/* Estado */}
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(query.is_executable, query.attempts_count)}
                      <span className="text-xs text-text-muted">
                        {getStatusText(query.is_executable, query.attempts_count)}
                      </span>
                    </div>
                    
                    {/* Fecha */}
                    <div className="flex items-center gap-1 text-xs text-text-muted">
                      <Clock className="w-3 h-3" />
                      {formatTime(query.timestamp)}
                    </div>
                  </div>
                  
                  {/* Botones de acción */}
                  <div className="flex gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewDetails(query.id);
                      }}
                      className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
                      disabled={isLoadingDetails}
                    >
                      <Eye className="w-3 h-3" />
                      Detalles
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteQuery(query.id);
                      }}
                      className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition-colors"
                    >
                      <Trash2 className="w-3 h-3" />
                      Eliminar
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Modal de detalles separado */}
      <QueryDetailsModal
        isOpen={showDetailsModal}
        onClose={() => setShowDetailsModal(false)}
        query={selectedQuery}
      />
    </>
  );
}