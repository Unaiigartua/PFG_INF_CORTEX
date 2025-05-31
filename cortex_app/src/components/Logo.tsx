import { useState } from 'react';

export default function Logo() {
  const [showText, setShowText] = useState(false);
  
  return (
    <div 
      className="flex flex-col items-center relative mb-6"
      onMouseEnter={() => setShowText(true)}
      onMouseLeave={() => setShowText(false)}
    >
      <img 
        src="src/assets/logo-cortex-t.png" 
        alt="Cortex Logo" 
        className="w-24 h-24 mb-4 drop-shadow-xl filter saturate-150"
      />
      {showText && (
        <div className="absolute -bottom-6 typewriter z-10">
          <p className="text-xs text-center font-medium text-[var(--color-primary)]">
            Clinical Oriented Request Translator for EXecutable SQL
          </p>
        </div>
      )}
    </div>
  );
}