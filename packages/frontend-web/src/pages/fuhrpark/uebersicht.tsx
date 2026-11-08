import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Listenmaske `fuhrpark/fahrzeuge-liste` (StammListenParent). */
export default function Page(): JSX.Element {
  return (
    <NativeListPage
      screenId="fuhrpark/fahrzeuge-liste"
      testId="screen-fuhrpark/fahrzeuge-liste"
    />
  )
}
