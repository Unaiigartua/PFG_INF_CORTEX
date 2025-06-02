import { useState, useRef, useEffect } from "react";
import { Send, RefreshCw, CheckCircle, Circle } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import TermValidationModal from "./TermValidationModal";
import config from "../config";
import { useAuth } from "../context/AuthContext";

async function extractEntities(text: string, token: string | null, language: 'es' | 'en') {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  
  // Add authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Seleccionar endpoint según el idioma
  const endpoint = language === 'es' ? '/extractEs' : '/extract';

  const response = await fetch(`${config.API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error("Error al extraer términos");
  }

  const data = await response.json();
  return data.entities; 
}

// Add support for saving queries to history
async function saveQueryToHistory(query: string, token: string | null) {
  if (!token) return; // Only save if authenticated
  
  try {
    await fetch(`${config.API_BASE_URL}/queries/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ query_text: query }),
    });
  } catch (error) {
    console.error("Error saving query to history:", error);
  }
}

interface MessageInputProps {
  initialQuery?: string;
}

export default function MessageInput({ initialQuery = "" }: MessageInputProps) {
  const [text, setText] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);
  const [highlightedFragments, setHighlightedFragments] = useState<Array<{text: string, confirmed: boolean}>>([]);
  const [isProcessed, setIsProcessed] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  const [selectedFragmentIndex, setSelectedFragmentIndex] = useState<number | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { token, isAuthenticated } = useAuth();
  const { t, language } = useI18n();

  // Handle initialQuery changes
  useEffect(() => {
    if (initialQuery && !isProcessed) {
      setText(initialQuery);
      // Focus the textarea after setting the text
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  }, [initialQuery, isProcessed]);

  // Verificar si todos los fragmentos están confirmados
  const allFragmentsConfirmed = highlightedFragments.length > 0 && 
    highlightedFragments.every(fragment => fragment.confirmed);

  const handleSend = async () => {
    if (text.trim() === "") return;
    
    if (!isProcessed) {
      try {
        // 👈 Pasamos el idioma actual a la función de extracción
        const entities = await extractEntities(text, token, language);
  
        const fragments = entities.map((e: any) => ({
          text: e.word,
          confirmed: false,
        }));
  
        setHighlightedFragments(fragments);
        setIsProcessed(true);
        
        // Save to history if authenticated
        if (isAuthenticated) {
          saveQueryToHistory(text, token);
        }
      } catch (err) {
        console.error("Error al extraer entidades:", err);
      }
    } else if (allFragmentsConfirmed) {
      console.log(t('input.executing_query'));
    }
  };

  const handleConfirmFragment = (index: number) => {
    setSelectedFragmentIndex(index);
    setModalOpen(true);
  };

  const handleTermConfirm = (selectedTerms: any[]) => {
    if (selectedFragmentIndex === null) return;
    const updatedFragments = [...highlightedFragments];
  
    updatedFragments[selectedFragmentIndex] = {
      ...updatedFragments[selectedFragmentIndex],
      confirmed: true,
      // snomed: selectedTerms, 
    };
    setHighlightedFragments(updatedFragments);
    setSelectedFragmentIndex(null);
  };

  // Función para renderizar el texto con los fragmentos resaltados
  const renderHighlightedText = () => {
    if (!isProcessed) return text;

    let result = [];
    let currentText = text;

    
    const sortedFragments = [...highlightedFragments]
      .map((fragment, index) => ({ ...fragment, index }))
      .sort((a, b) => text.indexOf(a.text) - text.indexOf(b.text));

    let lastIndex = 0;

    for (const fragment of sortedFragments) {
      const fragmentIndex = currentText.indexOf(fragment.text, lastIndex);
      if (fragmentIndex === -1) continue;

      // Texto antes del fragmento
      if (fragmentIndex > lastIndex) {
        result.push(
          <span key={`text-${lastIndex}`}>
            {currentText.substring(lastIndex, fragmentIndex)}
          </span>
        );
      }

      // Fragmento resaltado 
      result.push(
        <button
          key={`fragment-${fragment.index}`}
          onClick={() => handleConfirmFragment(fragment.index)}
          className={`mx-1 px-3 py-1.5 rounded-lg inline-flex items-center gap-2 text-sm cursor-pointer transition-all duration-200 transform hover:scale-105 font-medium ${
            fragment.confirmed 
              ? 'bg-[var(--color-success)]/20 border border-[var(--color-success)]/40 text-[var(--color-success)] shadow-sm' 
              : 'bg-[var(--color-secondary)]/20 border border-[var(--color-secondary)]/40 text-[var(--color-secondary-dark)] hover:bg-[var(--color-secondary)]/30 shadow-sm'
          }`}
        >
          {fragment.text}
          {fragment.confirmed ? (
            <CheckCircle className="icon-sm text-[var(--color-success)]" />
          ) : (
            <Circle className="icon-sm text-[var(--color-secondary-dark)]" />
          )}
        </button>
      );

      lastIndex = fragmentIndex + fragment.text.length;
    }

    // Texto restante después del último fragmento
    if (lastIndex < currentText.length) {
      result.push(
        <span key={`text-end`}>
          {currentText.substring(lastIndex)}
        </span>
      );
    }

    return <div className="whitespace-pre-wrap">{result}</div>;
  };

  useEffect(() => {
    if (textareaRef.current && !isProcessed) {
      // Mantener altura fija en lugar de auto-resize
      textareaRef.current.style.height = "80px";
    }
  }, [text, isProcessed]);

  return (
    <>
    <div className="input-area flex flex-col w-full">
      <div className="flex-grow bg-transparent p-4 min-h-[80px] relative">
        {isProcessed ? (
          <div className="text-base text-[var(--color-text)] min-h-[80px] leading-relaxed">
            {renderHighlightedText()}
          </div>
        ) : (
          <>
            <textarea
              ref={textareaRef}
              className="w-full bg-transparent resize-none text-base text-[var(--color-text)] outline-none min-h-[80px] max-h-[80px] placeholder-[var(--color-text-muted)] leading-relaxed"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              rows={4}
              style={{ overflow: 'hidden' }}
            />
            {!isFocused && text === "" && (
              <div className="absolute top-4 left-4 text-[var(--color-text-muted)] pointer-events-none">
                {t('input.placeholder')}
              </div>
            )}
          </>
        )}
      </div>
      <div className="flex justify-end p-1 px-2 items-center space-x-2">
        {/* RESET button*/}
        {isProcessed && (
          <button
            onClick={() => {
              setIsProcessed(false);
              setText("");
              setHighlightedFragments([]);
            }}
            className="btn-secondary text-sm py-2 px-3"
          >
            <RefreshCw className="icon-sm" />
            {t('input.reset')}
          </button>
        )}
        
        {/* SEND button */}
        <div className="relative">
          <button
            onClick={handleSend}
            disabled={(text.trim() === "" && !isProcessed) || (isProcessed && !allFragmentsConfirmed)}
            className={`btn-primary text-sm py-2 px-3 ${(text.trim() === "" && !isProcessed) || (isProcessed && !allFragmentsConfirmed) ? "opacity-50 cursor-not-allowed" : ""}`}
            onMouseEnter={() => {
              if (isProcessed && !allFragmentsConfirmed) {
                setShowTooltip(true);
              }
            }}
            onMouseLeave={() => {
              setShowTooltip(false);
            }}
          >
            <Send className="icon-sm" />
            {t('input.send')}
          </button>
          {showTooltip && isProcessed && !allFragmentsConfirmed && (
            <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-text text-white text-xs rounded-lg shadow-lg whitespace-nowrap z-10">
              {t('input.confirm_terms')}
              <div className="absolute top-full left-3/4 transform -translate-x-1/2 border-4 border-transparent border-t-text"></div>
            </div>
          )}
        </div>
      </div>
    </div>


    <TermValidationModal
      term={highlightedFragments[selectedFragmentIndex!]?.text || ""}
      isOpen={modalOpen}
      onClose={() => setModalOpen(false)}
      onConfirm={handleTermConfirm}
    />
    </>
  );
}