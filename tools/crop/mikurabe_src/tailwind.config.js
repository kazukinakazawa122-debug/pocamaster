/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "var(--paper)", surface: "var(--surface)", ink: "var(--ink)", muted: "var(--muted)",
        line: "var(--line)", ng: "var(--ng)", flag: "var(--flag)", flagbg: "var(--flagbg)",
      },
      fontFamily: { display: ['"Zen Maru Gothic"', '"Hiragino Maru Gothic ProN"', "system-ui", "sans-serif"] },
    },
  },
  plugins: [],
};
