import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { ProcessBand } from '@/components/mask-builder/renderers/ProcessBand'
import { buildWorkflowState } from '@/components/mask-builder/runtime/WorkflowRuntime'
import { fetchFlowSpineWorkspace, type FlowSpineWorkspace } from '@/lib/api/flow-spines'
import type { WorkflowEntryContext } from './WorkflowEntryBanner'

/**
 * FSX-013 — Prozessband fuer Masken, die aus einem Flow-Spine-Vorgang heraus
 * geoeffnet werden.
 *
 * Ersetzt den `WorkflowEntryBanner`: aus einem Hinweiskasten mit vier
 * Merkmalschips und einem Absatz Erklaertext wird eine Zeile, die sagt, wo der
 * Vorgang steht und was als naechstes ansteht.
 *
 * Woher die Teile kommen — das ist die Regel aus FSX-030 und sie gilt hier
 * unveraendert:
 * - **Phasen und Aktionsbezeichnungen** stammen aus der Prozessbeschreibung
 *   (Flow-Spine-Knoten). Prozessdefinition, statisch zulaessig (FSX-003 Fall 1).
 * - **Der aktuelle Stand** stammt aus dem Vorgang: `node.status` wird
 *   serverseitig aus der Instanz ueberlagert. Ohne Instanz gibt es keinen Stand,
 *   und dann wird auch keiner angezeigt.
 *
 * Bewusst **kein** Blocker: die Knoten tragen heute keinen Sperrgrund, nur einen
 * Zustand. Aus "kritisch" einen Text zu erfinden waere genau die Sorte
 * Behauptung, die FSX-002 aus dem Leitstand entfernt hat.
 */
export function WorkflowProcessBand({
  context,
  className,
}: {
  context: WorkflowEntryContext
  className?: string
}): JSX.Element | null {
  const navigate = useNavigate()
  const [data, setData] = useState<FlowSpineWorkspace | null>(null)

  // Bewusst ohne react-query: dieser Baustein soll in beliebige Fachmasken
  // passen, und ein useQuery wuerde jeder von ihnen einen QueryClientProvider
  // aufzwingen — eine Abhaengigkeit, die beim Rollout ueber 18 Masken teuer
  // wird. Der Workspace-Endpunkt ist serverseitig 60 s HTTP-gecacht; ein
  // Abruf je Maskenaufruf ist vertretbar.
  useEffect(() => {
    let abgebrochen = false
    if (!context.process) {
      setData(null)
      return
    }
    void fetchFlowSpineWorkspace(context.process, context.instanceId || undefined)
      .then((workspace) => {
        if (!abgebrochen) setData(workspace)
      })
      .catch(() => {
        // Das Prozessband ist Orientierung, kein Arbeitsmittel: faellt der
        // Abruf aus, arbeitet die Maske ohne Band weiter. Ein Fehlerbanner
        // ueber einem funktionierenden Formular waere schlimmer als kein Band.
        if (!abgebrochen) setData(null)
      })
    return () => {
      abgebrochen = true
    }
  }, [context.process, context.instanceId])

  const { workflow, workflowState } = useMemo(() => {
    const nodes = data?.nodes ?? []
    const phases = nodes.map((node) => ({ key: node.id, label: node.label }))

    // Der laufende Knoten ist der Stand des Vorgangs. Ohne Instanz ueberlagert
    // das Backend nichts, dann bleibt der Stand unbekannt — und das Band zeigt
    // keine aktive Phase, statt auf die erste zu raten.
    const activeNode = context.instanceId
      ? (nodes.find((node) => node.status === 'active') ??
         nodes.find((node) => node.id === data?.focus_node_id) ??
         // Ein pausierter Vorgang hat keinen "active"-Knoten mehr. Ohne diesen
         // Rueckfall bliebe die Sperre unsichtbar — also genau im wichtigsten
         // Fall.
         nodes.find((node) => node.status === 'critical'))
      : undefined

    const primaryAction = activeNode?.actions?.find((action) => action.variant === 'primary')

    // F3 aus der Begehung, moeglich geworden durch FSX-001: Der Grund einer
    // Pause steht jetzt in den detail_rows des Knotens (aus dem juengsten
    // Ereignis). Vorher gab es keine Quelle und damit keinen Blocker.
    //
    // Gezeigt wird er nur, wenn der Vorgang tatsaechlich steht — die Sperre ist
    // eine Aussage des Lebenszyklus, nicht des Textes. Fehlt der Grund, wird er
    // als fehlend benannt statt erfunden: dass der Vorgang pausiert, ist ein
    // Fakt; warum, ist dann schlicht nicht hinterlegt.
    const lifecycle = data?.lifecycle_status
    const stehtStill = lifecycle === 'on_hold' || lifecycle === 'failed'
    const grundZeile = activeNode?.detail_rows?.find((row) =>
      ['Hinweis', 'Grund', 'Grundkategorie'].includes(row.label),
    )
    const blockingReasons = stehtStill
      ? [
          {
            code: lifecycle === 'failed' ? 'gescheitert' : 'pausiert',
            message:
              grundZeile?.value ||
              (lifecycle === 'failed'
                ? 'Gescheitert — Grund nicht hinterlegt'
                : 'Pausiert — Grund nicht hinterlegt'),
            blocking: true,
          },
        ]
      : []

    return {
      workflow: { processKey: context.process, phases },
      workflowState: buildWorkflowState(
        activeNode
          ? {
              status: {
                currentStatus: activeNode.id,
                statusLabel: activeNode.label,
                tone: activeNode.status === 'critical' ? 'danger' : 'neutral',
              },
              blockingReasons,
              nextAllowedActions: primaryAction
                ? [
                    {
                      actionKey: primaryAction.href,
                      label: primaryAction.label,
                      // Der Sprung in eine Maske aendert nichts; gefaehrlich wird
                      // erst, was dort ausgeloest wird.
                      dangerLevel: 'safe' as const,
                      requiresConfirmation: false,
                    },
                  ]
                : [],
            }
          : null,
      ),
    }
  }, [data, context.process, context.instanceId])

  if (workflow.phases.length === 0) return null

  return (
    <ProcessBand
      workflow={workflow}
      workflowState={workflowState}
      onAction={(href) => navigate(href)}
      onOpenProcess={() =>
        navigate(
          `/workflow/flow-spine-${context.process}${
            context.instanceId ? `?instanceId=${context.instanceId}` : ''
          }`,
        )
      }
      className={className}
    />
  )
}
