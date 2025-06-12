import { ReactNode } from 'react';
import { createPortal } from 'react-dom';

interface ModalPortalProps {
  children: ReactNode;
}

export default function ModalPortal({ children }: ModalPortalProps) {
  // Crear un div para el portal si no existe
  const modalRoot = document.getElementById('modal-root');
  
  if (!modalRoot) {
    const div = document.createElement('div');
    div.id = 'modal-root';
    document.body.appendChild(div);
  }
  
  // Usar el portal para renderizar el modal directamente en el body
  return createPortal(
    children,
    document.getElementById('modal-root') || document.body
  );
}