/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#FAF9F5",
        surface: "#FFFFFF",
        ink: "#1B1A17",
        "ink-muted": "#6B6558",
        border: "#E7E3D8",
        sidebar: "#14141A",
        "sidebar-ink": "#E8E6DF",
        danger: "#DC2626",
        "danger-soft": "#FEE2E2",
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      animation: {
        "pulse-dot": "pulse-dot 1.4s ease-in-out infinite",
      },
      keyframes: {
        "pulse-dot": {
          "0%, 80%, 100%": { transform: "scale(0.6)", opacity: "0.4" },
          "40%": { transform: "scale(1)", opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};
