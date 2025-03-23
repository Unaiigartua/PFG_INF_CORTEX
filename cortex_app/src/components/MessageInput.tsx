import { useState, useRef, useEffect } from "react";

export default function MessageInput() {
  const [text, setText] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [highlightedFragments, setHighlightedFragments] = useState<Array<{text: string, confirmed: boolean}>>([]);
  const [isProcessed, setIsProcessed] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Verificar si todos los fragmentos están confirmados
  const allFragmentsConfirmed = highlightedFragments.length > 0 && 
    highlightedFragments.every(fragment => fragment.confirmed);

  const handleSend = () => {
    if (text.trim() === "") return;
    
    if (!isProcessed) {
      // Primera pulsación: Simulación de la respuesta del backend
      setText("Patients diagnosed in the lower inner quadrant of breast that went under lumpectomy");
      setHighlightedFragments([
        { text: "inner quadrant of breast", confirmed: false },
        { text: "lumpectomy", confirmed: false },
      ]);
      setIsProcessed(true);
    } else if (allFragmentsConfirmed) {
      // Segunda pulsación: Todos los fragmentos están confirmados, ejecutar la consulta
      console.log("Ejecutando consulta SQL...");
      // Aquí iría la lógica para enviar al backend
    }
  };

  const handleConfirmFragment = (index: number) => {
    const updatedFragments = [...highlightedFragments];
    updatedFragments[index].confirmed = !updatedFragments[index].confirmed;
    setHighlightedFragments(updatedFragments);
  };

  // Función para renderizar el texto con los fragmentos resaltados
  const renderHighlightedText = () => {
    if (!isProcessed) return text;

    let result = [];
    let currentText = text;

    // Ordenamos los fragmentos por su posición en el texto para procesarlos secuencialmente
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

      // Fragmento resaltado - Hacemos el padding más pequeño
      result.push(
        <button
          key={`fragment-${fragment.index}`}
          onClick={() => handleConfirmFragment(fragment.index)}
          className="mx-1 px-1.5 py-0.5 bg-gray-200 rounded-md inline-flex items-center text-gray-900 cursor-pointer"
        >
          {fragment.text}
          <span className="material-icons ml-1 text-sm">
            {fragment.confirmed ? (
              <span className="material-icons text-green-500">check_circle</span>
            ) : (
              <span className="material-icons text-amber-500">warning</span>
            )}
          </span>
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
      // Reset height para evitar que solo crezca
      textareaRef.current.style.height = "auto";
      // Establecer la altura basada en el contenido
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
    }
  }, [text, isProcessed]);

  return (
    <div className="input-area flex flex-col w-full">
      <div className="flex-grow bg-transparent p-4 min-h-[100px] relative">
        {isProcessed ? (
          <div className="text-base text-gray-800 min-h-[100px]">
            {renderHighlightedText()}
          </div>
        ) : (
          <>
            <textarea
              ref={textareaRef}
              className="w-full bg-transparent resize-none text-base text-gray-800 outline-none min-h-[100px]"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              rows={5}
              style={{ overflow: 'hidden' }}
            />
            {!isFocused && text === "" && (
              <div className="absolute top-4 left-4 text-gray-500 pointer-events-none">
                Escriba su consulta...
              </div>
            )}
          </>
        )}
      </div>
      <div className="flex justify-end p-1 px-2 items-center space-x-1">
        {/* RESET button*/}
        {isProcessed && (
          <button
            onClick={() => {
              setIsProcessed(false);
              setText("");
              setHighlightedFragments([]);
            }}
            className="btn-primary text-sm py-1 px-2.5"
          >
            RESET
            <span className="material-icons ml-1 text-sm">
              refresh
            </span>
          </button>
        )}
        
        {/* SEND button */}
        <div className="relative">
          <button
            onClick={handleSend}
            disabled={(text.trim() === "" && !isProcessed) || (isProcessed && !allFragmentsConfirmed)}
            className={`btn-secondary text-sm py-1 px-2.5 ${(text.trim() === "" && !isProcessed) || (isProcessed && !allFragmentsConfirmed) ? "opacity-50 cursor-not-allowed" : ""}`}
            onMouseEnter={() => {
              if (isProcessed && !allFragmentsConfirmed) {
                setShowTooltip(true);
              }
            }}
            onMouseLeave={() => {
              setShowTooltip(false);
            }}
          >
            SEND
            <span className="material-icons ml-1 text-sm">
              send
            </span>
          </button>
          {showTooltip && isProcessed && !allFragmentsConfirmed && (
            <div className="absolute bottom-full right-0 mb-2 px-3 py-1.5 bg-gray-800 text-white text-xs rounded-md shadow-lg whitespace-nowrap z-10">
              Confirme todos los términos resaltados
              <div className="absolute top-full left-3/4 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800"></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}