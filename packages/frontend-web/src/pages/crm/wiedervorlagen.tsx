import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Wiedervorlagen aus der ScreenDefinition `crm/wiedervorlagen`; Zeilen oeffnen die Kundenakte. */
export default function WiedervorlagenPage(): JSX.Element {
  return <NativeListPage screenId="crm/wiedervorlagen" testId="screen-crm/wiedervorlagen" />
}
