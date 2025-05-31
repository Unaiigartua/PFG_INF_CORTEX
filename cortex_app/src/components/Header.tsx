import { useAuth } from "../context/AuthContext";
import { User, LogOut, UserCheck} from "lucide-react";


interface HeaderProps {
  onLoginClick: () => void;
}

export default function Header({ onLoginClick }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <div className="flex items-center gap-4">
      {isAuthenticated && user ? (
        <div className="flex items-center gap-4">
          <div className="bg-[#146a8c]/10 px-3 py-1 rounded-full text-sm flex items-center">
            <User className="w-6 h-6" />
            <span className="text-[#146a8c] font-medium">
              Bienvenido, {user.email.split('@')[0]}
            </span>
          </div>
          <button 
            onClick={logout}
            className="bg-red-500 hover:bg-red-600 text-white font-medium py-1 px-3 rounded-md transition-colors duration-300 flex items-center gap-1 shadow-md"
            title="Cerrar sesión"
          >
            <LogOut className="w-6 h-6" />
            <span>Salir</span>
          </button>
        </div>
      ) : (
        <button 
          className="btn-primary"
          onClick={onLoginClick}
        >
          <UserCheck className="w-6 h-6" />
          <span>Log In</span>
        </button>
      )}
      
      <div className="flex gap-3">
        <img src="src/assets/es-flag.png" alt="Español" className="w-12 h-9 rounded shadow hover:shadow-md transition-shadow cursor-pointer" />
        <img src="src/assets/uk-flag.png" alt="English" className="w-12 h-9 rounded shadow hover:shadow-md transition-shadow cursor-pointer" />
      </div>
    </div>
  );
}