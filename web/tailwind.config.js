/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // 538-inspired brand colors
        brand: {
          orange: '#ED713A',
          'orange-hover': '#D85F2E',
          black: '#000000',
        },
        // UI palette (light mode)
        ui: {
          bg: '#FFFFFF',
          surface: '#F7F7F8',
          card: '#FFFFFF',
          border: '#E5E7EB',
        },
        text: {
          primary: '#111827',
          muted: '#6B7280',
        },
        primary: {
          DEFAULT: '#ED713A',
          hover: '#D85F2E',
        },
        secondary: {
          DEFAULT: '#30A2DA',
        },
        success: '#6D904F',
        warning: '#E5AE38',
        neutral: '#8B8B8B',
        // Chart palette (categorical)
        chart: {
          1: '#30A2DA',
          2: '#ED713A',
          3: '#6D904F',
          4: '#E5AE38',
          5: '#8B8B8B',
          6: '#4E79A7',
          7: '#F28E2B',
          8: '#59A14F',
          9: '#E15759',
          10: '#B07AA1',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['var(--font-ibm-plex-mono)', 'IBM Plex Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
