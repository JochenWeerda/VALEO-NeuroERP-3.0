import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

/**
 * Native Cockpit: ScreenDefinition admin-suite
 * Go-Live-Readiness + Evidenzliste + Nav-Kacheln — Parität zur Legacy-Home-Maske.
 */
export default function AdminSuiteHomePage(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId="admin-suite"
      testId="screen-admin-suite"
    />
  )
}
