/**
 * Warehouse High-Contrast Theme
 *
 * Optimiert für:
 * - Industrielle Umgebungen (Staub, Schmutz)
 * - Sonnenlicht-Lesbarkeit
 * - Handschuh-Bedienung (XXL Touch Targets)
 * - Schnelle visuelle Erkennung (Kontrast)
 */

export const warehouseTheme = {
  name: 'warehouse',
  displayName: 'Lager-Terminal',

  // Farben (High Contrast - Schwarz/Gelb/Weiß)
  colors: {
    // Primärfarben
    background: '***REMOVED***1a1a1a',        // Fast Schwarz
    foreground: '***REMOVED***ffffff',        // Weiß
    primary: '***REMOVED***fbbf24',           // Amber/Gelb - Haupt-Akzent
    primaryForeground: '***REMOVED***000000', // Schwarz auf Gelb

    // UI-Elemente
    card: '***REMOVED***262626',              // Dunkelgrau
    cardForeground: '***REMOVED***ffffff',
    border: '***REMOVED***404040',            // Mittelgrau
    input: '***REMOVED***333333',
    inputForeground: '***REMOVED***ffffff',

    // Semantische Farben (verstärkt)
    success: '***REMOVED***22c55e',           // Grün
    successForeground: '***REMOVED***000000',
    warning: '***REMOVED***fbbf24',           // Gelb
    warningForeground: '***REMOVED***000000',
    error: '***REMOVED***ef4444',             // Rot
    errorForeground: '***REMOVED***ffffff',
    info: '***REMOVED***3b82f6',              // Blau
    infoForeground: '***REMOVED***ffffff',

    // Status-Farben für Lager
    eingang: '***REMOVED***22c55e',           // Grün - Wareneingang
    ausgang: '***REMOVED***f97316',           // Orange - Warenausgang
    inventur: '***REMOVED***8b5cf6',          // Violett - Inventur
    umlagerung: '***REMOVED***06b6d4',        // Cyan - Umlagerung
  },

  // Typografie (größer für Lesbarkeit)
  typography: {
    fontFamily: 'system-ui, -apple-system, sans-serif',
    sizes: {
      xs: '0.875rem',   // 14px
      sm: '1rem',       // 16px
      base: '1.125rem', // 18px
      lg: '1.25rem',    // 20px
      xl: '1.5rem',     // 24px
      '2xl': '1.875rem', // 30px
      '3xl': '2.25rem',  // 36px
    },
  },

  // Spacing (größer für Touch)
  spacing: {
    touchTarget: '60px',      // Minimum Touch Target
    buttonPadding: '1.5rem',  // 24px
    cardPadding: '1.5rem',
    gap: '1rem',
  },

  // Border Radius (reduziert für industriellen Look)
  borderRadius: {
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
  },
}

/**
 * CSS Custom Properties für Warehouse Theme
 */
export const warehouseThemeCSS = `
  .theme-warehouse {
    /* Background & Foreground */
    --background: 0 0% 10%;
    --foreground: 0 0% 100%;

    /* Card */
    --card: 0 0% 15%;
    --card-foreground: 0 0% 100%;

    /* Popover */
    --popover: 0 0% 15%;
    --popover-foreground: 0 0% 100%;

    /* Primary - Amber/Gelb */
    --primary: 43 96% 56%;
    --primary-foreground: 0 0% 0%;

    /* Secondary */
    --secondary: 0 0% 20%;
    --secondary-foreground: 0 0% 100%;

    /* Muted */
    --muted: 0 0% 20%;
    --muted-foreground: 0 0% 70%;

    /* Accent */
    --accent: 43 96% 56%;
    --accent-foreground: 0 0% 0%;

    /* Destructive */
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 100%;

    /* Border & Input */
    --border: 0 0% 25%;
    --input: 0 0% 20%;
    --ring: 43 96% 56%;

    /* Radius */
    --radius: 0.375rem;

    /* Custom Warehouse Colors */
    --warehouse-eingang: 142 71% 45%;
    --warehouse-ausgang: 25 95% 53%;
    --warehouse-inventur: 263 70% 50%;
    --warehouse-umlagerung: 187 94% 43%;
  }

  /* Größere Touch Targets im Warehouse Theme */
  .theme-warehouse button,
  .theme-warehouse [role="button"],
  .theme-warehouse input,
  .theme-warehouse select,
  .theme-warehouse a {
    min-height: 60px;
    min-width: 60px;
  }

  .theme-warehouse input[type="checkbox"],
  .theme-warehouse input[type="radio"] {
    min-height: 32px;
    min-width: 32px;
  }

  /* Größere Schrift */
  .theme-warehouse {
    font-size: 18px;
  }

  .theme-warehouse h1 {
    font-size: 2.25rem;
    font-weight: 700;
  }

  .theme-warehouse h2 {
    font-size: 1.875rem;
    font-weight: 600;
  }

  .theme-warehouse h3 {
    font-size: 1.5rem;
    font-weight: 600;
  }

  /* Verstärkter Focus-Ring */
  .theme-warehouse :focus-visible {
    outline: 4px solid hsl(var(--ring));
    outline-offset: 2px;
  }
`

/**
 * Hook zum Aktivieren des Warehouse Themes
 */
export function applyWarehouseTheme(): void {
  document.documentElement.classList.add('theme-warehouse')
  document.documentElement.classList.remove('dark', 'light')
}

/**
 * Hook zum Deaktivieren des Warehouse Themes
 */
export function removeWarehouseTheme(): void {
  document.documentElement.classList.remove('theme-warehouse')
}
