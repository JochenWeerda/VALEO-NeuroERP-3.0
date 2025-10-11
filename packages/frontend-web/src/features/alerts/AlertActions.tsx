import { useState } from "react"
import type { Alert } from "./rules"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { useAlertActions } from "./actions"
import { useToast } from "@/components/ui/toast-provider"
import { decide, updateCounters } from "@/policy/engine"
import { audit } from "@/policy/audit"

const PRICE_DELTA_CRITICAL = 3
const PRICE_DELTA_WARNING = 1
const REORDER_QTY_CRITICAL = 500
const REORDER_QTY_WARNING = 250

type ActionKind = "price" | "reorder" | "notify"

type ActionButton = {
  key: ActionKind
  label: string
}

type ActionConfig = {
  title: string
  description: string
}

type Props = {
  alert: Alert
}

/**
 * Alert-Actions Komponente mit Policy-Integration
 * Zeigt kontextabhängige Action-Buttons mit Confirm-Dialogs
 */
export function AlertActions({ alert }: Props): JSX.Element {
  const { priceAdjust, reorder, notifySales } = useAlertActions()
  const { push } = useToast()
  const [open, setOpen] = useState<boolean>(false)
  const [pending, setPending] = useState<ActionKind | null>(null)

  // TODO: Aus Auth-Context ziehen
  const userRoles: Array<"admin" | "manager" | "operator"> = ["manager"]

  // Vordefinierte Vorschläge (konservativ)
  const priceDelta =
    alert.severity === "crit" ? PRICE_DELTA_CRITICAL : PRICE_DELTA_WARNING
  const reorderQty =
    alert.severity === "crit" ? REORDER_QTY_CRITICAL : REORDER_QTY_WARNING

  /**
   * Gibt Titel und Beschreibung für Action-Dialog zurück
   */
  function getActionConfig(kind: ActionKind): ActionConfig {
    if (kind === "price") {
      return {
        title: "Preis anpassen",
        description: `Preis um +${priceDelta}% anheben?`,
      }
    }
    if (kind === "reorder") {
      return {
        title: "Nachbestellen",
        description: `Nachbestellung über ${reorderQty} Einheiten auslösen?`,
      }
    }
    return {
      title: "Vertrieb informieren",
      description: "Hinweis an den Vertrieb senden?",
    }
  }

  /**
   * Führt die gewählte Action mit Policy-Check aus
   */
  async function executeAction(kind: ActionKind): Promise<void> {
    setPending(kind)

    // Policy-Check
    const decision = decide(userRoles, alert)

    if (decision.type === "deny") {
      push(`🚫 Policy: ${decision.reason}`)
      setPending(null)
      setOpen(false)
      return
    }

    // Approval-Check
    if (decision.needsApproval && !decision.execute) {
      push("📝 Freigabe angefordert – wartet auf Genehmigung.")
      
      // Audit-Log
      void audit({
        ts: new Date().toISOString(),
        user: "current-user", // TODO: Aus Auth
        roles: userRoles,
        action: kind === "price" ? "pricing.adjust" : kind === "reorder" ? "inventory.reorder" : "sales.notify",
        params: decision.resolvedParams,
        ruleId: decision.ruleId,
        result: "requested-approval",
      })

      setPending(null)
      setOpen(false)
      return
    }

    // Parameter aus Policy oder Fallback
    const params = decision.resolvedParams
    const finalDeltaPct = (params.deltaPct as number | undefined) ?? priceDelta
    const finalQty = (params.qty as number | undefined) ?? reorderQty
    const finalTopic = (params.topic as string | undefined) ?? alert.title
    const finalMessage = (params.messageTemplate as string | undefined) ?? alert.message

    try {
      if (kind === "price") {
        await priceAdjust.mutateAsync({ deltaPct: finalDeltaPct })
        push("✔ Preisupdate angestoßen")
        updateCounters(decision.ruleId, { deltaPct: finalDeltaPct })
      } else if (kind === "reorder") {
        await reorder.mutateAsync({ qty: finalQty })
        push("✔ Nachbestellung gestartet")
        updateCounters(decision.ruleId, { qty: finalQty })
      } else {
        await notifySales.mutateAsync({
          topic: finalTopic,
          message: finalMessage,
        })
        push("✔ Vertrieb benachrichtigt")
      }

      // Audit-Log
      void audit({
        ts: new Date().toISOString(),
        user: "current-user", // TODO: Aus Auth
        roles: userRoles,
        action: kind === "price" ? "pricing.adjust" : kind === "reorder" ? "inventory.reorder" : "sales.notify",
        params: { deltaPct: finalDeltaPct, qty: finalQty, topic: finalTopic, message: finalMessage },
        ruleId: decision.ruleId,
        result: "executed",
      })
    } catch {
      push("❌ Aktion fehlgeschlagen")

      // Audit-Log für Fehler
      void audit({
        ts: new Date().toISOString(),
        user: "current-user",
        roles: userRoles,
        action: kind === "price" ? "pricing.adjust" : kind === "reorder" ? "inventory.reorder" : "sales.notify",
        params: decision.resolvedParams,
        ruleId: decision.ruleId,
        result: "denied",
        reason: "Execution failed",
      })
    } finally {
      setPending(null)
      setOpen(false)
    }
  }

  /**
   * Bestimmt verfügbare Buttons basierend auf KPI-ID
   */
  function getAvailableButtons(): ActionButton[] {
    const buttons: ActionButton[] = []

    if (alert.kpiId === "margin") {
      buttons.push({ key: "price", label: `Preis +${priceDelta}%` })
    }
    if (alert.kpiId === "stock") {
      buttons.push({ key: "reorder", label: `Nachbestellen ${reorderQty}` })
    }
    if (alert.kpiId === "rev") {
      buttons.push({ key: "notify", label: "Vertrieb informieren" })
    }

    // Fallback: immer mindestens „Vertrieb informieren"
    if (buttons.length === 0) {
      buttons.push({ key: "notify", label: "Vertrieb informieren" })
    }

    return buttons
  }

  const buttons = getAvailableButtons()
  const isAnyPending =
    priceAdjust.isPending || reorder.isPending || notifySales.isPending

  return (
    <div className="flex flex-wrap gap-2">
      {buttons.map((button): JSX.Element => {
        const config = getActionConfig(button.key)
        const isThisPending = pending === button.key

        return (
          <AlertDialog
            key={button.key}
            open={open && isThisPending}
            onOpenChange={setOpen}
          >
            <AlertDialogTrigger asChild>
              <Button
                size="sm"
                variant="secondary"
                onClick={(): void => {
                  setPending(button.key)
                  setOpen(true)
                }}
              >
                {button.label}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>{config.title}</AlertDialogTitle>
                <AlertDialogDescription>
                  {config.description}
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Abbrechen</AlertDialogCancel>
                <AlertDialogAction
                  onClick={(): void => {
                    void executeAction(button.key)
                  }}
                  disabled={isAnyPending}
                >
                  Bestätigen
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )
      })}
    </div>
  )
}
