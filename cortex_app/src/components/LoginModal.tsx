import { useState, useEffect } from "react";
import { X, Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
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
  const [success, setSuccess] = useState("");

  // Limpiar campos cuando se abre/cierra el modal o cambia el modo
  useEffect(() => {
    if (isOpen) {
      setEmail("");
      setPassword("");
      setError("");
      setSuccess("");
    }
  }, [isOpen, isRegistering]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
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

        // Mostrar mensaje de éxito y cambiar a login
        setSuccess("¡Registro exitoso! Ahora puedes iniciar sesión");
        setIsRegistering(false);
        setPassword(""); // Limpiar contraseña pero mantener email
        setIsLoading(false);
        return;
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
      setSuccess("¡Login exitoso!");
      
      // Pequeña pausa para mostrar el éxito antes de cerrar
      setTimeout(() => {
        onLoginSuccess(data.access_token);
        setEmail("");
        setPassword("");
        setError("");
        setSuccess("");
      }, 500);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error en la autenticación");
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsRegistering(!isRegistering);
    setError("");
    setSuccess("");
    setPassword(""); // Limpiar contraseña al cambiar modo
  };

  if (!isOpen) return null;

  return (
    <ModalPortal>
      <div
        className="modal-overlay"
        onClick={(e) => e.target === e.currentTarget && onClose()}
        style={{ top: 0, left: 0, right: 0, bottom: 0 }}
      >
        <div className="modal-content w-full max-w-md m-4 animate-fade-in-down">
          {/* Header */}
          <div className="modal-header">
            <h2 className="text-xl font-semibold">
              {isRegistering ? "Registro de usuario" : "Iniciar sesión"}
            </h2>
            <button 
              onClick={onClose}
              className="text-white/90 hover:text-white hover:bg-white/20 p-2 rounded-lg transition-all duration-200 hover:rotate-90"
            >
              <X className="icon-md" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-5">
          
          {/* Mensajes de estado */}
          {error && (
            <div className="bg-[var(--color-error)]/10 border border-[var(--color-error)]/30 text-[var(--color-error)] px-4 py-3 rounded-xl flex items-center gap-3">
              <AlertCircle className="icon-md flex-shrink-0" />
              <span className="font-medium">{error}</span>
            </div>
          )}

          {success && (
            <div className="bg-[var(--color-success)]/10 border border-[var(--color-success)]/30 text-[var(--color-success)] px-4 py-3 rounded-xl flex items-center gap-3">
              <CheckCircle2 className="icon-md flex-shrink-0" />
              <span className="font-medium">{success}</span>
            </div>
          )}

          <div className="space-y-2">
            <label className="block text-sm font-semibold text-[var(--color-text)]">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-[var(--color-secondary)]/30 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-[var(--color-primary)] transition-all duration-200 bg-[var(--color-background)] text-[var(--color-text)] placeholder-[var(--color-text-muted)]"
              required
              placeholder="tu@email.com"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-semibold text-[var(--color-text)]">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-[var(--color-secondary)]/30 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-[var(--color-primary)] transition-all duration-200 bg-[var(--color-background)] text-[var(--color-text)] placeholder-[var(--color-text-muted)]"
              required
              placeholder="••••••••"
            />
          </div>

          <div className="flex justify-between items-center pt-4">
            <button
              type="button"
              onClick={toggleMode}
              className="text-[var(--color-primary)] hover:text-[var(--color-primary-dark)] hover:underline transition-all duration-200 text-sm font-medium px-2 py-1 rounded-lg hover:bg-[var(--color-primary)]/5"
            >
              {isRegistering ? "¿Ya tienes cuenta? Inicia sesión" : "¿No tienes cuenta? Regístrate"}
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed min-w-[140px]"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="icon-sm animate-spin" />
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