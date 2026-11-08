/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        display: ["'Syne'", "sans-serif"],
        body: ["'DM Sans'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      colors: {
        brand: {
          50:  "#f0f4ff",
          100: "#e0eaff",
          200: "#c7d7fe",
          300: "#a5bafd",
          400: "#8195fa",
          500: "#6272f5",
          600: "#4f51e8",
          700: "#4040ce",
          800: "#3535a7",
          900: "#2f3083",
          950: "#1d1e52",
        },
        accent: {
          cyan:   "#00d4ff",
          violet: "#8b5cf6",
          pink:   "#ec4899",
          emerald:"#10b981",
          amber:  "#f59e0b",
        },
      },
      backgroundImage: {
        "mesh-gradient": "radial-gradient(at 40% 20%, hsla(228,100%,74%,0.15) 0, transparent 50%), radial-gradient(at 80% 0%, hsla(189,100%,56%,0.10) 0, transparent 50%), radial-gradient(at 0% 50%, hsla(355,100%,93%,0.08) 0, transparent 50%)",
        "card-shine": "linear-gradient(135deg, rgba(255,255,255,0.07) 0%, transparent 60%)",
      },
      animation: {
        "fade-up":     "fadeUp 0.5s ease forwards",
        "fade-in":     "fadeIn 0.4s ease forwards",
        "slide-right": "slideRight 0.4s ease forwards",
        "pulse-slow":  "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "spin-slow":   "spin 3s linear infinite",
        "bounce-sm":   "bounceSm 1s infinite",
        shimmer:       "shimmer 2s linear infinite",
        glow:          "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        fadeUp: {
          "0%":   { opacity: 0, transform: "translateY(20px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        fadeIn: {
          "0%":   { opacity: 0 },
          "100%": { opacity: 1 },
        },
        slideRight: {
          "0%":   { opacity: 0, transform: "translateX(-20px)" },
          "100%": { opacity: 1, transform: "translateX(0)" },
        },
        bounceSm: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":      { transform: "translateY(-4px)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        glow: {
          "0%":   { boxShadow: "0 0 20px rgba(98, 114, 245, 0.3)" },
          "100%": { boxShadow: "0 0 40px rgba(98, 114, 245, 0.6)" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
