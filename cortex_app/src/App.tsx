import { useState } from "react";
import Home from "./pages/Home";
import { AuthProvider } from "./context/AuthContext";
import LoginModal from "./components/LoginModal";

function App() {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  return (
    <AuthProvider>
      <Home onLoginClick={() => setIsLoginModalOpen(true)} />
      <LoginModal 
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onLoginSuccess={(token) => {
          // Aquí usarías el token para autenticar
          setIsLoginModalOpen(false);
        }}
      />
    </AuthProvider>
  );
}

export default App;