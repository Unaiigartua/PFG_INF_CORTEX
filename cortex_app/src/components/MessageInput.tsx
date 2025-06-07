import { useState, useRef, useEffect } from "react";
import { Send, RefreshCw, CheckCircle, Circle, Highlighter, Loader2 } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import TermValidationModal from "./TermValidationModal";
import SQLResultView from "./SQLResultView";
import config from "../config";
import { useAuth } from "../context/AuthContext";

async function extractEntities(text: string, token: string | null, language: 'es' | 'en') {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

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

async function saveQueryToHistory(query: string, token: string | null) {
  if (!token) return;
  
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

async function generateSQL(question: string, medicalTerms: any[], token: string | null) {
  if (!token) {
    throw new Error("Token de autenticación requerido");
  }

  const response = await fetch(`${config.API_BASE_URL}/sql-generation/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      question,
      medical_terms: medicalTerms
    }),
  });

  if (!response.ok) {
    throw new Error("Error al generar SQL");
  }

  return response.json();
}

interface MessageInputProps {
  initialQuery?: string;
}

interface HighlightedFragment {
  text: string;
  start: number;
  end: number;
  confirmed: boolean;
  snomedTerms?: any[];
}

export default function MessageInput({ initialQuery = "" }: MessageInputProps) {
  const [text, setText] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);
  const [highlightedFragments, setHighlightedFragments] = useState<HighlightedFragment[]>([]);
  const [isProcessed, setIsProcessed] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [selection, setSelection] = useState<{ start: number; end: number } | null>(null);
  const [isGeneratingSQL, setIsGeneratingSQL] = useState(false);
  const [sqlResult, setSqlResult] = useState<any>(null);
  const [selectedFragmentIndex, setSelectedFragmentIndex] = useState<number | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const textDisplayRef = useRef<HTMLDivElement>(null);
  const { token, isAuthenticated } = useAuth();
  const { t, language } = useI18n();

  useEffect(() => {
    if (initialQuery && !isProcessed) {
      setText(initialQuery);
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  }, [initialQuery, isProcessed]);

  const allFragmentsConfirmed = highlightedFragments.length > 0 && 
    highlightedFragments.every(fragment => fragment.confirmed);

  const handleSend = async () => {
    if (text.trim() === "") return;
    
    if (!isProcessed) {
      try {
        const entities = await extractEntities(text, token, language);
  
        const fragments: HighlightedFragment[] = entities.map((e: any) => ({
          text: e.word,
          start: e.start,
          end: e.end,
          confirmed: false,
        }));
  
        setHighlightedFragments(fragments);
        setIsProcessed(true);
        
        if (isAuthenticated) {
          saveQueryToHistory(text, token);
        }
      } catch (err) {
        console.error("Error al extraer entidades:", err);
      }
    } else if (allFragmentsConfirmed && isAuthenticated && token) {
      setIsGeneratingSQL(true);
      try {
        const medicalTerms: any[] = [];
        highlightedFragments.forEach(fragment => {
          if (fragment.snomedTerms) {
            fragment.snomedTerms.forEach(snomedTerm => {
              medicalTerms.push({
                term: fragment.text,
                concept_id: snomedTerm.concept_id
              });
            });
          }
        });

        const result = await generateSQL(text, medicalTerms, token);
        setSqlResult(result);
      } catch (err) {
        console.error("Error al generar SQL:", err);
      } finally {
        setIsGeneratingSQL(false);
      }
    }
  };

  const handleConfirmFragment = (index: number) => {
    if (isEditMode) return;
    
    setSelectedFragmentIndex(index);
    setModalOpen(true);
  };

  const handleTermConfirm = (selectedTerms: any[]) => {
    if (selectedFragmentIndex === null) return;
    const updatedFragments = [...highlightedFragments];
  
    updatedFragments[selectedFragmentIndex] = {
      ...updatedFragments[selectedFragmentIndex],
      confirmed: true,
      snomedTerms: selectedTerms,
    };
    setHighlightedFragments(updatedFragments);
    setSelectedFragmentIndex(null);
  };

  const handleTextSelection = () => {
    if (!isEditMode || !textDisplayRef.current) return;

    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);
    const selectedText = range.toString().trim();
    
    if (selectedText.length === 0) return;

    const containerElement = textDisplayRef.current;
    const textNodes = getTextNodesIn(containerElement);
    
    let textOffset = 0;
    let startOffset = -1;
    let endOffset = -1;

    for (const node of textNodes) {
      const nodeText = node.textContent || '';
      
      if (range.startContainer === node) {
        startOffset = textOffset + range.startOffset;
      }
      if (range.endContainer === node) {
        endOffset = textOffset + range.endOffset;
      }
      
      textOffset += nodeText.length;
      
      if (startOffset !== -1 && endOffset !== -1) break;
    }

    if (startOffset !== -1 && endOffset !== -1) {
      setSelection({ start: startOffset, end: endOffset });
    }
  };

  const getTextNodesIn = (node: Node): Text[] => {
    const textNodes: Text[] = [];
    
    if (node.nodeType === Node.TEXT_NODE) {
      textNodes.push(node as Text);
    } else {
      for (let i = 0; i < node.childNodes.length; i++) {
        textNodes.push(...getTextNodesIn(node.childNodes[i]));
      }
    }
    
    return textNodes;
  };

  const addSelectedTerm = () => {
    if (!selection) return;

    const selectedText = text.slice(selection.start, selection.end).trim();
    if (selectedText.length === 0) return;

    const hasOverlap = highlightedFragments.some(fragment => 
      !(selection.end <= fragment.start || selection.start >= fragment.end)
    );

    if (hasOverlap) {
      alert('No se pueden crear términos solapados');
      return;
    }

    const newFragment: HighlightedFragment = {
      text: selectedText,
      start: selection.start,
      end: selection.end,
      confirmed: false,
    };

    setHighlightedFragments(prev => [...prev, newFragment].sort((a, b) => a.start - b.start));
    setSelection(null);
    
    window.getSelection()?.removeAllRanges();
  };

  const removeFragment = (index: number) => {
    setHighlightedFragments(prev => prev.filter((_, i) => i !== index));
  };

  const toggleEditMode = () => {
    setIsEditMode(!isEditMode);
    setSelection(null);
    
    if (isEditMode) {
      window.getSelection()?.removeAllRanges();
    }
  };

  const handleNewQuery = () => {
    setIsProcessed(false);
    setText("");
    setHighlightedFragments([]);
    setSqlResult(null);
    setIsEditMode(false);
    setSelection(null);
  };

  const handleEditQuery = () => {
    setSqlResult(null);
  };

  const renderHighlightedText = () => {
    if (!isProcessed) return text;

    let result = [];
    let lastIndex = 0;

    const sortedFragments = [...highlightedFragments].sort((a, b) => a.start - b.start);

    for (let i = 0; i < sortedFragments.length; i++) {
      const fragment = sortedFragments[i];

      if (fragment.start > lastIndex) {
        result.push(
          <span key={`text-${lastIndex}`}>
            {text.substring(lastIndex, fragment.start)}
          </span>
        );
      }

      result.push(
        <button
          key={`fragment-${i}`}
          onClick={() => isEditMode ? removeFragment(highlightedFragments.indexOf(fragment)) : handleConfirmFragment(highlightedFragments.indexOf(fragment))}
          className={`mx-1 px-3 py-1.5 rounded-lg inline-flex items-center gap-2 text-sm cursor-pointer transition-all duration-200 transform hover:scale-105 font-medium ${
            isEditMode 
              ? 'bg-[var(--color-error)]/20 border border-[var(--color-error)]/40 text-[var(--color-error)] hover:bg-[var(--color-error)]/30'
              : fragment.confirmed 
                ? 'bg-[var(--color-success)]/20 border border-[var(--color-success)]/40 text-[var(--color-success)] shadow-sm' 
                : 'bg-[var(--color-secondary)]/20 border border-[var(--color-secondary)]/40 text-[var(--color-secondary-dark)] hover:bg-[var(--color-secondary)]/30 shadow-sm'
          }`}
          title={isEditMode ? 'Click para eliminar' : undefined}
        >
          {fragment.text}
          {!isEditMode && (
            fragment.confirmed ? (
              <CheckCircle className="icon-sm text-[var(--color-success)]" />
            ) : (
              <Circle className="icon-sm text-[var(--color-secondary-dark)]" />
            )
          )}
        </button>
      );

      lastIndex = fragment.end;
    }

    if (lastIndex < text.length) {
      result.push(
        <span key={`text-end`}>
          {text.substring(lastIndex)}
        </span>
      );
    }

    return <div className="whitespace-pre-wrap">{result}</div>;
  };

  useEffect(() => {
    if (textareaRef.current && !isProcessed) {
      textareaRef.current.style.height = "80px";
    }
  }, [text, isProcessed]);

  return (
    <>
      {sqlResult ? (
        <SQLResultView
          result={sqlResult}
          validatedTerms={highlightedFragments
            .filter(f => f.confirmed && f.snomedTerms)
            .map(f => ({
              text: f.text,
              snomedTerms: f.snomedTerms || []
            }))
          }
          onNewQuery={handleNewQuery}
          onEditQuery={handleEditQuery}
        />
      ) : (
        <div className="input-area flex flex-col w-full">
          <div className="flex-grow bg-transparent p-4 min-h-[80px] relative">
            {isProcessed ? (
              <div 
                ref={textDisplayRef}
                className={`text-base text-[var(--color-text)] min-h-[80px] leading-relaxed ${
                  isEditMode ? 'select-text cursor-text' : 'select-none'
                }`}
                onMouseUp={handleTextSelection}
                style={{ userSelect: isEditMode ? 'text' : 'none' }}
              >
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
          
          {isEditMode && selection && (
            <div className="px-4 pb-2">
              <div className="flex items-center justify-between bg-[var(--color-primary)]/10 border border-[var(--color-primary)]/30 rounded-lg px-3 py-2">
                <span className="text-sm text-[var(--color-text)]">
                  Seleccionado: "<strong>{text.slice(selection.start, selection.end)}</strong>"
                </span>
                <button
                  onClick={addSelectedTerm}
                  className="btn-primary text-xs py-1 px-3"
                >
                  Añadir término
                </button>
              </div>
            </div>
          )}
          
          <div className="flex justify-end p-1 px-2 items-center space-x-2">
            {isProcessed && !isGeneratingSQL && (
              <button
                onClick={handleNewQuery}
                className="btn-secondary text-sm py-2 px-3"
              >
                <RefreshCw className="icon-sm" />
                {t('input.reset')}
              </button>
            )}
            
            {isProcessed && (
              <button
                onClick={toggleEditMode}
                className={`text-sm py-2 px-3 transition-all duration-300 flex items-center gap-2 rounded-xl font-semibold ${
                  isEditMode 
                    ? 'bg-[var(--color-warning)] hover:bg-[var(--color-warning)]/80 text-white shadow-lg'
                    : 'btn-ghost'
                }`}
                title={isEditMode ? 'Salir del modo edición' : 'Editar términos detectados'}
              >
                <Highlighter className="icon-sm" />
                {isEditMode ? 'Finalizar' : 'Editar'}
              </button>
            )}
            
            <div className="relative">
              <button
                onClick={handleSend}
                disabled={
                  (text.trim() === "" && !isProcessed) || 
                  (isProcessed && !allFragmentsConfirmed) || 
                  (allFragmentsConfirmed && (!isAuthenticated || !token)) ||
                  isGeneratingSQL ||
                  isEditMode
                }
                className={`btn-primary text-sm py-2 px-3 ${
                  (text.trim() === "" && !isProcessed) || 
                  (isProcessed && !allFragmentsConfirmed) || 
                  (allFragmentsConfirmed && (!isAuthenticated || !token)) ||
                  isGeneratingSQL ||
                  isEditMode ? "opacity-50 cursor-not-allowed" : ""
                }`}
                onMouseEnter={() => {
                  if (isProcessed && !allFragmentsConfirmed && !isEditMode) {
                    setShowTooltip(true);
                  }
                }}
                onMouseLeave={() => {
                  setShowTooltip(false);
                }}
              >
                {isGeneratingSQL ? (
                  <>
                    <Loader2 className="icon-sm animate-spin" />
                    Generando SQL...
                  </>
                ) : (
                  <>
                    <Send className="icon-sm" />
                    {t('input.send')}
                  </>
                )}
              </button>
              {showTooltip && isProcessed && !allFragmentsConfirmed && !isEditMode && (
                <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-text text-white text-xs rounded-lg shadow-lg whitespace-nowrap z-10">
                  {t('input.confirm_terms')}
                  <div className="absolute top-full left-3/4 transform -translate-x-1/2 border-4 border-transparent border-t-text"></div>
                </div>
              )}
              {isProcessed && allFragmentsConfirmed && (!isAuthenticated || !token) && (
                <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-text text-white text-xs rounded-lg shadow-lg whitespace-nowrap z-10">
                  {t('input.save_query_login')}
                  <div className="absolute top-full left-3/4 transform -translate-x-1/2 border-4 border-transparent border-t-text"></div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <TermValidationModal
        term={highlightedFragments[selectedFragmentIndex!]?.text || ""}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onConfirm={handleTermConfirm}
      />
    </>
  );
}