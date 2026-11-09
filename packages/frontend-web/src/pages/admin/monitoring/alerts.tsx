import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Monitoring-Alarme: Studio-Liste `admin/monitoring/alerting` (gleicher Leseweg wie die frühere Seite). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="admin/monitoring/alerting" testId="screen-admin-monitoring-alerts" />
}
