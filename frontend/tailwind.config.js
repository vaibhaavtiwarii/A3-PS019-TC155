/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        enterprise: {
          dark: '#020617',
          sidebar: '#0f172a',
          card: '#1e293b',
          border: '#1e293b',
          accent: '#3b82f6',
          muted: '#94a3b8',
        },
      },
    },
  },
  plugins: [],
}
