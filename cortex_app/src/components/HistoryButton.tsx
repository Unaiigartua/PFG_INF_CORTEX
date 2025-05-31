import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import QueryHistory from "./QueryHistory";

interface HistoryButtonProps {
  onSelectQuery: (query: string) => void;
}

export default function HistoryButton({ onSelectQuery }: HistoryButtonProps) {
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const { isAuthenticated } = useAuth();

  const handleOpenHistory = () => {
    if (isAuthenticated) {
      setIsHistoryOpen(true);
    } else {
      // You could show a message or prompt login
      alert("Inicia sesión para ver tu historial de consultas");
    }
  };

  return (
    <>
      <button 
        className="flex items-center text-gray-700 hover:text-[#146a8c] transition-colors p-2 rounded-full hover:bg-white/50"
        onClick={handleOpenHistory}
        title={isAuthenticated ? "Ver historial" : "Inicia sesión para ver historial"}
      >
        <span className="material-icons text-2xl">schedule</span>
      </button>

      <QueryHistory 
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelect={(query) => {
          onSelectQuery(query);
          setIsHistoryOpen(false);
        }}
      />
    </>
  );
}