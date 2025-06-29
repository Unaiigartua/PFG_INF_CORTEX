import { useState, useRef } from "react";
import { RefreshCw, CheckCircle, AlertCircle, ChevronDown, ChevronUp, Edit3, Search } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import Editor from '@monaco-editor/react';
import { useTheme } from "../context/ThemeContext";
import { useAuth } from "../context/AuthContext";
import config from "../config";
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
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const { t } = useI18n();
  const { theme } = useTheme();
  const { token } = useAuth();
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleValidate = async () => {
    if (!token) {
      alert(t('sql_result.auth_required'));
      return;
    }

    setIsValidating(true);
    try {
      const response = await fetch(`${config.API_BASE_URL}/sql-generation/validate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          sql_query: sqlCode,
          question: result.question
        }),
      });

      if (!response.ok) {
        throw new Error(t('sql_result.validation_error'));
      }

      const validationData = await response.json();
      setValidationResult(validationData);
      
    } catch (err) {
      console.error("Error al validar SQL:", err);
      alert(t('sql_result.validation_error'));
    } finally {
      setIsValidating(false);
    }
  };

  const monacoTheme = theme === 'dark' ? 'vs-dark' : 'vs';

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 animate-fade-in-down">
      
      {/* HEADER: Consulta original y términos validados */}
      <div className="card">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-lg font-semibold text-[var(--color-primary)] mb-3">
            {t('sql_result.original_query')}
          </h3>
          <button
            onClick={onEditQuery}
            className="btn-ghost text-sm py-1 px-3"
            title={t('sql_result.edit_query')}
          >
            <Edit3 className="icon-sm mr-1" />
            {t('sql_result.edit')}
          </button>
        </div>
        
        <p className="text-[var(--color-text)] mb-4 text-base leading-relaxed bg-[var(--color-background-soft)] p-4 rounded-xl border border-[var(--color-primary)]/20">
          {result.question}
        </p>

        <div className="space-y-2">
          <h4 className="text-sm font-medium text-[var(--color-text-light)]">
            {t('sql_result.validated_terms')}:
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
            {t('sql_result.generated_sql')}
          </h3>
          <div className="text-sm text-[var(--color-text-muted)]">
            {result.attempts_count} {result.attempts_count === 1 ? t('sql_result.attempt') : t('sql_result.attempts')}
          </div>
        </div>

        <div className="border border-[var(--color-secondary)]/30 rounded-xl overflow-hidden shadow-lg">
          <Editor
            height="300px"
            defaultLanguage="sql"
            value={sqlCode}
            onChange={(value) => {
              setSqlCode(value || "");
              // Limpiar resultado de validación cuando se edita
              if (validationResult) {
                setValidationResult(null);
              }
            }}
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
          
          {/* Estado de ejecución/validación */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {validationResult ? (
                // Mostrar resultado de la validación
                <>
                  {validationResult.is_executable ? (
                    <>
                      <CheckCircle className="icon-lg text-[var(--color-success)]" />
                      <span className="font-semibold text-[var(--color-success)]">
                        {t('sql_result.valid_executable')}
                      </span>
                    </>
                  ) : validationResult.is_valid ? (
                    <>
                      <AlertCircle className="icon-lg text-[var(--color-warning)]" />
                      <span className="font-semibold text-[var(--color-warning)]">
                        {t('sql_result.valid_not_executable')}
                      </span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="icon-lg text-[var(--color-error)]" />
                      <span className="font-semibold text-[var(--color-error)]">
                        {t('sql_result.invalid')}
                      </span>
                    </>
                  )}
                </>
              ) : (
                // Mostrar resultado original si no se ha validado
                <>
                  {result.is_executable ? (
                    <>
                      <CheckCircle className="icon-lg text-[var(--color-success)]" />
                      <span className="font-semibold text-[var(--color-success)]">
                        {t('sql_result.executable_original')}
                      </span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="icon-lg text-[var(--color-error)]" />
                      <span className="font-semibold text-[var(--color-error)]">
                        {t('sql_result.not_executable_original')}
                      </span>
                    </>
                  )}
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
                {t('sql_result.new_query')}
              </button>
              
              <button
                onClick={handleValidate}
                disabled={isValidating || !sqlCode.trim()}
                className={`btn-primary ${
                  isValidating || !sqlCode.trim() ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isValidating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                    {t('sql_result.validating')}
                  </>
                ) : (
                  <>
                    <Search className="icon-sm" />
                    {t('sql_result.check_sql')}
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Detalles de error (colapsables) */}
          {((validationResult && !validationResult.is_valid) || (!validationResult && !result.is_executable)) && (
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
                {t('sql_result.view_error_details')}
              </button>
              
              {showErrorDetails && (
                <div className="mt-3 p-4 bg-[var(--color-error)]/5 border border-[var(--color-error)]/20 rounded-xl">
                  <p className="text-sm text-[var(--color-error)] font-mono leading-relaxed">
                    {validationResult ? 
                      (validationResult.syntax_error || validationResult.execution_error) : 
                      result.error_message
                    }
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Información adicional de validación */}
          {validationResult && (
            <div className="border-t border-[var(--color-secondary)]/20 pt-4">
              <details className="group">
                <summary className="cursor-pointer text-sm font-medium text-[var(--color-secondary)] hover:text-[var(--color-secondary-dark)] transition-colors list-none flex items-center gap-2">
                  <ChevronDown className="icon-sm group-open:rotate-180 transition-transform" />
                  {t('sql_result.validation_info')}
                </summary>
                <div className="mt-3 p-4 bg-[var(--color-secondary)]/5 border border-[var(--color-secondary)]/20 rounded-xl space-y-2">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-[var(--color-text)]">{t('sql_result.valid_syntax')}:</span>
                      <span className={`ml-2 ${validationResult.is_valid ? 'text-[var(--color-success)]' : 'text-[var(--color-error)]'}`}>
                        {validationResult.is_valid ? t('sql_result.yes') : t('sql_result.no')}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-[var(--color-text)]">{t('sql_result.executable')}:</span>
                      <span className={`ml-2 ${validationResult.is_executable ? 'text-[var(--color-success)]' : 'text-[var(--color-error)]'}`}>
                        {validationResult.is_executable ? t('sql_result.yes') : t('sql_result.no')}
                      </span>
                    </div>
                    {validationResult.execution_time && (
                      <div>
                        <span className="font-medium text-[var(--color-text)]">{t('sql_result.time')}:</span>
                        <span className="ml-2 text-[var(--color-text-muted)]">
                          {validationResult.execution_time.toFixed(3)}s
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </details>
            </div>
          )}

          {/* Ejemplo similar utilizado (si existe) - siempre mostrar el original */}
          {result.similar_example && (
            <div className="border-t border-[var(--color-secondary)]/20 pt-4">
              <details className="group">
                <summary className="cursor-pointer text-sm font-medium text-[var(--color-secondary)] hover:text-[var(--color-secondary-dark)] transition-colors list-none flex items-center gap-2">
                  <ChevronDown className="icon-sm group-open:rotate-180 transition-transform" />
                  {t('sql_result.similar_example')} ({t('sql_result.score')}: {(result.similar_example.score * 100).toFixed(1)}%)
                </summary>
                <div className="mt-3 p-4 bg-[var(--color-secondary)]/5 border border-[var(--color-secondary)]/20 rounded-xl space-y-2">
                  <p className="text-sm font-medium text-[var(--color-text)]">
                    {t('sql_result.example_question')}: {result.similar_example.question}
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