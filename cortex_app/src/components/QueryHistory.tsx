import { useState, useEffect } from "react";
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
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-30"
          onClick={onClose}
        ></div>
      )}
      
      {/* Drawer from left side */}
      <div 
        className={`fixed top-0 left-0 h-full w-80 bg-white shadow-xl z-40 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="bg-gradient-to-r from-[#146a8c] to-[#2c87a8] text-white p-4 flex justify-between items-center">
          <h2 className="text-xl font-semibold">Historial de consultas</h2>
          <button
            onClick={onClose}
            className="text-white/80 hover:text-white transition-colors p-1 hover:bg-white/10 rounded-full"
          >
            <span className="material-icons">close</span>
          </button>
        </div>

        <div className="p-4 h-[calc(100%-4rem)] overflow-auto">
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#146a8c]"></div>
            </div>
          ) : queries.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No hay consultas en el historial
            </div>
          ) : (
            <ul className="space-y-2">
              {queries.map((query) => (
                <li
                  key={query.id}
                  className="p-3 hover:bg-gray-50 rounded-md cursor-pointer transition-colors border border-gray-100"
                  onClick={() => onSelect(query.query_text)}
                >
                  <div className="flex flex-col">
                    <div className="font-medium text-[#146a8c] mb-1">{query.query_text}</div>
                    <div className="text-xs text-gray-500">
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