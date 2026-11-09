import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

/** Anfrage-Erfassung: dieselbe Studio-Maske wie "Anfrage erstellen" (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId="einkauf/anfrage-erstellen"
      testId="einkauf-anfrage-erfassung"
      permissions={['procurement.read']}
    />
  )
}
