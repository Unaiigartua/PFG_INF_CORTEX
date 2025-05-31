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

  // Load authentication state from localStorage on startup
  useEffect(() => {
    const storedToken = localStorage.getItem("auth_token");
    
    if (storedToken) {
      setToken(storedToken);
      // Try to load user data
      const userData = localStorage.getItem("user_data");
      if (userData) {
        try {
          setUser(JSON.parse(userData));
        } catch (e) {
          console.error("Failed to parse user data", e);
        }
      }
    }
    
    setIsLoading(false);
  }, []);

  // Function to get user data with the token
  const fetchUserData = async (authToken: string): Promise<User | null> => {
    try {
      // This endpoint should return the current user data
      // You might need to implement this in your backend
      const response = await fetch(`${config.API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        return userData;
      }
      return null;
    } catch (e) {
      console.error("Error fetching user data", e);
      return null;
    }
  };

  const login = async (newToken: string) => {
    setToken(newToken);
    localStorage.setItem("auth_token", newToken);
    
    // Intentar extraer información del usuario del token JWT
    try {
      const base64Url = newToken.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const payload = JSON.parse(window.atob(base64));
      
      if (payload.sub) {
        const userData = {
          id: payload.user_id || 0,
          email: payload.sub,
          is_active: true
        };
        
        setUser(userData);
        localStorage.setItem("user_data", JSON.stringify(userData));
      }
    } catch (e) {
      console.error("Error decoding token", e);
    }
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_data");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!token,
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