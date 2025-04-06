import { useEffect, useState, useRef } from "react";
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
      className="fixed inset-0 bg-[#146a8c]/10 backdrop-blur-md flex justify-center items-center z-50 transition-opacity duration-300"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div 
        className="bg-white rounded-2xl shadow-xl w-full max-w-5xl p-0 border border-gray-100 overflow-hidden transform transition-all duration-300 animate-fadeIn"
        style={{ maxHeight: "95vh" }}
      >
        {/* Header with primary color background */}
        <div className="bg-gradient-to-r from-[#146a8c] to-[#2c87a8] text-white p-5 flex justify-between items-center">
          <h2 className="text-xl font-semibold">
            Validate Term: <span className="italic font-normal">{term}</span>
          </h2>
          <button 
            onClick={onClose}
            className="text-white/80 hover:text-white transition-colors p-1 hover:bg-white/10 rounded-full"
          >
            <span className="material-icons">close</span>
          </button>
        </div>

        {/* Content area with shadow separator */}
        <div className="p-6 overflow-auto" style={{ maxHeight: "calc(95vh - 180px)" }}>
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#146a8c]"></div>
            </div>
          ) : (
            <>
              <div ref={tableRef} className="overflow-hidden rounded-lg border border-[#a8d0d0]/50 shadow-sm">
                <table className="w-full table-auto border-collapse text-sm text-gray-700">
                  <thead className="bg-gradient-to-r from-[#a8d0d0]/30 to-[#eaf3f3]/50 text-gray-700">
                    <tr>
                      <th className="p-3" style={{ width: '40px' }}>✓</th>
                      <th className="p-3 text-left" style={{ width: '35%' }}>Term</th>
                      <th className="p-3 text-left" style={{ width: '35%' }}>PT</th>
                      <th className="p-3 text-left" style={{ width: '18%' }}>Tag</th>
                      <th className="p-3 text-left" style={{ width: '10%' }}>Code</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedTerms.map((t, i) => {
                      const globalIndex = start + i;
                      return (
                        <tr
                          key={globalIndex}
                          className={`border-b border-[#a8d0d0]/20 hover:bg-[#eaf3f3] transition-colors ${
                            selected.has(globalIndex) ? "bg-[#146a8c]/10" : ""
                          }`}
                          onClick={() => toggleSelect(globalIndex)}
                        >
                          <td className="p-3 text-center">
                            <div className="flex justify-center">
                              <input
                                type="checkbox"
                                checked={selected.has(globalIndex)}
                                onChange={(e) => e.stopPropagation()}
                                onClick={(e) => e.stopPropagation()}
                                className="h-4 w-4 rounded border-gray-300 text-[#146a8c] focus:ring-[#146a8c]"
                              />
                            </div>
                          </td>
                          <td className="p-3 font-medium">{t.term}</td>
                          <td className="p-3">{t.preferred_term}</td>
                          <td className="p-3 whitespace-nowrap">
                            <span className="px-2 py-1 rounded-full text-xs bg-[#a8d0d0]/30 text-[#146a8c]">
                              {t.semantic_tag}
                            </span>
                          </td>
                          <td className="p-3 font-mono text-[#5e35b1] font-medium">{t.concept_id}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* PAGINATION */}
              {totalPages > 1 && (
                <div className="flex justify-between items-center mt-5 text-sm text-gray-600">
                  <span className="bg-[#eaf3f3] px-3 py-1 rounded-md font-medium">
                    {start + 1}–{Math.min(start + ITEMS_PER_PAGE, terms.length)} of{" "}
                    {terms.length}
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                      disabled={currentPage === 1}
                      className="px-3 py-1.5 bg-[#a8d0d0]/20 hover:bg-[#a8d0d0]/40 rounded-md disabled:opacity-40 transition-colors border border-[#a8d0d0]/30 flex items-center"
                    >
                      <span className="material-icons text-sm mr-1">chevron_left</span>
                      Prev
                    </button>
                    <button
                      onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                      disabled={currentPage === totalPages}
                      className="px-3 py-1.5 bg-[#a8d0d0]/20 hover:bg-[#a8d0d0]/40 rounded-md disabled:opacity-40 transition-colors border border-[#a8d0d0]/30 flex items-center"
                    >
                      Next
                      <span className="material-icons text-sm ml-1">chevron_right</span>
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* BUTTONS */}
        <div className="p-5 flex justify-end space-x-3 border-t border-[#eaf3f3] bg-gradient-to-r from-white to-[#eaf3f3]/30">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-md hover:bg-gray-100 text-gray-700 transition-colors border border-gray-300 font-medium"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={selected.size === 0}
            className={`btn-primary ${selected.size === 0 ? 'opacity-60 cursor-not-allowed' : ''}`}
          >
            Confirm selection
            <span className="material-icons ml-1 text-sm">check</span>
          </button>
        </div>
      </div>
    </div>
  );
}