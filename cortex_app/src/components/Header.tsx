export default function Header() {
    return (
      <div className="flex items-center gap-4">
        <button className="btn-primary">
          <span className="material-icons text-sm">person_outline</span>
          <span>Log In</span>
        </button>
        <div className="flex gap-2">
          <img src="src/assets/es-flag.png" alt="Español" className="w-8 h-6 rounded shadow hover:shadow-md transition-shadow cursor-pointer" />
          <img src="src/assets/us-flag.png" alt="English" className="w-8 h-6 rounded shadow hover:shadow-md transition-shadow cursor-pointer" />
        </div>
      </div>
    );
  }