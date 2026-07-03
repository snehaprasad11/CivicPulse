/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        civic: {
          ink: "#122024",
          teal: "#155e75",
          mint: "#5eead4",
          clay: "#b45309",
          rose: "#be123c"
        }
      }
    }
  },
  plugins: []
};
