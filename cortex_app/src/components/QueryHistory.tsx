import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";

interface QueryLogItem {
  id: number;
  query_text: string;
  timestamp: string;
}

export default function QueryHistory({ isOpen, onClose, onSelect }: {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (query: string) => void;
}) {
  const [queries, setQueries] = useState<QueryLogItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isOpen && isAuthenticated) {
      fetchQueries();
    }
  }, [isOpen, isAuthenticated]);

  const fetchQueries = async () => {
    setIsLoading(true);
    try {
      const data = await api.get("/queries");
      setQueries(data);
    } catch (error) {
      console.error("Error fetching query history:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Overlay to capture clicks outside the drawer */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-text/20 backdrop-blur-sm z-30"
          onClick={onClose}
        ></div>
      )}
      
      {/* Drawer from left side */}
      <div 
        className={`fixed top-0 left-0 h-full w-80 bg-white shadow-large z-40 transform transition-transform duration-300 ease-in-out border-r border-secondary/20 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="modal-header">
          <h2 className="text-xl font-semibold">Historial de consultas</h2>
          <button
            onClick={onClose}
            className="text-white/90 hover:text-white hover:bg-white/20 p-2 rounded-lg transition-all duration-200 hover:rotate-90"
          >
            <X className="icon-md" />
          </button>
        </div>

        <div className="p-4 h-[calc(100%-4rem)] overflow-auto">
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
            </div>
          ) : queries.length === 0 ? (
            <div className="text-center py-8 text-text-muted">
              No hay consultas en el historial
            </div>
          ) : (
            <ul className="space-y-3">
              {queries.map((query) => (
                <li
                  key={query.id}
                  className="p-3 hover:bg-background-soft rounded-xl cursor-pointer transition-all duration-200 border border-secondary/10 hover:border-primary/30 hover:shadow-soft"
                  onClick={() => onSelect(query.query_text)}
                >
                  <div className="flex flex-col">
                    <div className="font-medium text-primary mb-2 line-clamp-3">
                      {query.query_text}
                    </div>
                    <div className="text-xs text-text-muted">
                      {new Date(query.timestamp).toLocaleString()}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </>
  );
}