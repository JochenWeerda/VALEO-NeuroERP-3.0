import * as React from "react"
import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { type Alert, decide } from "@/policy/engine"

type Props = {
  formData: Record<string, unknown>
  kpiId: string
  userRoles: Array<"admin" | "manager" | "operator">
}

/**
 * PolicyWarningBanner - Zeigt Policy-Warnungen inline in Formularen
 *
 * Beispiel: "Preis < EK → Freigabe nötig"
 */
export function PolicyWarningBanner({
  formData,
  kpiId,
  userRoles,
}: Props): JSX.Element | null {
  const [warning, setWarning] = useState<string | null>(null)
  const [severity, setSeverity] = useState<"warn" | "crit" | null>(null)

  useEffect(() => {
    // Policy-Check durchführen
    void checkPolicy()
  }, [formData])

  async function checkPolicy(): Promise<void> {
    try {
      // Beispiel: Marge-Check
      const lines = formData.lines as Array<{
        qty: number
        price: number
      }> | undefined

      if (lines === undefined || lines.length === 0) {
        setWarning(null)
        return
      }

      // Berechne Gesamtsumme
      const total = lines.reduce((sum, line) => sum + line.qty * line.price, 0)

      // Beispiel-Regel: Warnung bei Summe < 100
      if (total < 100) {
        setWarning("⚠️ Auftragswert unter Minimum (100 €)")
        setSeverity("warn")
        return
      }

      // Beispiel-Regel: Kritisch bei Summe < 50
      if (total < 50) {
        setWarning("🚨 Auftragswert kritisch niedrig - Freigabe erforderlich")
        setSeverity("crit")
        return
      }

      // Policy-Engine-Check (optional)
      const alert: Alert = {
        id: "form-check",
        kpiId,
        title: "Formular-Validierung",
        message: `Auftragswert: ${total.toFixed(2)} €`,
        severity: total < 50 ? "crit" : total < 100 ? "warn" : "ok",
      }

      const decision = decide(userRoles, alert)

      if (decision.type === "deny") {
        setWarning(`🚫 Policy: ${decision.reason}`)
        setSeverity("crit")
        return
      }

      if (decision.needsApproval === true && decision.execute === false) {
        setWarning("🔐 Freigabe durch Manager/Admin erforderlich")
        setSeverity("warn")
        return
      }

      setWarning(null)
      setSeverity(null)
    } catch {
      // Silent fail
      setWarning(null)
    }
  }

  if (warning === null) {
    return null
  }

  const bgColor =
    severity === "crit"
      ? "bg-red-50 border-red-300 text-red-800"
      : "bg-amber-50 border-amber-300 text-amber-800"

  return (
    <Card className={`p-3 border ${bgColor}`}>
      <div className="text-sm font-medium">{warning}</div>
    </Card>
  )
}

