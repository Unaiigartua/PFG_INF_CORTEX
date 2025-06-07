import { useEffect, useState, useRef } from "react";
import { X, ChevronLeft, ChevronRight, Check } from "lucide-react";
import { useI18n } from "../context/I18nContext";
import config from "../config";

interface SimilarTerm {
  term: string;
  concept_id: string;
  similarity: number;
  preferred_term: string;
  semantic_tag: string;
}

interface TermValidationModalProps {
  term: string;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (selected: SimilarTerm[]) => void;
}

const ITEMS_PER_PAGE = 15;

export default function TermValidationModal({
  term,
  isOpen,
  onClose,
  onConfirm,
}: TermValidationModalProps) {
  const [terms, setTerms] = useState<SimilarTerm[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  const { t } = useI18n();

  useEffect(() => {
    if (isOpen && term) {
      setIsLoading(true);
      fetch(`${config.API_BASE_URL}/similar_db`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ term }),
      })
        .then((res) => res.json())
        .then((data) => {
          setTerms(data.results);
          setSelected(new Set());
          setCurrentPage(1);
        })
        .catch((err) => console.error(t('term_validation.error'), err))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen, term, t]);

  useEffect(() => {
    if (tableRef.current) {
      tableRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [currentPage]);

  const toggleSelect = (index: number) => {
    const updated = new Set(selected);
    if (updated.has(index)) {
      updated.delete(index);
    } else {
      updated.add(index);
    }
    setSelected(updated);
  };

  const handleConfirm = () => {
    const selectedTerms = Array.from(selected).map((i) => terms[i]);
    onConfirm(selectedTerms);
    onClose();
  };

  if (!isOpen) return null;

  const totalPages = Math.ceil(terms.length / ITEMS_PER_PAGE);
  const start = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedTerms = terms.slice(start, start + ITEMS_PER_PAGE);

  return (
    <div 
      className="modal-overlay"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div 
        className="modal-content w-full max-w-4xl max-h-[85vh] animate-fade-in-down m-4"
      >
        {/* Header */}
        <div className="modal-header">
          <h2 className="text-xl font-semibold">
            {t('term_validation.title')}: <span className="italic font-normal">{term}</span>
          </h2>
          <button 
            onClick={onClose}
            className="text-white/90 hover:text-white hover:bg-white/20 p-2 rounded-lg transition-all duration-200 hover:rotate-90"
          >
            <X className="icon-md" />
          </button>
        </div>

        {/* Content area */}
        <div className="p-6 overflow-auto max-h-[60vh]">
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
            </div>
          ) : (
            <>
              <div ref={tableRef} className="overflow-hidden rounded-xl border border-[var(--color-secondary)]/30 shadow-lg">
                {/* Tabla con estilos mejorados para modo oscuro */}
                <div className="term-validation-table bg-white dark:bg-[var(--color-background-soft)]">
                  <table className="w-full table-auto border-collapse text-sm">
                    <thead className="term-validation-header sticky top-0 z-10">
                      <tr>
                        <th className="p-4 w-12 font-semibold text-[var(--color-text)]">✓</th>
                        <th className="p-4 text-left font-semibold w-1/3 text-[var(--color-text)]">Term</th>
                        <th className="p-4 text-left font-semibold w-1/3 text-[var(--color-text)]">PT</th>
                        <th className="p-4 text-left font-semibold w-5/24 text-[var(--color-text)]">Tag</th>
                        <th className="p-4 text-left font-semibold w-3/24 text-[var(--color-text)]">Code</th>
                      </tr>
                    </thead>
                    <tbody>
                      {paginatedTerms.map((t, i) => {
                        const globalIndex = start + i;
                        return (
                          <tr
                            key={globalIndex}
                            className={`term-validation-row cursor-pointer ${
                              selected.has(globalIndex) ? "term-validation-row-selected" : ""
                            }`}
                          >
                            <td className="p-3 text-center">
                              <div className="flex justify-center">
                                <input
                                  type="checkbox"
                                  checked={selected.has(globalIndex)}
                                  onChange={() => toggleSelect(globalIndex)}
                                  className="term-validation-checkbox h-4 w-4 rounded cursor-pointer"
                                />
                              </div>
                            </td>
                            <td 
                              className="p-3 font-medium cursor-pointer transition-colors term-validation-term"
                              onClick={() => toggleSelect(globalIndex)}
                            >
                              {t.term}
                            </td>
                            <td 
                              className="p-3 cursor-pointer transition-colors term-validation-pt"
                              onClick={() => toggleSelect(globalIndex)}
                            >
                              {t.preferred_term}
                            </td>
                            <td 
                              className="p-3 cursor-pointer"
                              onClick={() => toggleSelect(globalIndex)}
                            >
                              <span className="term-validation-badge">
                                {t.semantic_tag}
                              </span>
                            </td>
                            <td 
                              className="p-3 font-mono font-medium cursor-pointer transition-colors term-validation-code"
                              onClick={() => toggleSelect(globalIndex)}
                            >
                              {t.concept_id}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* PAGINATION con estilos mejorados */}
              {totalPages > 1 && (
                <div className="flex justify-between items-center mt-6 text-sm">
                  <span className="term-validation-pagination-info">
                    {start + 1}–{Math.min(start + ITEMS_PER_PAGE, terms.length)} {t('term_validation.of')}{" "}
                    {terms.length}
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                      disabled={currentPage === 1}
                      className="term-validation-nav-btn disabled:opacity-40"
                    >
                      <ChevronLeft className="icon-sm mr-1" />
                      {t('term_validation.previous')}
                    </button>
                    <button
                      onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                      disabled={currentPage === totalPages}
                      className="term-validation-nav-btn disabled:opacity-40"
                    >
                      {t('term_validation.next')}
                      <ChevronRight className="icon-sm ml-1" />
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* BUTTONS con estilos mejorados */}
        <div className="term-validation-footer">
          <button
            onClick={onClose}
            className="term-validation-cancel-btn"
          >
            {t('term_validation.cancel')}
          </button>
          <button
            onClick={handleConfirm}
            disabled={selected.size === 0}
            className={`btn-primary ${selected.size === 0 ? 'opacity-60 cursor-not-allowed' : ''}`}
          >
            {t('term_validation.confirm')}
            <Check className="icon-sm" />
          </button>
        </div>
      </div>
    </div>
  );
}