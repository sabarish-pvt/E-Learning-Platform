/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e6ff",
          400: "#5b8def",
          500: "#3266d6",
          600: "#254fae",
          700: "#1c3d87",
        },
      },
    },
  },
  plugins: [],
};
