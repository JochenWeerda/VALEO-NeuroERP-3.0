import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'verkauf/rechnungen/neu',
  'verkauf-rechnungen-neu',
  () => import('./sales/invoice-editor-legacy'),
)
