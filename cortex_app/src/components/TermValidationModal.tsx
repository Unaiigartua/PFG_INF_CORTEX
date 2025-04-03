import { useEffect, useState } from "react";

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

  useEffect(() => {
    if (isOpen && term) {
      fetch("http://localhost:8000/similar", {
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
        .catch((err) => console.error("Error fetching similar terms:", err));
    }
  }, [isOpen, term]);

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
    <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl p-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">
          Validate Term: <span className="italic">{term}</span>
        </h2>

        <div className="overflow-x-auto max-h-[400px] rounded-lg border border-gray-100">
          <table className="w-full table-auto border-collapse text-sm text-gray-700">
            <thead className="bg-blue-50 text-gray-600">
              <tr>
                <th className="p-3">✓</th>
                <th className="p-3 text-left">Term</th>
                <th className="p-3 text-left">PT</th>
                <th className="p-3 text-left">Tag</th>
                <th className="p-3 text-left">Code</th>
              </tr>
            </thead>
            <tbody>
              {paginatedTerms.map((t, i) => {
                const globalIndex = start + i;
                return (
                  <tr
                    key={globalIndex}
                    className={globalIndex % 2 === 0 ? "bg-blue-100/40" : ""}
                  >
                    <td className="p-2 text-center">
                      <input
                        type="checkbox"
                        checked={selected.has(globalIndex)}
                        onChange={() => toggleSelect(globalIndex)}
                      />
                    </td>
                    <td className="p-2">{t.term}</td>
                    <td className="p-2">{t.preferred_term}</td>
                    <td className="p-2">{t.semantic_tag}</td>
                    <td className="p-2 font-mono text-blue-900">{t.concept_id}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* PAGINATION */}
        {totalPages > 1 && (
          <div className="flex justify-between items-center mt-4 text-sm text-gray-600">
            <span>
              {start + 1}–{Math.min(start + ITEMS_PER_PAGE, terms.length)} of{" "}
              {terms.length}
            </span>
            <div className="space-x-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                disabled={currentPage === 1}
                className="px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded disabled:opacity-50"
              >
                ← Prev
              </button>
              <button
                onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded disabled:opacity-50"
              >
                Next →
              </button>
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end space-x-2">
          <button
            onClick={onClose}
            className="bg-gray-200 px-4 py-2 rounded-md hover:bg-gray-300 text-sm"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
          >
            Confirm selection
          </button>
        </div>
      </div>
    </div>
  );
}
