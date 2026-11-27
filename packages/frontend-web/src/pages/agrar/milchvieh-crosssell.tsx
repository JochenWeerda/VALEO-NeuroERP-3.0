import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

/**
 * Native Cockpit: ScreenDefinition agrar/milchvieh-crosssell
 * KPIs + Kundenliste + Produktgruppen — Parität zur Legacy-Auswertungsmaske.
 */
export default function MilchviehCrossSellPage(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId="agrar/milchvieh-crosssell"
      testId="screen-agrar/milchvieh-crosssell"
    />
  )
}
