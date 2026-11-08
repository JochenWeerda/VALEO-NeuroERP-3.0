import { useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

/** Antwort eines Kommando-Endpunkts im Maskenformat (``run_delegated_mask_action``). */
export type MaskCommandResult = { success: boolean; summary?: string | null; error?: string | null }

type Row = Record<string, unknown>

export interface MaskRowCommandOptions {
  /** Query-Schluessel der Maske; wird nach jeder erfolgreichen Aktion neu geladen. */
  screenId: string
  /** Aktionen mit Kommando-Endpunkt: Schluessel -> Pfad je Zeile. Dieselben Wege rufen CLI und MCP. */
  commands: Record<string, (row: Row) => string>
  /** Reine Navigation (``localEffect: navigation``): Schluessel -> Zielroute je Zeile. */
  navigation?: Record<string, (row: Row) => unknown>
  /** Reine Oberflaechenwirkung ohne Server (``localEffect: print`` u. a.). */
  local?: Record<string, (row: Row) => void>
  /** Zusaetzliche Nutzdaten je Aktion (ohne Umschlagfelder); ``null`` bricht die Aktion ab. */
  payload?: (actionKey: string, row: Row) => Record<string, unknown> | null | undefined
  /** Frage nach der Begruendung; ``false`` = Aktion ohne Pflichtbegruendung. */
  reasonPrompt?: string | false
  /** Kennung der Zeile fuer den Doppelausfuehrungsschutz. */
  rowKey?: (row: Row) => string
  successTitle?: string
}

/**
 * Zeilenaktionen einer Cockpit-Maske ueber ihre Kommando-Endpunkte (MASK-COMMANDS-ROLLOUT).
 *
 * Die Seite fragt nur die Begruendung ab; Bearbeiter, Zustand, Audit und Wiederholungsschutz prueft der
 * Endpunkt. Eine fachliche Ablehnung kommt mit HTTP 200 und ``success=false`` und ist kein Erfolg. Je Zeile
 * und Aktion laeuft hoechstens ein Auftrag (Per-Entity Pending State); andere Zeilen bleiben bedienbar.
 */
export function useMaskRowCommands(options: MaskRowCommandOptions): (actionKey: string, row: Row) => Promise<void> {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const pending = useRef(new Set<string>())

  return async function handleAction(actionKey: string, row: Row): Promise<void> {
    const target = options.navigation?.[actionKey]
    if (target) {
      const route = String(target(row) ?? '')
      if (route.startsWith('/')) window.location.assign(route)
      return
    }
    const local = options.local?.[actionKey]
    if (local) {
      local(row)
      return
    }
    const command = options.commands[actionKey]
    if (!command) return
    const id = options.rowKey ? options.rowKey(row) : String(row.id ?? '')
    if (!id) return
    const key = `${id}:${actionKey}`
    if (pending.current.has(key)) return
    const extra = options.payload?.(actionKey, row)
    if (extra === null) return
    let reason: string | undefined
    if (options.reasonPrompt !== false) {
      reason = window.prompt(options.reasonPrompt ?? 'Grund fuer die Bearbeitung (Audit):')?.trim()
      if (!reason || reason.length < 5) return
    }
    pending.current.add(key)
    try {
      const { data } = await apiClient.post<MaskCommandResult>(command(row), {
        ...(extra ?? {}),
        ...(reason ? { _auditReason: reason } : {}),
        _idempotencyKey: crypto.randomUUID(),
      })
      if (!data?.success) throw new Error(data?.error ?? 'Die Aktion wurde abgelehnt.')
      await queryClient.invalidateQueries({ queryKey: [options.screenId] })
      toast({ title: options.successTitle ?? 'Aktion ausgefuehrt', description: data.summary ?? undefined })
    } catch (error) {
      toast({
        title: 'Aktion fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } finally {
      pending.current.delete(key)
    }
  }
}

/** Pfadbaustein: Kennung sicher kodiert. */
export const seg = (value: unknown): string => encodeURIComponent(String(value ?? ''))
