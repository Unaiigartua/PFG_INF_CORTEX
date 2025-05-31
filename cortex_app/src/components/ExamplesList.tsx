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
    <div className="examples-card">
      <h2 className="font-semibold text-center mb-6 text-[#5e35b1]">Examples</h2>
      <ul className="space-y-4">
        {examples.map((example, index) => (
          <li 
            key={index} 
            className="flex hover:bg-white/50 p-2 rounded-md transition-colors cursor-pointer"
            onClick={() => onSelectExample(example)}
          >
            <span className="mr-2 text-[#5e35b1] font-bold">•</span>
            <span className="text-sm">{example}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}