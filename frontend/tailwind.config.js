/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        sidebar: '#1e293b',
        accent: '#3b82f6',
      },
    },
  },
  plugins: [],
};
