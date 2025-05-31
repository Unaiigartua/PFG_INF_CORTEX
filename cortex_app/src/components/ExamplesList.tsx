interface ExamplesListProps {
  onSelectExample: (example: string) => void;
}

const examples = [
  "Find female patients with metastatic breast cancer who had mastectomy in the past year",
  "Female patients diagnosed with a paget disease",
  "Female patients diagnosed with adenosquamous carcinoma of the lung",
  "Patients diagnosed in the lower inner quadrant of breast that went under lumpectomy",
];

export default function ExamplesList({ onSelectExample }: ExamplesListProps) {
  return (
    <div className="examples-card animate-fade-in-down" style={{ animationDelay: '0.6s' }}>
      <h2 className="font-bold text-xl text-center mb-5 text-[var(--color-accent)] bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-light)] bg-clip-text text-transparent">
        Examples
      </h2>
      <ul className="space-y-3">
        {examples.map((example, index) => (
          <li 
            key={index} 
            className="group flex items-start hover:bg-gradient-to-r hover:from-white/60 hover:to-[var(--color-accent)]/10 p-3 rounded-xl transition-all duration-300 cursor-pointer hover:shadow-lg border border-transparent hover:border-[var(--color-accent)]/20"
            onClick={() => onSelectExample(example)}
            style={{ animationDelay: `${0.8 + index * 0.1}s` }}
          >
            <span className="mr-3 text-[var(--color-accent)] font-bold text-lg group-hover:scale-110 transition-transform duration-300 flex-shrink-0">
              •
            </span>
            <span className="text-sm text-[var(--color-text)] group-hover:text-[var(--color-text-light)] transition-colors duration-300 leading-relaxed">
              {example}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}