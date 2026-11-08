import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Offene Debitorenposten aus der kanonischen ScreenDefinition. */
export default function DebitorenPage(): JSX.Element {
  return <NativeListPage screenId="fibu/debitoren-liste" testId="screen-fibu/debitoren-liste" />
}
