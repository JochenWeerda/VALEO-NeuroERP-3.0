import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'annahme/qualitaets-check',
  'annahme-qualitaets-check',
  () => import('./qualitaets-check-legacy'),
)
