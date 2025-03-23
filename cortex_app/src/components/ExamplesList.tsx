const examples = [
    "Find female patients with metastatic breast cancer who had mastectomy in the past year",
    "Patients diagnosed with angiomyxoma",
    "Find patients with stage II melanoma who received immunotherapy",
    "Patients diagnosed in the lower inner quadrant of breast that went under lumpectomy",
  ];
  
  export default function ExamplesList() {
    return (
      <div className="examples-card">
        <h2 className="font-semibold text-center mb-6 text-[#5e35b1]">Examples</h2>
        <ul className="space-y-4">
          {examples.map((example, index) => (
            <li key={index} className="flex hover:bg-white/50 p-2 rounded-md transition-colors">
              <span className="mr-2 text-[#5e35b1] font-bold">•</span>
              <span className="text-sm">{example}</span>
            </li>
          ))}
        </ul>
      </div>
    );
  }