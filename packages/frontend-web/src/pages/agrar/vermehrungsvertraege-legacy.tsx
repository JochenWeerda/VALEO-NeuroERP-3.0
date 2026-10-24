import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Listenmaske `agrar/vermehrungsvertraege-liste` (StammListenParent). */
export default function Page(): JSX.Element {
  return (
    <NativeListPage
      screenId="agrar/vermehrungsvertraege-liste"
      testId="screen-agrar/vermehrungsvertraege-liste"
    />
  )
}
