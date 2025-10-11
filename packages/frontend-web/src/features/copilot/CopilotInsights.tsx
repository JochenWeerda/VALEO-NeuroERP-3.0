import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { useCopilotInsight } from "./useCopilotInsight"

const COPILOT_RESPONSE_DELAY_MS = 1000

type CopilotQuestion = "margin" | "inventory"

const COPILOT_RESPONSES: Record<CopilotQuestion, string> = {
  margin: "Marge profitiert von steigenden Verkaufspreisen und optimierten Einkaufskonditionen.",
  inventory: "Lager sinkt wegen Abverkauf im Nordseeraum und erhöhter Nachfrage aus Skandinavien.",
}

export function CopilotInsights(): JSX.Element {
  const { insight, loading } = useCopilotInsight()
  const [response, setResponse] = useState<string | null>(null)

  const askCopilot = (question: CopilotQuestion): void => {
    setResponse("⏳ Analysiere …")
    // → hier GPT-Query oder MCP-Call einsetzen
    setTimeout((): void => {
      setResponse(`Antwort: ${COPILOT_RESPONSES[question]}`)
    }, COPILOT_RESPONSE_DELAY_MS)
  }

  if (loading || insight === null) {
    return (
      <div className="border rounded-xl p-4 bg-gradient-to-r from-gray-50 to-emerald-50">
        🤖 KI lädt …
      </div>
    )
  }

  return (
    <motion.div
      className="border rounded-xl p-4 bg-gradient-to-r from-emerald-50 to-teal-50 shadow space-y-2"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="font-semibold text-emerald-700">🤖 Copilot-Analyse</div>
      <p className="text-sm text-gray-800">{insight.summary}</p>

      <div className="mt-2">
        <div className="text-xs uppercase opacity-70">Hauptfaktoren</div>
        <ul className="list-disc list-inside text-sm">
          {insight.factors.map((factor, index): JSX.Element => (
            <li key={index}>{factor}</li>
          ))}
        </ul>
      </div>

      <div className="mt-2">
        <div className="text-xs uppercase opacity-70">Empfehlungen</div>
        <ul className="list-disc list-inside text-sm">
          {insight.suggestions.map((suggestion, index): JSX.Element => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>

      <div className="flex flex-wrap gap-2 pt-2">
        <Button
          size="sm"
          variant="secondary"
          onClick={(): void => {
            askCopilot("margin")
          }}
        >
          Warum ändert sich die Marge?
        </Button>
        <Button
          size="sm"
          variant="secondary"
          onClick={(): void => {
            askCopilot("inventory")
          }}
        >
          Lagerentwicklung?
        </Button>
      </div>

      {response !== null && (
        <motion.div
          className="mt-3 text-sm border-t pt-2 italic text-gray-700"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {response}
        </motion.div>
      )}
    </motion.div>
  )
}
