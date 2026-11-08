import { NativeListPage } from '@/components/mask-builder/NativeListPage'

const SCREEN_ID = 'sales/kreditlimit-pruefung'

export default function KreditlimitPruefungPage(): JSX.Element {
  return <NativeListPage screenId={SCREEN_ID} testId="sales-kreditlimit-pruefung" />
}
