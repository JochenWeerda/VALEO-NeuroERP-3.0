import { inboxOpenHref, type InboxQueueItem } from '@/components/adaptive-workspace/inbox'
import type { RouteTarget } from '@/app/routing/typed-router'
import type { SpecializedComponentKind } from '@/studio/workspace-composition'
export { INBOX_SLOT } from './queue-contracts'

/**
 * Konsum der Dispo-Tafel. Ziel ist die spezialisierte Maske, nicht das Godfile.
 * `type`/`id` kommen aus dem Geschwister-Vertrag (nur gelesen).
 */
export const DISPOSITION_BOARD_SLOT = {
  kind: 'disposition_board' as const satisfies SpecializedComponentKind,
  id: 'lkw-disposition-board',
  route: '/disposition/touren-disposition',
  screenId: 'disposition/touren-disposition',
  label: 'LKW-Disposition',
}

/**
 * Oeffnet die bestehende Belegmaske. Prefill und Approve bleiben beim Widget/Server;
 * 409 auf approve wird hier nicht umgangen.
 */
export function openInboxItemInMask(
  item: InboxQueueItem,
  navigate: (to: RouteTarget) => void,
): void {
  const href = inboxOpenHref(item)
  if (!href) {
    return
  }
  navigate(href as RouteTarget)
}
