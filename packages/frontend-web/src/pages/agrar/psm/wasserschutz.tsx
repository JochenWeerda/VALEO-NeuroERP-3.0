import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Wasserschutz aus der ScreenDefinition `agrar/psm-wasserschutz-liste`. */
export default function AgrarPsmWasserschutzTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/psm-wasserschutz-liste" testId="screen-agrar/psm-wasserschutz-liste" />
  )
}
