import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'einkauf/auftragsbestaetigung',
  'einkauf-auftragsbestaetigung',
  () => import('./auftragsbestaetigung-legacy'),
)
