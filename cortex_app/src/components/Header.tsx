import { useAuth } from "../context/AuthContext";
import { useI18n } from "../context/I18nContext";
import { User, LogOut, LogIn } from "lucide-react";
import ThemeToggle from "./ThemeToggle";

interface HeaderProps {
  onLoginClick: () => void;
}

export default function Header({ onLoginClick }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuth();
  const { language, setLanguage, t } = useI18n();

  return (
    <div className="flex items-center gap-4">
      {isAuthenticated && user ? (
        <div className="flex items-center gap-4">
          <div className="bg-[var(--color-primary)]/10 backdrop-blur-sm px-4 py-2 rounded-full text-sm flex items-center gap-2 border border-[var(--color-primary)]/20 shadow-md">
            <User className="icon-md text-[var(--color-primary)]" />
            <span className="text-[var(--color-primary-dark)] font-semibold">
              {user.email.split('@')[0]}
            </span>
          </div>
          <button 
            onClick={logout}
            className="bg-[var(--color-error)] hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-xl transition-all duration-300 flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
            title={t('header.close_session')}
          >
            <LogOut className="icon-md" />
            <span>{t('header.logout')}</span>
          </button>
        </div>
      ) : (
        <button 
          className="btn-primary"
          onClick={onLoginClick}
        >
          <LogIn className="icon-md" />
          <span>{t('header.login')}</span>
        </button>
      )}
      
      <div className="flex gap-3">
        <button
          onClick={() => setLanguage('es')}
          className={`transition-all duration-300 cursor-pointer hover:scale-105 border rounded-lg ${
            language === 'es' 
              ? 'border-[var(--color-primary)]/60 shadow-lg ring-2 ring-[var(--color-primary)]/30' 
              : 'border-white/60 hover:border-[var(--color-primary)]/40 shadow-lg hover:shadow-xl'
          }`}
          title="Español"
        >
          <img 
            src="src/assets/es-flag.png" 
            alt="Español" 
            className="w-12 h-9 rounded-lg" 
          />
        </button>
        <button
          onClick={() => setLanguage('en')}
          className={`transition-all duration-300 cursor-pointer hover:scale-105 border rounded-lg ${
            language === 'en' 
              ? 'border-[var(--color-secondary)]/60 shadow-lg ring-2 ring-[var(--color-secondary)]/30' 
              : 'border-white/60 hover:border-[var(--color-secondary)]/40 shadow-lg hover:shadow-xl'
          }`}
          title="English"
        >
          <img 
            src="src/assets/uk-flag.png" 
            alt="English" 
            className="w-12 h-9 rounded-lg" 
          />
        </button>
      </div>
    </div>
  );
}