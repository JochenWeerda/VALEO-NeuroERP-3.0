import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'admin/command-monitor',
  'admin-command-monitor',
  () => import('./command-monitor-legacy'),
)
