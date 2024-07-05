/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*"],
  theme: {
    fontFamily: {
      OverPass: ["Overpass", "sans-serif"],
    },
    extend: {
      colors: {
        white: "#fff",
        customGreen: "#003C43",
        secendGreen: "#135D66",
        therdGreen: "#77B0AA",
        LightGreen: "#E3FEF7",
        DarkGray: " #868686",
        LightGray: "#F5F5F5",
      },
    },
  },
  plugins: [],
}


