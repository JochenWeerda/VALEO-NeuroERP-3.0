import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Betriebsprofile aus der ScreenDefinition `crm/betriebsprofile-liste`. */
export default function BetriebsprofileListePage(): JSX.Element {
  return <NativeListPage screenId="crm/betriebsprofile-liste" testId="screen-crm/betriebsprofile-liste" />
}
