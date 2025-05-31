import { useState } from "react";
import config from "../config";
import ModalPortal from "./ModalPortal";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (token: string) => void;
}

export default function LoginModal({ isOpen, onClose, onLoginSuccess }: LoginModalProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      if (isRegistering) {
        // Register
        const registerResponse = await fetch(`${config.API_BASE_URL}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (!registerResponse.ok) {
          const errorData = await registerResponse.json();
          throw new Error(errorData.detail || "Error al registrarse");
        }

        // Auto login after registration
        setIsRegistering(false);
      }

      // Login - using OAuth2 password flow format
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const loginResponse = await fetch(`${config.API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/x-www-form-urlencoded" 
        },
        body: formData,
      });

      if (!loginResponse.ok) {
        const errorData = await loginResponse.json();
        throw new Error(errorData.detail || "Credenciales inválidas");
      }

      const data = await loginResponse.json();
      onLoginSuccess(data.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error en la autenticación");
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <ModalPortal>
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm flex justify-center items-center z-50"
        onClick={(e) => e.target === e.currentTarget && onClose()}
        style={{ top: 0, left: 0, right: 0, bottom: 0 }}
      >
        <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-0 overflow-hidden m-4 animate-fade-in-down">
          {/* Header */}
          <div className="bg-gradient-to-r from-[#146a8c] to-[#2c87a8] text-white p-5 flex justify-between items-center">
            <h2 className="text-xl font-semibold">
              {isRegistering ? "Registro de usuario" : "Iniciar sesión"}
            </h2>
            <button 
              onClick={onClose}
              className="text-white/80 hover:text-white transition-colors p-1 hover:bg-white/10 rounded-full"
            >
              <span className="material-icons">close</span>
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#146a8c]"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#146a8c]"
              required
            />
          </div>

          <div className="flex justify-between items-center pt-4">
            <button
              type="button"
              onClick={() => setIsRegistering(!isRegistering)}
              className="text-[#146a8c] hover:underline text-sm"
            >
              {isRegistering ? "¿Ya tienes cuenta? Inicia sesión" : "¿No tienes cuenta? Regístrate"}
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
            >
              {isLoading ? (
                <span className="flex items-center">
                  <span className="animate-spin h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full"></span>
                  Cargando...
                </span>
              ) : isRegistering ? (
                "Registrarse"
              ) : (
                "Iniciar sesión"
              )}
            </button>
          </div>
          </form>
        </div>
      </div>
    </ModalPortal>
  );
}