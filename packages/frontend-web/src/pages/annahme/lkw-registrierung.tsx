import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'annahme/lkw-registrierung',
  'annahme-lkw-registrierung',
  () => import('./lkw-registrierung-legacy'),
)
