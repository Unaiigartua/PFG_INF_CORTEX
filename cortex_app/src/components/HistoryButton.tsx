import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import QueryHistory from "./QueryHistory";
import {Clock } from "lucide-react";

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
        className="flex items-center text-gray-700 hover:text-[#146a8c] transition-colors p-0.5 rounded-full hover:bg-white/50"
        onClick={handleOpenHistory}
        title={isAuthenticated ? "Ver historial" : "Inicia sesión para ver historial"}
      >
      <Clock className="w-7 h-7" />
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