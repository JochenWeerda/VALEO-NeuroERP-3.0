/**
 * Abschluss-Checklist: Prozessmaske (Saldenvortrag), Detail bereits ueber
 * UniversalNativeDetailPage wenn Entity-ID gesetzt — Create bleibt Legacy-Workspace.
 */
import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'fibu/abschluss-checklist-detail',
  'fibu-abschluss-checklist-detail',
  () => import('./abschluss-checklist-detail-legacy'),
)
