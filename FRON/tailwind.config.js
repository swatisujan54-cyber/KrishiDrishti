/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Natural sage green — the primary brand color
        brand: {
          50:  '#f5f7f0',
          100: '#e8ecd9',
          200: '#cdd4b8',
          300: '#a8b88a',
          400: '#829c63',
          500: '#638046',
          600: '#4d6638',
          700: '#3d512c',
          800: '#2f3e22',
          900: '#232d19',
        },
        // Warm earth/brown for accents and text
        earth: {
          50:  '#faf7f2',
          100: '#f0e8dc',
          200: '#e0cdb4',
          300: '#c9a888',
          400: '#a8814f',
          500: '#8b6939',
          600: '#705530',
          700: '#5a4427',
          800: '#463520',
          900: '#36291a',
        },
        // Warm cream backgrounds
        cream: {
          50:  '#fdfcf8',
          100: '#faf7ef',
          200: '#f3eee0',
          300: '#ecddb8',
        },
        // Turmeric/amber for subtle highlights
        harvest: {
          400: '#e0a820',
          500: '#c89010',
          600: '#a87408',
        },
      },
    },
  },
  plugins: [],
}
