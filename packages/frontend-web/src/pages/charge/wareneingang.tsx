import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Wareneingang Chargen aus der ScreenDefinition `charge/wareneingang-liste`. */
export default function ChargeWareneingangTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="charge/wareneingang-liste" testId="screen-charge/wareneingang-liste" />
  )
}
