import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

/**
 * Native Cockpit: ScreenDefinition admin/command-monitor
 * Idempotenz-KPIs + Commands/Aggregate/Lookup-Pfade — Parität zur Legacy-Maske.
 */
export default function CommandMonitorPage(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId="admin/command-monitor"
      testId="screen-admin/command-monitor"
    />
  )
}
