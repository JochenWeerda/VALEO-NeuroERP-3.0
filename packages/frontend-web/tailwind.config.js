/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "-apple-system", "BlinkMacSystemFont", "Segoe UI Variable", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      fontSize: {
        "2xs": ["var(--text-2xs)", { lineHeight: "1rem" }],
        xs:   ["var(--text-xs)",   { lineHeight: "1rem" }],
        sm:   ["var(--text-sm)",   { lineHeight: "1.25rem" }],
        base: ["var(--text-base)", { lineHeight: "1.5rem" }],
        lg:   ["var(--text-lg)",   { lineHeight: "1.75rem" }],
        xl:   ["var(--text-xl)",   { lineHeight: "2rem" }],
        "2xl":["var(--text-2xl)",  { lineHeight: "2.5rem" }],
        "3xl":["var(--text-3xl)",  { lineHeight: "3rem" }],
      },
      letterSpacing: {
        tight:   "var(--tracking-tight)",
        normal:  "var(--tracking-normal)",
        wide:    "var(--tracking-wide)",
        widest:  "var(--tracking-widest)",
      },
      lineHeight: {
        tight:   "var(--leading-tight)",
        snug:    "var(--leading-snug)",
        normal:  "var(--leading-normal)",
        relaxed: "var(--leading-relaxed)",
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        DEFAULT: "var(--shadow-md)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
        xl: "var(--shadow-xl)",
      },
      transitionDuration: {
        instant: "var(--duration-instant)",
        fast:    "var(--duration-fast)",
        normal:  "var(--duration-normal)",
        slow:    "var(--duration-slow)",
      },
      transitionTimingFunction: {
        spring: "var(--ease-spring)",
        "ease-out": "var(--ease-out)",
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        sm:   "var(--radius-sm)",
        md:   "var(--radius-md)",
        lg:   "var(--radius-lg)",
        xl:   "var(--radius-xl)",
        "2xl":"var(--radius-2xl)",
        DEFAULT: "var(--radius-lg)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
      /* Wave B 024: Touch-optimierte Ziele (Lager, Waage, Annahme) */
      minHeight: {
        "touch": "var(--touch-target, 44px)",
      },
      minWidth: {
        "touch": "var(--touch-target, 44px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}