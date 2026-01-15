/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        omnix: {
          bg: {
            dark: '#030610',
            panel: 'rgba(8, 14, 28, 0.90)',
          },
          primary: '#00f0ff',
          primaryDim: 'rgba(0, 240, 255, 0.15)',
          secondary: '#ff0099',
          secondaryDim: 'rgba(255, 0, 153, 0.15)',
          accent: '#fcee0a',
          text: {
            primary: '#e0f7ff',
            secondary: '#94a3b8',
          }
        },
      },
      fontFamily: {
        hud: ['Orbitron', 'sans-serif'],
        body: ['Rajdhani', 'sans-serif'],
      },
      boxShadow: {
        'neon-cyan': '0 0 10px rgba(0, 240, 255, 0.5), 0 0 20px rgba(0, 240, 255, 0.3)',
        'neon-magenta': '0 0 10px rgba(255, 0, 153, 0.5), 0 0 20px rgba(255, 0, 153, 0.3)',
      },
      animation: {
        'spin-slow': 'spin 8s linear infinite',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
}
