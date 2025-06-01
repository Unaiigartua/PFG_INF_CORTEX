module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: ['class', '[data-theme="dark"]'], // Habilitar modo oscuro basado en data-theme
  theme: {
    extend: {
      colors: {
        // Colores modo claro (conservados tal como estaban)
        'primary': {
          DEFAULT: '#4a9d7a',
          light: '#6db89a',
          dark: '#2d7a5a',
        },
        'secondary': {
          DEFAULT: '#8fadca',
          light: '#b5c9df',
          dark: '#6b8db0',
        },
        'accent': {
          DEFAULT: '#a584c7',
          light: '#c4a9d9',
          dark: '#8b6fb5',
        },
        'background': {
          DEFAULT: '#f0f9f6',
          soft: '#e8f5f0',
          accent: '#f5f0ff',
        },
        'text': {
          DEFAULT: '#1a2e23',
          light: '#4a6b56',
          muted: '#7a9485',
        },
        // Colores de estado vibrantes (conservados)
        'success': '#16a34a',
        'warning': '#ea580c',
        'error': '#dc2626',
        'info': '#0284c7',
        
        // Nuevos colores para modo oscuro
        'dark': {
          'primary': {
            DEFAULT: '#6ea085',
            light: '#8bb399',
            dark: '#5a8a71',
          },
          'secondary': {
            DEFAULT: '#acb1c8',
            light: '#c1c5d6',
            dark: '#969bb5',
          },
          'accent': {
            DEFAULT: '#9f90b6',
            light: '#b5a8c9',
            dark: '#8a79a3',
          },
          'background': {
            DEFAULT: '#0a0f0b',
            soft: '#0f1711',
            accent: '#0e0d12',
          },
          'text': {
            DEFAULT: '#fcfdfd',
            light: '#d0d5d2',
            muted: '#a0a8a3',
          },
        }
      },
      backgroundImage: {
        'vibrant-gradient': 'linear-gradient(135deg, #f0f9f6 0%, #e8f5f0 25%, #f5f0ff 50%, #e8f5f0 75%, #f0f9f6 100%)',
        'vibrant-gradient-dark': 'linear-gradient(135deg, #0a0f0b 0%, #0f1711 25%, #0e0d12 50%, #0f1711 75%, #0a0f0b 100%)',
        'glass-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1))',
        'glass-gradient-dark': 'linear-gradient(135deg, rgba(15, 23, 17, 0.3), rgba(15, 23, 17, 0.1))',
      },
      boxShadow: {
        'inner-custom': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
        'soft': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'medium': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'large': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'vibrant': '0 20px 40px -12px rgba(74, 157, 122, 0.3), 0 8px 16px -4px rgba(165, 132, 199, 0.2)',
        'glow': '0 0 20px rgba(74, 157, 122, 0.3), 0 0 40px rgba(165, 132, 199, 0.2)',
        // Sombras para modo oscuro
        'vibrant-dark': '0 20px 40px -12px rgba(110, 160, 133, 0.2), 0 8px 16px -4px rgba(159, 144, 182, 0.1)',
        'glow-dark': '0 0 20px rgba(110, 160, 133, 0.2), 0 0 40px rgba(159, 144, 182, 0.1)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in-down': 'fadeInDown 0.4s ease-out forwards',
        'slide-in-left': 'slideInLeft 0.4s ease-out forwards',
        'pulse-gentle': 'pulse-gentle 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      backdropBlur: {
        'xs': '2px',
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px',
      },
      blur: {
        '4xl': '72px',
      }
    },
  },
  plugins: [],
}