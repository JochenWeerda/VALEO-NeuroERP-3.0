import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Debitoren OP aus der ScreenDefinition `fibu/debitoren-liste`. */
export default function FibuDebitorenTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/debitoren-liste" testId="screen-fibu/debitoren-liste" />
  )
}
