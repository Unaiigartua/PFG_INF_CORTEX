import { useAuth } from "../context/AuthContext";
import { User, LogOut, LogIn } from "lucide-react";

interface HeaderProps {
  onLoginClick: () => void;
}

export default function Header({ onLoginClick }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuth();

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
            title="Cerrar sesión"
          >
            <LogOut className="icon-md" />
            <span>Salir</span>
          </button>
        </div>
      ) : (
        <button 
          className="btn-primary"
          onClick={onLoginClick}
        >
          <LogIn className="icon-md" />
          <span>Iniciar Sesión</span>
        </button>
      )}
      
      <div className="flex gap-3">
        <img 
          src="src/assets/es-flag.png" 
          alt="Español" 
          className="w-12 h-9 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer hover:scale-105 border border-white/60 hover:border-[var(--color-primary)]/40" 
        />
        <img 
          src="src/assets/uk-flag.png" 
          alt="English" 
          className="w-12 h-9 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer hover:scale-105 border border-white/60 hover:border-[var(--color-secondary)]/40" 
        />
      </div>
    </div>
  );
}