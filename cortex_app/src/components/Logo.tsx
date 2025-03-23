import { useState } from 'react';

export default function Logo() {
  const [showText, setShowText] = useState(false);
  
  return (
    <div 
      className="flex flex-col items-center relative w-[140px] h-[140px]"
      onMouseEnter={() => setShowText(true)}
      onMouseLeave={() => setShowText(false)}
    >
      <div className={`transition-all duration-500 absolute transform ${showText ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}`}>
        <img 
          src="src/assets/logo-cortex-t.png" 
          alt="Cortex Logo" 
          className="w-35 h-35 mb-3 drop-shadow-xl filter saturate-150"
        />
      </div>
      <div className={`w-full h-full flex flex-col justify-center items-center text-center p-4 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] rounded-full text-white shadow-xl transition-all duration-500 transform ${showText ? 'scale-100 opacity-100' : 'scale-0 opacity-0'}`}>
        <span className="font-bold text-lg mb-1">CORTEX</span>
        <p className="text-[10px] md:text-xs leading-tight">
          Clinical Oriented<br />
          Request<br />
          Translator for<br />
          EXecutable SQL
        </p>
      </div>
    </div>
  );
}