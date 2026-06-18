/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/admin/developer/**/*.html",
    "./templates/admin/developer/*.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#7fb04f',
          dark: 'hsl(94, 42%, 36%)',
        },
        bg: {
          DEFAULT: 'hsl(210, 12%, 7%)',
        },
        surface: {
          DEFAULT: 'hsla(210, 12%, 14%, 0.65)',
          border: 'hsla(210, 15%, 35%, 0.25)',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
