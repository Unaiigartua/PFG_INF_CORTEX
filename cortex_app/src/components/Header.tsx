import { useAuth } from "../context/AuthContext";


interface HeaderProps {
  onLoginClick: () => void;
}

export default function Header({ onLoginClick }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <div className="flex items-center gap-4">
      {isAuthenticated && user ? (
        <div className="flex items-center gap-3">
          <div className="bg-[#146a8c]/10 px-3 py-1 rounded-full text-sm flex items-center">
            <span className="material-icons text-sm mr-1 text-[#146a8c]">person</span>
            <span className="text-[#146a8c] font-medium">
              Bienvenido, {user.email.split('@')[0]}
            </span>
          </div>
          <button 
            onClick={logout}
            className="bg-red-500 hover:bg-red-600 text-white font-medium py-1 px-3 rounded-md transition-colors duration-300 flex items-center gap-1 shadow-md"
            title="Cerrar sesión"
          >
            <span className="material-icons text-sm">logout</span>
            <span>Salir</span>
          </button>
        </div>
      ) : (
        <button 
          className="btn-primary"
          onClick={onLoginClick}
        >
          <span className="material-icons text-sm">person_outline</span>
          <span>Log In</span>
        </button>
      )}
      
      <div className="flex gap-2">
        <img src="src/assets/es-flag.png" alt="Español" className="w-8 h-6 rounded shadow hover:shadow-md transition-shadow cursor-pointer" />
        <img src="src/assets/us-flag.png" alt="English" className="w-8 h-6 rounded shadow hover:shadow-md transition-shadow cursor-pointer" />
      </div>
    </div>
  );
}