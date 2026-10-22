import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'fibu/zahlungsmeldungen',
  'fibu-zahlungsmeldungen',
  () => import('./fibu/zahlungsmeldungen-legacy'),
)
