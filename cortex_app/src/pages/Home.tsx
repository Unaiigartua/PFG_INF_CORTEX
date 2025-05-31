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
    <div className="min-h-screen bg-[#eaf3f3] flex flex-col">
      {/* Barra de navegación con efecto de cristal */}
      <div className="w-full flex justify-between items-center p-4 bg-white/30 backdrop-blur-sm sticky top-0 z-10 shadow-sm">
        <HistoryButton onSelectQuery={setCurrentQuery} />
        <Header onLoginClick={onLoginClick} />
      </div>
      
      {/* Contenido principal */}
      <div className="flex flex-col items-center justify-center flex-grow px-4 py-8">
        {/* Logo con animación suave */}
        <div className="logo-container">
          <Logo />
        </div>
        
        {/* Input de mensaje con sombras mejoradas */}
        <div className="w-full max-w-3xl mb-8">
          <MessageInput initialQuery={currentQuery} />
        </div>
        
        {/* Ejemplos con estilo de tarjeta */}
        <div className="w-full max-w-3xl">
          <ExamplesList onSelectExample={setCurrentQuery} />
        </div>
      </div>
      
      {/* Footer con el disclaimer */}
      <div className="w-full flex justify-center items-center p-4 bg-white/20 backdrop-blur-sm mt-auto">
        <FooterDisclaimer />
      </div>
    </div>
  );
}