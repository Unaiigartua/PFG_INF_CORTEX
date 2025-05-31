import { useState } from "react";
import Home from "./pages/Home";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginModal from "./components/LoginModal";

function AppContent() {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const { login } = useAuth();

  const handleLoginSuccess = async (token: string) => {
    await login(token);
    setIsLoginModalOpen(false);
  };

  return (
    <>
      <Home onLoginClick={() => setIsLoginModalOpen(true)} />
      <LoginModal 
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;