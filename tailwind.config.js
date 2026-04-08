/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#050505",
        primary: "#00F3FF",
        secondary: "#BD00FF",
        charcoal: "#0e0e0e",
      },
      fontFamily: {
        syne: ["Syne", "sans-serif"],
        manrope: ["Manrope", "sans-serif"],
      },
      backdropBlur: {
        '20px': '20px',
      },
      transitionDuration: {
        '300': '300ms',
      }
    },
  },
  plugins: [],
}
