import { createContext, useState, useContext, useEffect, ReactNode } from "react";
import config from "../config";

interface User {
  id: number;
  email: string;
  is_active: boolean;
}

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  user: User | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Function to get user data with the token
  const fetchUserData = async (authToken: string): Promise<User | null> => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
          "ngrok-skip-browser-warning": "true",
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const userData = await response.json();
        return userData;
      } else {
        console.error("Error al obtener datos del usuario:", response.status);
        return null;
      }
    } catch (e) {
      console.error("Error fetching user data", e);
      return null;
    }
  };

  // Load authentication state from localStorage on startup
  useEffect(() => {
    const loadAuthState = async () => {
      try {
        const storedToken = localStorage.getItem("auth_token");
        console.log("Token cargado desde localStorage:", !!storedToken);
        
        if (storedToken) {
          setToken(storedToken);
          
          // Try to load user data from localStorage first
          const userData = localStorage.getItem("user_data");
          if (userData) {
            try {
              const parsedUser = JSON.parse(userData);
              console.log("Usuario cargado desde localStorage:", parsedUser);
              setUser(parsedUser);
            } catch (e) {
              console.error("Failed to parse user data", e);
            }
          }
          
          // If no user data in localStorage, fetch from API
          if (!userData) {
            const fetchedUser = await fetchUserData(storedToken);
            if (fetchedUser) {
              setUser(fetchedUser);
              try {
                localStorage.setItem("user_data", JSON.stringify(fetchedUser));
              } catch (e) {
                console.log("No se pudo guardar usuario en localStorage");
              }
            }
          }
        }
      } catch (e) {
        console.log("localStorage no disponible");
      }
      
      setIsLoading(false);
    };

    loadAuthState();
  }, []);

  const login = async (newToken: string) => {
    console.log("Iniciando login con token:", !!newToken);
    setToken(newToken);
    
    try {
      localStorage.setItem("auth_token", newToken);
    } catch (e) {
      console.log("No se pudo guardar en localStorage");
    }
    
    // Intentar extraer información del usuario del token JWT
    try {
      const base64Url = newToken.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const payload = JSON.parse(window.atob(base64));
      console.log("Payload del token:", payload);
      
      // Si tenemos user_id en el payload, intentar obtener los datos del usuario
      if (payload.user_id) {
        const fetchedUser = await fetchUserData(newToken);
        if (fetchedUser) {
          setUser(fetchedUser);
          try {
            localStorage.setItem("user_data", JSON.stringify(fetchedUser));
          } catch (e) {
            console.log("No se pudo guardar usuario en localStorage");
          }
        } else {
          // Fallback: crear un usuario básico con el user_id
          const fallbackUser = {
            id: payload.user_id,
            email: `user${payload.user_id}@example.com`, // Email temporal
            is_active: true
          };
          console.log("Usando usuario fallback:", fallbackUser);
          setUser(fallbackUser);
        }
      }
    } catch (e) {
      console.error("Error decoding token", e);
    }
  };

  const logout = () => {
    console.log("Cerrando sesión");
    try {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user_data");
    } catch (e) {
      console.log("No se pudo limpiar localStorage");
    }
    setToken(null);
    setUser(null);
  };

  const isAuthenticated = !!token;
  console.log("Estado de autenticación:", { isAuthenticated, hasUser: !!user, hasToken: !!token });

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        token,
        user,
        login,
        logout,
        isLoading
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}