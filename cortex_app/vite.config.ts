import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: '0.0.0.0', // Bind to all interfaces
    port: 5173,
    allowedHosts: ['.loca.lt', '.trycloudflare.com'] // Allow all loca.lt subdomains
  },
  plugins: [react(), tailwindcss()], 
})