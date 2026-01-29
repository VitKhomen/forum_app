/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Використовуємо class strategy
  theme: {
    extend: {
      colors: {
        // Можна додати кастомні кольори
      }
    },
  },
  plugins: [],
}