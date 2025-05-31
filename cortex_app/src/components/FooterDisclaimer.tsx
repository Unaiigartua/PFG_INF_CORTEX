import { Info } from "lucide-react";

export default function FooterDisclaimer() {
  return (
    <div className="flex items-center text-[var(--color-text-light)] text-sm bg-white/80 backdrop-blur-sm px-6 py-3 rounded-full shadow-lg border border-[var(--color-primary)]/20 hover:shadow-xl transition-all duration-300 group">
      <Info className="icon-md mr-3 text-[var(--color-warning)] group-hover:scale-105 transition-transform duration-300" />
      <p className="group-hover:text-[var(--color-text)] transition-colors duration-300">
        Disclaimer: Esta herramienta es una prueba y los resultados pueden no ser correctos
      </p>
    </div>
  );
}