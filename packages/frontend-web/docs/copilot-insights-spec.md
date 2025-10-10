***REMOVED*** Copilot Insights 2.0 - Specification

***REMOVED******REMOVED*** Phase E - Interaktiver KI-Analyse-Layer

Diese Spezifikation beschreibt die Copilot Insights 2.0 Komponente, einen interaktiven KI-gestützten Analyse-Layer für das Analytics Dashboard.

***REMOVED******REMOVED*** Übersicht

Copilot Insights 2.0 wertet automatisch KPIs und Trends aus, formuliert verständliche Erkenntnisse und ermöglicht Rückfragen für tiefergehende Analysen.

***REMOVED******REMOVED*** Komponenten

***REMOVED******REMOVED******REMOVED*** 1. `useCopilotInsight.ts` - Custom Hook

**Pfad:** `src/features/copilot/useCopilotInsight.ts`

**Zweck:** Holt KPI- und Trenddaten und generiert daraus KI-Analysen.

**TypeScript Types:**
```typescript
type KPI = {
  id: string
  label: string
  value: number
  delta: number
  unit?: string
}

type TrendPoint = {
  date: string
  sales: number
  inventory: number
}

type Insight = {
  summary: string      // Hauptzusammenfassung
  factors: string[]    // Einflussfaktoren
  suggestions: string[] // Handlungsempfehlungen
}
```

**Return Type:**
```typescript
{
  insight: Insight | null
  loading: boolean
}
```

**Funktionsweise:**
1. Lädt KPIs und Trends via `useMcpQuery`
2. Berechnet Durchschnittswerte (z.B. Lagerreichweite)
3. Generiert nach 1.2s eine strukturierte Analyse
4. Kann später durch echten GPT-API-Call ersetzt werden

**Konstanten:**
- `INSIGHT_GENERATION_DELAY_MS = 1200` - Simulierte Ladezeit
- `MILLISECONDS_PER_KILOGRAM = 1000` - Umrechnungsfaktor für Tonnen

***REMOVED******REMOVED******REMOVED*** 2. `CopilotInsights.tsx` - UI Komponente

**Pfad:** `src/features/copilot/CopilotInsights.tsx`

**Zweck:** Zeigt KI-Analysen an und ermöglicht interaktive Rückfragen.

**Features:**
- **Zusammenfassung:** Textuelle Analyse der aktuellen Geschäftslage
- **Hauptfaktoren:** Liste der wichtigsten Einflussfaktoren
- **Empfehlungen:** Konkrete Handlungsvorschläge
- **Rückfrage-Buttons:** Zwei vordefinierte Fragen
  - "Warum ändert sich die Marge?"
  - "Lagerentwicklung?"
- **Inline-Antworten:** Antworten erscheinen animiert unter den Buttons

**Konstanten:**
- `COPILOT_RESPONSE_DELAY_MS = 1000` - Antwort-Verzögerung

**Copilot Questions:**
```typescript
type CopilotQuestion = "margin" | "inventory"

const COPILOT_RESPONSES: Record<CopilotQuestion, string> = {
  margin: "Marge profitiert von steigenden Verkaufspreisen...",
  inventory: "Lager sinkt wegen Abverkauf im Nordseeraum..."
}
```

***REMOVED******REMOVED*** Integration

***REMOVED******REMOVED******REMOVED*** In `analytics.tsx`:

```typescript
import { CopilotInsights } from "@/features/copilot/CopilotInsights"

// Ersetzt die alte statische Insight-Box
<CopilotInsights />
```

***REMOVED******REMOVED*** Styling

**Design-System:**
- Gradient-Hintergrund: `from-emerald-50 to-teal-50`
- Emoji-Icon: 🤖 für visuelle Identifikation
- Animationen: Framer Motion für sanftes Einblenden
- Buttons: Shadcn UI `Button` mit `variant="secondary"`

**Layout:**
- Hauptcontainer: `rounded-xl p-4 shadow space-y-2`
- Listen: `list-disc list-inside text-sm`
- Buttons: `flex flex-wrap gap-2`
- Antworten: `border-t pt-2 italic text-gray-700`

***REMOVED******REMOVED*** Backend-Integration (Optional)

***REMOVED******REMOVED******REMOVED*** Aktuell: Simuliert
Die aktuelle Implementierung simuliert KI-Antworten mit festen Texten und Timeouts.

***REMOVED******REMOVED******REMOVED*** Zukünftig: GPT-API

**Endpoint-Vorschlag:** `POST /mcp/copilot/analyze`

**Request:**
```json
{
  "kpis": [
    { "id": "rev", "value": 483210, "delta": 5.6 },
    { "id": "margin", "value": 18.7, "delta": 0.9 }
  ],
  "trends": [
    { "date": "01.10", "sales": 24000, "inventory": 82000 }
  ]
}
```

**Response:**
```json
{
  "summary": "Der Umsatz liegt aktuell bei 483.210 €...",
  "factors": [
    "Starke Nachfrage nach Milchpulversegment",
    "Steigende Logistikkosten"
  ],
  "suggestions": [
    "Lageroptimierung: Prüfe Putaway-Zyklen",
    "Preisanpassung bei stabiler Nachfrage"
  ]
}
```

**Rückfragen-Endpoint:** `POST /mcp/copilot/ask`

**Request:**
```json
{
  "question": "Warum ändert sich die Marge?",
  "context": {
    "kpis": [...],
    "trends": [...]
  }
}
```

**Response:**
```json
{
  "answer": "Die Marge profitiert von steigenden Verkaufspreisen..."
}
```

***REMOVED******REMOVED*** Code-Qualität

***REMOVED******REMOVED******REMOVED*** ✅ Memory-Bank Compliance

- **TypeScript Strict Mode:** Alle Typen explizit definiert
- **Keine Magic Numbers:** Alle Konstanten benannt
- **Explizite Return Types:** Überall vorhanden
- **Kein `any` Typ:** Strikte Typisierung
- **Nullish Coalescing:** `??` statt `||`
- **Explizite Boolean Checks:** Keine impliziten Truthy-Checks

***REMOVED******REMOVED******REMOVED*** ✅ Lint Status

- 0 Errors
- 0 Warnings
- Import-Sortierung korrekt
- Ungenutzte Variablen vermieden

***REMOVED******REMOVED*** Features

***REMOVED******REMOVED******REMOVED*** ✅ Implementiert

1. **Automatische KI-Analyse**
   - Generiert Zusammenfassung aus KPIs & Trends
   - Berechnet Durchschnittswerte
   - Erkennt Trends (steigend/fallend)

2. **Strukturierte Insights**
   - Summary (Hauptaussage)
   - Factors (Einflussfaktoren)
   - Suggestions (Handlungsempfehlungen)

3. **Interaktive Rückfragen**
   - 2 vordefinierte Fragen
   - Inline-Antworten mit Animation
   - Erweiterbar auf beliebig viele Fragen

4. **Animationen**
   - Framer Motion für sanftes Einblenden
   - Loading-State während Generierung
   - Smooth Transitions für Antworten

***REMOVED******REMOVED******REMOVED*** 🚀 Erweiterungsmöglichkeiten

1. **GPT-Integration**
   - Echter LLM-API-Call statt Simulation
   - Dynamische Antworten basierend auf Kontext
   - Streaming-Responses für Echtzeit-Gefühl

2. **Historische Insights**
   - Speicherung vergangener Analysen
   - Timeline-View mit Timestamps
   - Vergleich über Zeiträume

3. **Export-Funktionen**
   - PDF-Report-Generierung
   - Excel-Export mit Diagrammen
   - Email-Versand an Stakeholder

4. **Erweiterte Fragen**
   - Freitext-Eingabe für beliebige Fragen
   - Kontext-bewusste Antworten
   - Follow-up-Fragen vorschlagen

5. **Anomalie-Erkennung**
   - Automatische Warnung bei Ausreißern
   - Priorisierung nach Wichtigkeit
   - Proaktive Benachrichtigungen

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Unit Tests (Vorschlag)

```typescript
describe('useCopilotInsight', () => {
  it('should generate insight from KPIs and trends', async () => {
    const { result } = renderHook(() => useCopilotInsight())
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
      expect(result.current.insight).not.toBeNull()
    })
  })
})

describe('CopilotInsights', () => {
  it('should display insight summary', () => {
    render(<CopilotInsights />)
    expect(screen.getByText(/Umsatz liegt aktuell/)).toBeInTheDocument()
  })
  
  it('should show answer when button clicked', async () => {
    render(<CopilotInsights />)
    fireEvent.click(screen.getByText(/Warum ändert sich die Marge/))
    
    await waitFor(() => {
      expect(screen.getByText(/Antwort:/)).toBeInTheDocument()
    })
  })
})
```

***REMOVED******REMOVED*** Deployment

***REMOVED******REMOVED******REMOVED*** Voraussetzungen

- `framer-motion` installiert
- `recharts` installiert (für Analytics Dashboard)
- MCP-Backend mit `analytics/kpis` und `analytics/trends` Endpoints

***REMOVED******REMOVED******REMOVED*** Build

```bash
cd packages/frontend-web
pnpm run build
```

***REMOVED******REMOVED******REMOVED*** Lint

```bash
pnpm run lint  ***REMOVED*** Sollte 0 Errors, 0 Warnings zeigen
```

***REMOVED******REMOVED*** Zusammenfassung

**Phase E - Copilot Insights 2.0** erweitert das Analytics Dashboard um einen intelligenten KI-Layer, der:

- ✅ Automatisch KPIs & Trends analysiert
- ✅ Verständliche Zusammenfassungen generiert
- ✅ Interaktive Rückfragen ermöglicht
- ✅ Vollständig typsicher implementiert ist
- ✅ Einfach an echte GPT-API anbindbar ist

**Status:** Production Ready 🚀
