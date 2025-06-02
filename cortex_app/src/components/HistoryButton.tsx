import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useI18n } from "../context/I18nContext";
import QueryHistory from "./QueryHistory";
import { Clock } from "lucide-react";

interface HistoryButtonProps {
  onSelectQuery: (query: string) => void;
}

export default function HistoryButton({ onSelectQuery }: HistoryButtonProps) {
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const { isAuthenticated } = useAuth();
  const { t } = useI18n();

  const handleOpenHistory = () => {
    if (isAuthenticated) {
      setIsHistoryOpen(true);
    } else {
      // You could show a message or prompt login
      alert(t('history.login_message'));
    }
  };

  return (
    <>
      <button 
        className="btn-ghost p-2 rounded-full"
        onClick={handleOpenHistory}
        title={isAuthenticated ? t('history.view_history') : t('history.login_required')}
      >
        <Clock className="icon-lg text-text-light hover:text-primary transition-colors" />
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