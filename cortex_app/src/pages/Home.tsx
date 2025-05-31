import { useState } from "react";
import Header from "../components/Header.tsx";
import Logo from "../components/Logo.tsx";
import MessageInput from "../components/MessageInput.tsx";
import ExamplesList from "../components/ExamplesList.tsx";
import FooterDisclaimer from "../components/FooterDisclaimer.tsx";
import HistoryButton from "../components/HistoryButton.tsx";

interface HomeProps {
  onLoginClick: () => void;
}

export default function Home({ onLoginClick }: HomeProps) {
  const [currentQuery, setCurrentQuery] = useState("");

  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--color-background)] to-[var(--color-background-soft)] flex flex-col relative">
      {/* Elementos decorativos sutiles */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-[var(--color-primary)]/5 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-[var(--color-secondary)]/5 rounded-full blur-3xl"></div>
      
      {/* Barra de navegación limpia y profesional */}
      <div className="w-full flex justify-between items-center p-4 bg-white/80 backdrop-blur-sm sticky top-0 z-50 shadow-lg border-b border-[var(--color-primary)]/10">
        {/* Contenedor izquierdo con margen */}
        <div className="flex-1 flex justify-start pl-4 md:pl-8">
          <HistoryButton onSelectQuery={setCurrentQuery} />
        </div>
        
        {/* Contenedor derecho con margen */}
        <div className="flex-1 flex justify-end pr-4 md:pr-8">
          <Header onLoginClick={onLoginClick} />
        </div>
      </div>

      
      {/* Contenido principal */}
      <div className="flex flex-col items-center justify-center flex-grow px-4 py-5 relative z-10">
        {/* Logo simple y elegante */}
        <div className="logo-container">
          <Logo />
        </div>
        
        {/* Input de mensaje con efectos vibrantes */}
        <div className="w-full max-w-2xl mb-6">
          <MessageInput initialQuery={currentQuery} />
        </div>
        
        {/* Ejemplos con estilo de tarjeta vibrante */}
        <div className="w-full max-w-2xl">
          <ExamplesList onSelectExample={setCurrentQuery} />
        </div>
      </div>
      
      {/* Footer profesional */}
      <div className="w-full flex justify-center items-center p-4 bg-white/70 backdrop-blur-sm mt-auto border-t border-[var(--color-primary)]/10">
        <FooterDisclaimer />
      </div>
    </div>
  );
}