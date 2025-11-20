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
          dark: '#050b14',
          panel: 'rgba(10, 20, 40, 0.7)',
          blue: '#00f3ff', // Cyan neon
          blueDim: 'rgba(0, 243, 255, 0.1)',
          red: '#ff2a2a', // Alert red
          text: '#e0f7ff',
        },
      },
      fontFamily: {
        hud: ['Orbitron', 'sans-serif'],
        body: ['Rajdhani', 'sans-serif'],
      },
      boxShadow: {
        'neon-blue': '0 0 10px rgba(0, 243, 255, 0.5), 0 0 20px rgba(0, 243, 255, 0.3)',
        'neon-red': '0 0 10px rgba(255, 42, 42, 0.5)',
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
