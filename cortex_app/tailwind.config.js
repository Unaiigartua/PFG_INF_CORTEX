module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cortex-primary': '#146a8c',
        'cortex-secondary': '#a8d0d0',
        'cortex-accent': '#5e35b1',
        'cortex-background': '#eaf3f3',
      },
      boxShadow: {
        'inner-custom': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}