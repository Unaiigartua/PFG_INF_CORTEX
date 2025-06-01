import { useState } from 'react';
import { useTheme } from '../context/ThemeContext';

export default function Logo() {
  const [showText, setShowText] = useState(false);
  const { theme } = useTheme();
  
  return (
    <div 
      className="flex flex-col items-center relative mb-6"
      onMouseEnter={() => setShowText(true)}
      onMouseLeave={() => setShowText(false)}
    >
      {/* Logo con filtro automático para modo oscuro */}
      <img 
        src="src/assets/logo-cortex-t.png" 
        alt="Cortex Logo" 
        className={`w-24 h-24 mb-4 drop-shadow-xl transition-all duration-300 ${
          theme === 'dark' 
            ? 'filter brightness-0 invert saturate-150' 
            : 'filter saturate-150'
        }`}
      />
      
      {/* Texto descriptivo con mejor contraste */}
      {showText && (
        <div className="absolute -bottom-6 typewriter z-10">
          <p className="text-xs text-center font-medium text-[var(--color-primary)] bg-white/95 dark:bg-gray-800/95 px-3 py-2 rounded-lg border border-[var(--color-primary)]/20">
            Clinical Oriented Request Translator for EXecutable SQL
          </p>
        </div>
      )}
    </div>
  );
}