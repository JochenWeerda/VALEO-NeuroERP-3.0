import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Verkaufsangebote aus der ScreenDefinition `sales/angebote-liste`. */
export default function AngeboteListePage(): JSX.Element {
  return <NativeListPage screenId="sales/angebote-liste" testId="screen-sales/angebote-liste" />
}
