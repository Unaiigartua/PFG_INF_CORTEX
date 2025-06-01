import { Sun, Moon } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="btn-ghost p-2 rounded-full relative overflow-hidden group"
      title={theme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'}
    >
      {/* Contenedor con transición */}
      <div className="relative">
        {/* Icono de sol (modo claro) */}
        <Sun 
          className={`icon-lg text-[var(--color-warning)] transition-all duration-500 transform ${
            theme === 'light' 
              ? 'rotate-0 scale-100 opacity-100' 
              : 'rotate-180 scale-0 opacity-0 absolute inset-0'
          }`} 
        />
        
        {/* Icono de luna (modo oscuro) */}
        <Moon 
          className={`icon-lg text-[var(--color-secondary)] transition-all duration-500 transform ${
            theme === 'dark' 
              ? 'rotate-0 scale-100 opacity-100' 
              : '-rotate-180 scale-0 opacity-0 absolute inset-0'
          }`} 
        />
      </div>

      {/* Efecto de fondo al hover */}
      <div className="absolute inset-0 bg-[var(--color-primary)]/10 rounded-full scale-0 group-hover:scale-100 transition-transform duration-300"></div>
    </button>
  );
}