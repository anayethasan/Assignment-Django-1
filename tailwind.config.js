/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./events/templates/**/*.html",
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Barlow', 'sans-serif'],
      },
    },
  },
  plugins: [],
};