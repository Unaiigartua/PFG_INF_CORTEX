import { useState, useRef } from "react";
import { Play, RefreshCw, CheckCircle, AlertCircle, ChevronDown, ChevronUp, Edit3 } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import Editor from '@monaco-editor/react';
import { useTheme } from "../context/ThemeContext";
import type { editor } from 'monaco-editor';

interface MedicalTerm {
  term: string;
  concept_id: string;
  preferred_term?: string;
  similarity?: number;
  semantic_tag?: string;
}

interface SQLResult {
  question: string;
  generated_sql: string;
  is_executable: boolean;
  error_message?: string;
  attempts_count: number;
  similar_example?: {
    question: string;
    sql: string;
    score: number;
  };
}

interface SQLResultViewProps {
  result: SQLResult;
  validatedTerms: Array<{text: string, snomedTerms: MedicalTerm[]}>;
  onNewQuery: () => void;
  onEditQuery: () => void;
}

export default function SQLResultView({ 
  result, 
  validatedTerms, 
  onNewQuery, 
  onEditQuery 
}: SQLResultViewProps) {
  const [sqlCode, setSqlCode] = useState(result.generated_sql);
  const [showErrorDetails, setShowErrorDetails] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const { t } = useI18n();
  const { theme } = useTheme();
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleExecute = async () => {
    setIsExecuting(true);
    // TODO: Implementar ejecución real
    setTimeout(() => {
      setIsExecuting(false);
      console.log("SQL ejecutado:", sqlCode);
    }, 2000);
  };

  const monacoTheme = theme === 'dark' ? 'vs-dark' : 'vs';

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 animate-fade-in-down">
      
      {/* HEADER: Consulta original y términos validados */}
      <div className="card">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-lg font-semibold text-[var(--color-primary)] mb-3">
            Consulta Original
          </h3>
          <button
            onClick={onEditQuery}
            className="btn-ghost text-sm py-1 px-3"
            title="Editar consulta"
          >
            <Edit3 className="icon-sm mr-1" />
            Editar
          </button>
        </div>
        
        <p className="text-[var(--color-text)] mb-4 text-base leading-relaxed bg-[var(--color-background-soft)] p-4 rounded-xl border border-[var(--color-primary)]/20">
          {result.question}
        </p>

        <div className="space-y-2">
          <h4 className="text-sm font-medium text-[var(--color-text-light)]">
            Términos Validados:
          </h4>
          <div className="flex flex-wrap gap-2">
            {validatedTerms.map((termGroup, index) => 
              termGroup.snomedTerms.map((snomedTerm, snomedIndex) => (
                <div
                  key={`${index}-${snomedIndex}`}
                  className="inline-flex items-center gap-2 bg-[var(--color-success)]/10 border border-[var(--color-success)]/30 text-[var(--color-success)] px-3 py-1 rounded-lg text-sm font-medium"
                >
                  <span>{termGroup.text}</span>
                  <span className="text-[var(--color-success)]/70">→</span>
                  <span className="font-mono text-xs">
                    {snomedTerm.concept_id}
                  </span>
                  {snomedTerm.preferred_term && (
                    <span className="text-[var(--color-success)]/80 text-xs">
                      ({snomedTerm.preferred_term})
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* EDITOR SQL */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-[var(--color-secondary)]">
            Consulta SQL Generada
          </h3>
          <div className="text-sm text-[var(--color-text-muted)]">
            {result.attempts_count} intento{result.attempts_count !== 1 ? 's' : ''}
          </div>
        </div>

        <div className="border border-[var(--color-secondary)]/30 rounded-xl overflow-hidden shadow-lg">
          <Editor
            height="300px"
            defaultLanguage="sql"
            value={sqlCode}
            onChange={(value) => setSqlCode(value || "")}
            theme={monacoTheme}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              roundedSelection: false,
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 2,
              wordWrap: 'on',
              formatOnPaste: true,
              formatOnType: true,
            }}
            onMount={(editor) => {
              editorRef.current = editor;
            }}
          />
        </div>
      </div>

      {/* STATUS Y ACCIONES */}
      <div className="card">
        <div className="flex flex-col space-y-4">
          
          {/* Estado de ejecución */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {result.is_executable ? (
                <>
                  <CheckCircle className="icon-lg text-[var(--color-success)]" />
                  <span className="font-semibold text-[var(--color-success)]">
                     SQL Ejecutable
                  </span>
                </>
              ) : (
                <>
                  <AlertCircle className="icon-lg text-[var(--color-error)]" />
                  <span className="font-semibold text-[var(--color-error)]">
                     SQL No Ejecutable
                  </span>
                </>
              )}
            </div>

            {/* Botones de acción */}
            <div className="flex gap-3">
              <button
                onClick={onNewQuery}
                className="btn-secondary"
              >
                <RefreshCw className="icon-sm" />
                Nueva Consulta
              </button>
              
              <button
                onClick={handleExecute}
                disabled={!result.is_executable || isExecuting}
                className={`btn-primary ${
                  !result.is_executable ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isExecuting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                    Ejecutando...
                  </>
                ) : (
                  <>
                    <Play className="icon-sm" />
                    Ejecutar
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Detalles de error (colapsables) */}
          {!result.is_executable && result.error_message && (
            <div className="border-t border-[var(--color-error)]/20 pt-4">
              <button
                onClick={() => setShowErrorDetails(!showErrorDetails)}
                className="flex items-center gap-2 text-[var(--color-error)] hover:text-[var(--color-error)]/80 transition-colors text-sm font-medium"
              >
                {showErrorDetails ? (
                  <ChevronUp className="icon-sm" />
                ) : (
                  <ChevronDown className="icon-sm" />
                )}
                Ver detalles del error
              </button>
              
              {showErrorDetails && (
                <div className="mt-3 p-4 bg-[var(--color-error)]/5 border border-[var(--color-error)]/20 rounded-xl">
                  <p className="text-sm text-[var(--color-error)] font-mono leading-relaxed">
                    {result.error_message}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Ejemplo similar utilizado (si existe) */}
          {result.similar_example && (
            <div className="border-t border-[var(--color-secondary)]/20 pt-4">
              <details className="group">
                <summary className="cursor-pointer text-sm font-medium text-[var(--color-secondary)] hover:text-[var(--color-secondary-dark)] transition-colors list-none flex items-center gap-2">
                  <ChevronDown className="icon-sm group-open:rotate-180 transition-transform" />
                  Ejemplo similar utilizado (score: {(result.similar_example.score * 100).toFixed(1)}%)
                </summary>
                <div className="mt-3 p-4 bg-[var(--color-secondary)]/5 border border-[var(--color-secondary)]/20 rounded-xl space-y-2">
                  <p className="text-sm font-medium text-[var(--color-text)]">
                    Pregunta: {result.similar_example.question}
                  </p>
                  <pre className="text-xs font-mono text-[var(--color-text-muted)] bg-[var(--color-background)] p-2 rounded border overflow-x-auto">
{result.similar_example.sql}
                  </pre>
                </div>
              </details>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}