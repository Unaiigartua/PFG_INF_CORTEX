import { useEffect, useState, useRef } from "react";
import { X, ChevronLeft, ChevronRight, Check } from "lucide-react";
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

  useEffect(() => {
    if (isOpen && term) {
      setIsLoading(true);
      fetch(`${config.API_BASE_URL}/test`, {
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
        .catch((err) => console.error("Error fetching similar terms:", err))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen, term]);

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
            Validate Term: <span className="italic font-normal">{term}</span>
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
              <div ref={tableRef} className="overflow-hidden rounded-xl border border-[var(--color-secondary)]/30 shadow-lg bg-white">
                <table className="w-full table-auto border-collapse text-sm text-[var(--color-text)]">
                  <thead className="table-header sticky top-0 z-10">
                    <tr>
                      <th className="p-4 w-12 font-semibold">✓</th>
                      <th className="p-4 text-left font-semibold w-1/3">Term</th>
                      <th className="p-4 text-left font-semibold w-1/3">PT</th>
                      <th className="p-4 text-left font-semibold w-1/6">Tag</th>
                      <th className="p-4 text-left font-semibold w-1/6">Code</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedTerms.map((t, i) => {
                      const globalIndex = start + i;
                      return (
                        <tr
                          key={globalIndex}
                          className={`table-row cursor-pointer ${
                            selected.has(globalIndex) ? "bg-[var(--color-primary)]/10 border-[var(--color-primary)]/20" : ""
                          }`}
                        >
                          <td className="p-3 text-center">
                            <div className="flex justify-center">
                              <input
                                type="checkbox"
                                checked={selected.has(globalIndex)}
                                onChange={() => toggleSelect(globalIndex)}
                                className="h-4 w-4 rounded border-[var(--color-secondary)] text-[var(--color-primary)] focus:ring-[var(--color-primary)] cursor-pointer"
                              />
                            </div>
                          </td>
                          <td 
                            className="p-3 font-medium text-[var(--color-text)] cursor-pointer hover:text-[var(--color-primary)] transition-colors"
                            onClick={() => toggleSelect(globalIndex)}
                          >
                            {t.term}
                          </td>
                          <td 
                            className="p-3 text-[var(--color-text-light)] cursor-pointer hover:text-[var(--color-text)] transition-colors"
                            onClick={() => toggleSelect(globalIndex)}
                          >
                            {t.preferred_term}
                          </td>
                          <td 
                            className="p-3 cursor-pointer"
                            onClick={() => toggleSelect(globalIndex)}
                          >
                            <span className="badge badge-secondary">
                              {t.semantic_tag}
                            </span>
                          </td>
                          <td 
                            className="p-3 font-mono text-[var(--color-accent)] font-medium cursor-pointer hover:text-[var(--color-accent-dark)] transition-colors"
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

              {/* PAGINATION */}
              {totalPages > 1 && (
                <div className="flex justify-between items-center mt-6 text-sm text-text-light">
                  <span className="bg-background-soft px-3 py-2 rounded-lg font-medium border border-secondary/20">
                    {start + 1}–{Math.min(start + ITEMS_PER_PAGE, terms.length)} of{" "}
                    {terms.length}
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                      disabled={currentPage === 1}
                      className="btn-ghost px-3 py-2 disabled:opacity-40"
                    >
                      <ChevronLeft className="icon-sm mr-1" />
                      Anterior
                    </button>
                    <button
                      onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                      disabled={currentPage === totalPages}
                      className="btn-ghost px-3 py-2 disabled:opacity-40"
                    >
                      Siguiente
                      <ChevronRight className="icon-sm ml-1" />
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* BUTTONS */}
        <div className="p-6 flex justify-end space-x-4 border-t border-[var(--color-background-soft)] bg-gradient-to-r from-white to-[var(--color-background-soft)]">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-100 hover:bg-gray-200 text-[var(--color-text)] font-medium rounded-xl transition-all duration-200 border border-gray-300"
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirm}
            disabled={selected.size === 0}
            className={`btn-primary ${selected.size === 0 ? 'opacity-60 cursor-not-allowed' : ''}`}
          >
            Confirmar selección
            <Check className="icon-sm" />
          </button>
        </div>
      </div>
    </div>
  );
}