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
        // 538-inspired palette
        primary: {
          DEFAULT: '#ED713A',
          dark: '#D85F2A',
        },
        blue: {
          DEFAULT: '#30A2DA',
          dark: '#2080B0',
        },
        green: '#2ECC71',
        yellow: '#F7DC6F',
        gray: {
          50: '#F7F7F7',
          100: '#E8E8E8',
          200: '#D4D4D4',
          300: '#B8B8B8',
          400: '#8A8A8A',
          500: '#5C5C5C',
          600: '#3F3F3F',
          700: '#2A2A2A',
          800: '#1A1A1A',
          900: '#0F0F0F',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
};
