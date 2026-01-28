/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  darkMode: 'class',  // ← ОЦЕ КЛЮЧОВЕ! Змінює на class
  theme: {
    extend: {},
  },
  plugins: [],
}